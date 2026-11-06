"""Apply an album manifest written by tools/imagekit_uploader.py.

The manifest describes one album folder and the images already uploaded to
ImageKit. Album membership in fotoweb is by path (Album.get_images matches
Image.path against Album.path), so an image is only ever updated when its
stored path is inside this album; an image with the same name elsewhere is
reported as a conflict and left alone.
"""
from datetime import datetime
import os

from django.db import IntegrityError, transaction
from django.utils.text import slugify

from .models import Album, Image


class ManifestError(ValueError):
    pass


def _clean(value, max_length=None):
    """Strip NUL bytes (Postgres refuses them) and surrounding blanks."""
    if value is None:
        return None
    value = str(value).replace('\x00', '').strip()
    if max_length:
        value = value[:max_length]
    return value or None


def _parse_dt(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        return None


def validate(manifest):
    if not isinstance(manifest, dict) or manifest.get('version') != 1:
        raise ManifestError('expected a manifest with "version": 1')
    album = manifest.get('album')
    if not isinstance(album, dict):
        raise ManifestError('missing "album"')
    path = album.get('path')
    if not isinstance(path, str) or not path.startswith('/') or path.endswith('/'):
        raise ManifestError('album.path must start and not end with "/"')
    if album.get('domain') not in Album.Domains.values:
        raise ManifestError(f'album.domain must be one of {Album.Domains.values}')
    images = manifest.get('images')
    if not isinstance(images, list):
        raise ManifestError('missing "images"')
    for img in images:
        if not isinstance(img, dict):
            raise ManifestError('every image must be an object')
        name, ipath, url = img.get('name'), img.get('path'), img.get('url')
        if not (isinstance(name, str) and isinstance(ipath, str) and isinstance(url, str)):
            raise ManifestError(f'image needs name, path and url: {img!r:.200}')
        if not ipath.startswith(path + '/') or os.path.basename(ipath) != name:
            raise ManifestError(f'{name}: path {ipath} is not a file of the album')
        if len(name) > 100 or len(ipath) > 200 or len(url) > 200:
            raise ManifestError(f'{name}: name, path or url too long')


def ingest(manifest, dry_run=False):
    """Create or update the album and its images. Returns a report dict."""
    validate(manifest)
    a = manifest['album']
    apath, domain = a['path'], a['domain']
    title = _clean(a.get('title'), 100) or apath.rsplit('/', 1)[-1][:100]

    report = {'dry_run': dry_run, 'album': None, 'created': [], 'updated': [],
              'unchanged': [], 'conflicts': [], 'errors': [], 'warnings': []}

    with transaction.atomic():
        album = Album.objects.filter(path=apath).first()
        if album is None:
            # Old albums use other path styles (/C1/foto/..., /2024/d:/...):
            # don't create a duplicate of one of them.
            same = Album.objects.filter(title=title, domain=domain).first()
            if same:
                raise ManifestError(
                    f'album "{title}" already exists as {same.id} with path {same.path}')
            slug = slugify(apath)
            if Album.objects.filter(slug=slug).exists():
                raise ManifestError(f'album slug {slug} already in use')
            album = Album(path=apath, title=title, slug=slug, domain=domain)
            album.save()
            report['album'] = {'id': album.id, 'slug': album.slug, 'created': True}
        else:
            report['album'] = {'id': album.id, 'slug': album.slug, 'created': False}
            if album.domain != domain:
                report['warnings'].append(
                    f'album domain is {album.domain}, manifest says {domain}; kept {album.domain}')

        first = None
        for img in sorted(manifest['images'], key=lambda i: i['name']):
            try:
                with transaction.atomic():
                    result, image = _ingest_image(img, apath, album.domain)
            except IntegrityError as e:
                report['errors'].append({'name': img['name'], 'error': str(e).splitlines()[0]})
                continue
            if result == 'conflicts':
                report['conflicts'].append(image)
                continue
            report[result].append(img['name'])
            if first is None:
                first = image

        if not album.cover and first is not None:
            album.cover = first.url
            if first.created_dt:
                album.taken_dt = first.created_dt.date()
            album.save()  # also re-sets the domain of the album's images

        if dry_run:
            transaction.set_rollback(True)

    return report


def _ingest_image(img, apath, domain):
    name, path, url = img['name'], img['path'], img['url']
    taken = _parse_dt(img.get('taken_dt'))
    keywords = [k for k in (_clean(k) for k in img.get('keywords') or []) if k]
    meta = {
        'title': _clean(img.get('title'), 200),
        'description': _clean(img.get('description')),
        'tags': ','.join(keywords) or None,
    }

    image = Image.objects.filter(name=name).first()
    if image is None:
        image = Image(name=name, path=path, url=url, path_fs=path, url_fs=url,
                      domain=domain, private=True, **meta)
        image.save()
        if taken:  # created_dt is auto_now_add, so set it after the insert
            Image.objects.filter(pk=image.pk).update(created_dt=taken)
            image.created_dt = taken
        return 'created', image

    if not (image.path or '').startswith(apath + '/'):
        return 'conflicts', {'name': name, 'id': image.id,
                             'stored_path': image.path, 'new_path': path}

    changed = False
    for field, value in [('path_fs', path), ('url_fs', url)]:
        if getattr(image, field) != value:
            setattr(image, field, value)
            changed = True
    # path/url may hold an older 2048 web copy: only fill them when empty.
    for field, value in [('path', path), ('url', url), *meta.items()]:
        if value and not getattr(image, field):
            setattr(image, field, value)
            changed = True
    if changed:
        image.save()
    if taken and image.created_dt != taken:
        Image.objects.filter(pk=image.pk).update(created_dt=taken)
        image.created_dt = taken
        changed = True
    return ('updated' if changed else 'unchanged'), image
