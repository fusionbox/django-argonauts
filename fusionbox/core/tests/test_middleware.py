from django.test import TestCase
from django.test.utils import override_settings


class TestGenericTemplateFinderMiddleware(TestCase):
    @override_settings(APPEND_SLASH=False)
    def test_respects_no_append_slash(self):
        response = self.client.get('/blog')
        self.assertEqual(response.status_code, 200)

    def test_appends_slash(self):
        response = self.client.get('/blog')
        self.assertRedirects(response, '/blog/', 301)

    def test_slashed_url_finds_index(self):
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)

    def test_finds_templates_without_html(self):
        response = self.client.get('/news/')
        print response.content
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/blog/detail/')
        self.assertEqual(response.status_code, 200)
