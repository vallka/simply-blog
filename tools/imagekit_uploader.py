# /// script
# requires-python = ">=3.12"
# dependencies = ["requests", "pillow"]
# ///
"""Upload one album folder of JPEGs to ImageKit and describe it in a JSON
manifest, optionally pushing the manifest to vallka.com (/photo/api/ingest/).

    uv run tools/imagekit_uploader.py "D:/FOTO/Lucas/2025/25-11 Corbera,  Denia"
    uv run tools/imagekit_uploader.py DIR --push --dry-run   # server reports only
    uv run tools/imagekit_uploader.py DIR --push

Folder rules: the JPEGs are on the top level of DIR. Exception for old
exports: if DIR has no top-level JPEGs and its only photo subfolders are
JPEG-Full-size (+ optionally JPEG-2048*), JPEG-Full-size is used and the
2048 copy ignored. Photo subfolders in any other case are warned about and
skipped.

The manifest is written to DIR/_vallka.json and doubles as an upload cache:
a file with the same size and mtime as last time is not uploaded again.

Config (TOML, default %APPDATA%/vallka/uploader.toml, or --config):

    [imagekit]          # the current account; replace when it is full
    private_key = "private_..."
    url_endpoint = "https://ik.imagekit.io/k8d1n4xgq"

    [site]
    url = "https://www.vallka.com"
    token = "..."       # INGEST_TOKEN in the server .env

    [domains]           # album root -> fotoweb domain (1 vallka, 2 Lucas)
    "D:/FOTO/vallka" = 1
    "D:/FOTO/Lucas" = 2
"""
import argparse
import json
import os
import re
import sys
import tomllib
from datetime import datetime, timezone
from pathlib import Path

import requests
from PIL import Image, IptcImagePlugin

UPLOAD_URL = 'https://upload.imagekit.io/api/v1/files/upload'
LIST_URL = 'https://api.imagekit.io/v1/files'
MANIFEST = '_vallka.json'
FULL_SIZE = 'JPEG-Full-size'
JPEG_EXT = {'.jpg', '.jpeg'}


def warn(msg):
    print(f'WARNING: {msg}', file=sys.stderr)


def default_config():
    base = os.environ.get('APPDATA') or os.path.expanduser('~/.config')
    return Path(base) / 'vallka' / 'uploader.toml'


def jpegs(folder):
    return sorted((p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in JPEG_EXT),
                  key=lambda p: p.name)


def find_photo_folder(album_dir):
    """Return the folder whose JPEGs make up the album (see module doc)."""
    top = jpegs(album_dir)
    photo_subdirs = [d for d in sorted(album_dir.iterdir()) if d.is_dir() and jpegs(d)]
    names = {d.name for d in photo_subdirs}
    if not top and FULL_SIZE in names and all(
            n == FULL_SIZE or n.startswith('JPEG-2048') for n in names):
        return album_dir / FULL_SIZE
    for d in photo_subdirs:
        warn(f'subfolder with photos ignored: {d.name}')
    return album_dir


def site_path(p):
    """D:\\FOTO\\x -> /d:/FOTO/x, the path style fotoweb stores."""
    s = str(p.resolve()).replace('\\', '/')
    if re.match(r'^[A-Za-z]:/', s):
        s = s[0].lower() + s[1:]
    return '/' + s.lstrip('/')


def imagekit_folder(path):
    # same rule as scan_pp, so URLs keep their shape
    return re.sub(r'[^/_0-9A-Za-z\-.]', '_', path)


def find_domain(album_dir, domains, override):
    if override:
        return override
    a = site_path(album_dir).lower() + '/'
    for root, domain in domains.items():
        if a.startswith(site_path(Path(root)).lower() + '/'):
            return int(domain)
    sys.exit(f'{album_dir} is under no [domains] root in the config; use --domain')


def _text(v):
    if v is None:
        return None
    if isinstance(v, list):
        v = v[0] if v else b''
    if isinstance(v, bytes):
        try:
            s = v.decode('utf-8')
        except UnicodeDecodeError:  # IPTC without the UTF-8 charset marker
            s = v.decode('cp1252', errors='replace')
    else:
        s = str(v)
    s = s.replace('\x00', '').strip()
    return s or None


def read_metadata(file):
    """Size, EXIF date/camera and IPTC title/caption/keywords."""
    with Image.open(file) as im:
        width, height = im.size
        exif = im.getexif()
        sub = exif.get_ifd(0x8769)  # Exif IFD
        iptc = IptcImagePlugin.getiptcinfo(im) or {}

    meta = {'width': width, 'height': height}

    dto = sub.get(36867) or exif.get(306)  # DateTimeOriginal, DateTime
    if dto:
        try:
            # EXIF has local time without zone; scan_pp stored it as UTC.
            dt = datetime.strptime(str(dto).strip().replace('\x00', ''), '%Y:%m:%d %H:%M:%S')
            meta['taken_dt'] = dt.isoformat() + 'Z'
        except ValueError:
            warn(f'{file.name}: unreadable EXIF date {dto!r}')

    camera = {
        'make': _text(exif.get(271)), 'model': _text(exif.get(272)),
        'lens': _text(sub.get(42036)),
        'focal_length': sub.get(37386), 'f_number': sub.get(33437),
        'exposure_time': sub.get(33434), 'iso': sub.get(34855),
    }
    camera = {k: (float(v) if k in ('focal_length', 'f_number', 'exposure_time') else v)
              for k, v in camera.items() if v is not None}
    if camera:
        meta['camera'] = camera

    meta['title'] = _text(iptc.get((2, 105))) or _text(iptc.get((2, 5)))  # headline, object name
    meta['description'] = _text(iptc.get((2, 120)))  # caption/abstract
    kw = iptc.get((2, 25)) or []
    if not isinstance(kw, list):
        kw = [kw]
    meta['keywords'] = [k for k in (_text(k) for k in kw) if k]
    return meta


class ImageKit:
    def __init__(self, cfg):
        self.auth = (cfg['private_key'], '')
        self.endpoint = cfg['url_endpoint'].rstrip('/')
        self._listed = {}

    def existing(self, folder):
        """{name: file} of what is already in an ImageKit folder."""
        if folder not in self._listed:
            files, skip = {}, 0
            while True:
                r = requests.get(LIST_URL, auth=self.auth, timeout=60, params={
                    'path': folder, 'type': 'file', 'limit': 1000, 'skip': skip})
                r.raise_for_status()
                batch = r.json()
                files.update({f['name']: f for f in batch if f.get('filePath', '').rsplit('/', 1)[0] == folder})
                if len(batch) < 1000:
                    break
                skip += 1000
            self._listed[folder] = files
        return self._listed[folder]

    def upload(self, file, folder):
        with open(file, 'rb') as fh:
            r = requests.post(UPLOAD_URL, auth=self.auth, timeout=600,
                              files={'file': (file.name, fh, 'image/jpeg')},
                              data={'fileName': file.name, 'folder': folder,
                                    'useUniqueFileName': 'false', 'overwriteFile': 'true'})
        if r.status_code >= 400:
            sys.exit(f'{file.name}: ImageKit upload failed {r.status_code}: {r.text[:500]}')
        return r.json()['url'].split('?', 1)[0]


def build(album_dir, cfg, args):
    photo_dir = find_photo_folder(album_dir)
    files = jpegs(photo_dir)
    if not files:
        sys.exit(f'no JPEGs in {photo_dir}')

    album_path = site_path(album_dir)
    domain = find_domain(album_dir, cfg.get('domains', {}), args.domain)
    folder = imagekit_folder(site_path(photo_dir))
    ik = ImageKit(cfg['imagekit'])

    manifest_file = album_dir / MANIFEST
    cache = {}
    if manifest_file.exists() and not args.force:
        old = json.loads(manifest_file.read_text(encoding='utf-8'))
        cache = {i['name']: i for i in old.get('images', [])}

    print(f'album  {album_path}  (domain {domain})')
    print(f'files  {len(files)} in {photo_dir}')
    print(f'imagekit {ik.endpoint}{folder}')

    images, uploaded, kept = [], 0, 0
    for n, file in enumerate(files, 1):
        st = file.stat()
        mtime = datetime.fromtimestamp(st.st_mtime, timezone.utc).isoformat().replace('+00:00', 'Z')
        path = site_path(file)
        c = cache.get(file.name)
        if c and c.get('size') == st.st_size and c.get('mtime') == mtime and c.get('path') == path:
            url = c['url']
            kept += 1
        else:
            url = None
            if not args.force:
                remote = ik.existing(folder).get(file.name)
                if (remote and remote.get('size') == st.st_size
                        and datetime.fromisoformat(remote['updatedAt'].replace('Z', '+00:00')).timestamp() >= st.st_mtime):
                    url = remote['url'].split('?', 1)[0]  # list adds ?updatedAt=
                    kept += 1
            if url is None:
                if args.no_upload:
                    warn(f'{file.name}: not on ImageKit, skipped (--no-upload)')
                    continue
                print(f'  [{n}/{len(files)}] upload {file.name}')
                url = ik.upload(file, folder)
                uploaded += 1
        images.append({'name': file.name, 'path': path, 'url': url,
                       'size': st.st_size, 'mtime': mtime, **read_metadata(file)})

    if not images:
        sys.exit('nothing to describe; manifest not written')
    names = [i['name'] for i in images]
    if len(set(n.lower() for n in names)) != len(names):
        warn('file names differ only by case; the site treats names as unique')

    manifest = {
        'version': 1,
        'generated': datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z'),
        'album': {'path': album_path, 'title': album_dir.name, 'domain': domain},
        'images': images,
    }
    manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'uploaded {uploaded}, already on ImageKit {kept}; wrote {manifest_file}')
    return manifest


def push(manifest, site, dry_run):
    url = site['url'].rstrip('/') + '/photo/api/ingest/'
    r = requests.post(url, json=manifest, timeout=120,
                      params={'dry_run': '1'} if dry_run else None,
                      headers={'Authorization': f'Bearer {site["token"]}'})
    try:
        rep = r.json()
    except ValueError:
        sys.exit(f'push failed {r.status_code}: {r.text[:500]}')
    if r.status_code != 200:
        sys.exit(f'push failed {r.status_code}: {rep.get("error")}')

    a = rep['album']
    print(f'{"DRY RUN: " if rep["dry_run"] else ""}album {a["id"]} {a["slug"]}'
          f'{" (new)" if a["created"] else ""}')
    for key in ('created', 'updated', 'unchanged'):
        print(f'  {key}: {len(rep[key])}')
    for w in rep['warnings']:
        warn(w)
    for c in rep['conflicts']:
        warn(f'{c["name"]} is already image {c["id"]} in another album: '
             f'{c["stored_path"]} (skipped, not moved)')
    for e in rep['errors']:
        warn(f'{e["name"]}: {e["error"]}')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('dir', type=Path, help='album folder')
    ap.add_argument('--config', type=Path, default=default_config())
    ap.add_argument('--domain', type=int, help='fotoweb domain, overrides [domains]')
    ap.add_argument('--force', action='store_true', help='upload every file again')
    ap.add_argument('--no-upload', action='store_true',
                    help='only describe files that are already on ImageKit')
    ap.add_argument('--push', action='store_true', help='send the manifest to the site')
    ap.add_argument('--dry-run', action='store_true', help='with --push: server reports, writes nothing')
    args = ap.parse_args()

    if args.force and args.no_upload:
        sys.exit('--force and --no-upload contradict each other')
    if args.dry_run and not args.push:
        sys.exit('--dry-run only applies with --push')
    if not args.dir.is_dir():
        sys.exit(f'not a folder: {args.dir}')
    if not args.config.exists():
        sys.exit(f'config not found: {args.config} (see the top of this script)')
    cfg = tomllib.loads(args.config.read_text(encoding='utf-8'))

    manifest = build(args.dir.resolve(), cfg, args)
    if args.push:
        push(manifest, cfg['site'], args.dry_run)


if __name__ == '__main__':
    main()
