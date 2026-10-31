import io
import shutil
import tempfile
from datetime import timedelta

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.utils import timezone
from PIL import Image as PILImage

from .models import Post


class SearchViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        past = timezone.now() - timedelta(days=1)
        Post.objects.create(title='Castles of Scotland', text='Ruined keeps', blog=True, blog_start_dt=past)
        Post.objects.create(title='Peñíscola', text='A walled town', blog=True, blog_start_dt=past)
        Post.objects.create(title='Draft castle', text='', blog=False, blog_start_dt=past)
        Post.objects.create(title='Future castle', text='', blog=True,
                            blog_start_dt=timezone.now() + timedelta(days=1))

    def titles(self, q):
        response = self.client.get('/blog/search/', {'q': q})
        self.assertEqual(response.status_code, 200)
        return [p.title for p in response.context['post_list']]

    def test_stemmed_match_skips_unpublished(self):
        self.assertEqual(self.titles('castle'), ['Castles of Scotland'])

    def test_searches_text(self):
        self.assertEqual(self.titles('ruined'), ['Castles of Scotland'])

    def test_ignores_accents(self):
        self.assertEqual(self.titles('peniscola'), ['Peñíscola'])

    def test_exclusion(self):
        self.assertEqual(self.titles('castle -scotland'), [])

    def test_no_query(self):
        response = self.client.get('/blog/search/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['post_list']), [])


class ImageUploadViewEMTest(TestCase):
    def setUp(self):
        self.media = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.media, ignore_errors=True)

    def test_returns_path_for_easymde(self):
        image = io.BytesIO()
        PILImage.new('RGB', (10, 10)).save(image, 'PNG')
        upload = SimpleUploadedFile('a.png', image.getvalue(), content_type='image/png')

        with override_settings(MEDIA_ROOT=self.media):
            response = self.client.post('/markdownx/upload-em/', {'image': upload})

        self.assertEqual(response.status_code, 200)
        path = response.json()['data']['filePath']
        self.assertTrue(path.startswith('media/markdownx/'), path)

    def test_rejects_non_image(self):
        upload = SimpleUploadedFile('a.txt', b'text', content_type='text/plain')
        response = self.client.post('/markdownx/upload-em/', {'image': upload})
        self.assertEqual(response.status_code, 400)


class PagesTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.post = Post.objects.create(title='Castles', text='## Heading\n\n| a |\n|---|\n| b |', blog=True,
                                       blog_start_dt=timezone.now() - timedelta(days=1))
        Site.objects.create(domain='testserver', name='vallka')
        cls.admin = User.objects.create_superuser('admin', password='x')

    def test_public_pages(self):
        for url in ['/blog/', f'/blog/{self.post.slug}/', '/sitemap.xml', '/castles/']:
            self.assertIn(self.client.get(url, follow=True).status_code, [200], url)

    def test_markdown_rendered(self):
        self.assertContains(self.client.get(f'/blog/{self.post.slug}/'), '<table>')

    def test_admin_editor(self):
        self.client.force_login(self.admin)
        response = self.client.get(f'/admin/blog/post/{self.post.id}/change/')
        self.assertContains(response, 'class="markdownx"')
        self.assertContains(response, '/markdownx/upload-em/')
        self.assertNotContains(response, '<div class="markdownx-preview">')
        self.assertNotContains(response, 'btn-send-test')
