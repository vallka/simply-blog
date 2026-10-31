from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.test import TestCase

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
