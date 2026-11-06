import json

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.test import TestCase, override_settings

from .models import Album, Image


def make_image(name, folder='Valencia', **kwargs):
    return Image.objects.create(
        name=name,
        path=f'/C1/foto/{folder}/{name}',
        url=f'https://ik.imagekit.io/x/{name}',
        **kwargs,
    )


class ImageSearchViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Site.objects.create(domain='testserver', name='vallka')
        make_image('DJI_0456.jpg', tags='castle,loch-ness')
        make_image('DSC_0123.jpg', folder='Peñíscola_2048', title='Old town')
        make_image('DSC_0124.jpg', tags='castle', no_show=True)
        make_image('DSC_0125.jpg', tags='castle', domain=Album.Domains.LUCAS)

    def names(self, q):
        response = self.client.get('/photo/search/', {'q': q})
        self.assertEqual(response.status_code, 200)
        return [i.name for i in response.context['image_list']]

    def test_tags_skip_hidden_and_other_domains(self):
        self.assertEqual(self.names('castles'), ['DJI_0456.jpg'])

    def test_file_name_parts(self):
        self.assertEqual(self.names('DJI'), ['DJI_0456.jpg'])
        self.assertEqual(self.names('0456'), ['DJI_0456.jpg'])
        self.assertEqual(self.names('DJI_0456'), ['DJI_0456.jpg'])
        self.assertEqual(self.names('DJI_0456.jpg'), ['DJI_0456.jpg'])

    def test_path_folder_ignores_accents(self):
        self.assertEqual(self.names('peniscola'), ['DSC_0123.jpg'])
        self.assertEqual(self.names('valencia'), ['DJI_0456.jpg'])

    def test_no_query(self):
        self.assertEqual(self.names(''), [])


class PagesTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Site.objects.create(domain='testserver', name='vallka')
        cls.image = make_image('DJI_0456.jpg', title='Loch', tags='castle,loch', description='Water')
        cls.album = Album.objects.create(path='/C1/foto/Valencia', title='Valencia')

    def test_public_pages(self):
        for url in ['/photo/', f'/photo/{self.album.slug}/', f'/photo/s/{self.album.slug}/', '/photo/images/',
                    f'/photo/image/{self.image.name}/', f'/photo/image/{self.image.id}/json']:
            self.assertEqual(self.client.get(url, follow=True).status_code, 200, url)


class ImageAdminTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser('admin', password='x')
        cls.image = make_image('DJI_0456.jpg', title='Loch castle', tags='castle')
        make_image('DSC_0123.jpg', title='Other')
        Album.objects.create(path='/C1/foto/Valencia', title='Valencia')

    def setUp(self):
        self.client.force_login(self.admin)

    def test_search(self):
        response = self.client.get('/admin/fotoweb/image/', {'q': 'castle'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual([i.name for i in response.context['cl'].result_list], ['DJI_0456.jpg'])

    def test_album_and_instagram_filters(self):
        for q in ['a:valencia', 'a:instagram']:
            self.assertEqual(self.client.get('/admin/fotoweb/image/', {'q': q}).status_code, 200)

    def test_pages(self):
        for url in ['/admin/', '/admin/fotoweb/image/', f'/admin/fotoweb/image/{self.image.id}/change/',
                    '/admin/fotoweb/album/', '/admin/fotoweb/album/add/']:
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_edit_page_keeps_tag_tools_without_retired_ones(self):
        response = self.client.get(f'/admin/fotoweb/image/{self.image.id}/change/')
        self.assertContains(response, 'btn_add_tags')
        for retired in ['scenex', 'btn_make_title', 'btn_find_tags']:
            self.assertNotContains(response, retired)

    def test_mark_published_action(self):
        response = self.client.post('/admin/fotoweb/image/', {
            'action': 'make_published_shutter', '_selected_action': [self.image.id],
        })
        self.assertEqual(response.status_code, 302)
        self.image.refresh_from_db()
        self.assertTrue(self.image.shutter)
        self.assertIsNotNone(self.image.shutter_dt)


@override_settings(INGEST_TOKEN='secret')
class IngestTest(TestCase):
    album_path = '/d:/FOTO/Lucas/2025/25-11 Corbera,  Denia'

    def manifest(self, *names, folder=''):
        base = self.album_path + folder
        return {'version': 1,
                'album': {'path': self.album_path, 'title': '25-11 Corbera,  Denia', 'domain': 2},
                'images': [{'name': n, 'path': f'{base}/{n}', 'url': f'https://ik.imagekit.io/k/{n}',
                            'taken_dt': '2025-11-16T10:20:30Z', 'title': 'Corbera',
                            'description': 'Castle\x00', 'keywords': ['castle', 'spain']}
                           for n in names]}

    def post(self, manifest, token='secret', **params):
        url = '/photo/api/ingest/' + ('?dry_run=1' if params.get('dry_run') else '')
        return self.client.post(url, json.dumps(manifest), content_type='application/json',
                                HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_auth(self):
        self.assertEqual(self.post(self.manifest('a.jpg'), token='wrong').status_code, 403)
        with override_settings(INGEST_TOKEN=''):
            self.assertEqual(self.post(self.manifest('a.jpg')).status_code, 404)
        self.assertEqual(self.client.get('/photo/api/ingest/').status_code, 405)

    def test_create_album_and_images(self):
        r = self.post(self.manifest('b.jpg', 'a.jpg', folder='/JPEG-Full-size')).json()
        self.assertEqual(sorted(r['created']), ['a.jpg', 'b.jpg'])
        album = Album.objects.get(path=self.album_path)
        self.assertEqual((album.slug, album.domain, album.level), ('dfotolucas202525-11-corbera-denia', 2, 2))
        self.assertEqual(album.cover, 'https://ik.imagekit.io/k/a.jpg')
        self.assertEqual(str(album.taken_dt), '2025-11-16')
        img = Image.objects.get(name='a.jpg')
        self.assertEqual(img.url, img.url_fs)
        self.assertEqual(img.path, img.path_fs)
        self.assertEqual((img.domain, img.private, img.description, img.tags), (2, True, 'Castle', 'castle,spain'))
        self.assertEqual(img.created_dt.isoformat(), '2025-11-16T10:20:30+00:00')
        self.assertEqual(list(album.get_images().order_by('name').values_list('name', flat=True)), ['a.jpg', 'b.jpg'])

    def test_rerun_keeps_edits(self):
        self.post(self.manifest('a.jpg'))
        Image.objects.filter(name='a.jpg').update(title='Edited')
        r = self.post(self.manifest('a.jpg')).json()
        self.assertEqual((r['unchanged'], r['updated'], r['album']['created']), (['a.jpg'], [], False))
        self.assertEqual(Image.objects.get(name='a.jpg').title, 'Edited')

    def test_moved_file_is_a_conflict(self):
        make_image('a.jpg', folder='Valencia')
        r = self.post(self.manifest('a.jpg', 'b.jpg')).json()
        self.assertEqual(r['created'], ['b.jpg'])
        self.assertEqual([c['name'] for c in r['conflicts']], ['a.jpg'])
        self.assertEqual(Image.objects.get(name='a.jpg').path, '/C1/foto/Valencia/a.jpg')

    def test_dry_run_writes_nothing(self):
        r = self.post(self.manifest('a.jpg'), dry_run=True).json()
        self.assertEqual((r['dry_run'], r['created']), (True, ['a.jpg']))
        self.assertFalse(Album.objects.exists() or Image.objects.exists())

    def test_old_album_with_other_path_is_refused(self):
        Album.objects.create(path='/2024/d:/FOTO/Lucas/2025/25-11 Corbera,  Denia',
                             title='25-11 Corbera,  Denia', domain=2)
        r = self.post(self.manifest('a.jpg'))
        self.assertEqual(r.status_code, 400)
        self.assertIn('already exists', r.json()['error'])

    def test_bad_manifest(self):
        m = self.manifest('a.jpg')
        m['images'][0]['path'] = '/elsewhere/a.jpg'
        self.assertEqual(self.post(m).status_code, 400)
        self.assertEqual(self.post({'version': 2}).status_code, 400)
