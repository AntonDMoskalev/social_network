from django.test import TestCase, Client
from django.urls import reverse


class AboutViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.guest_client = Client()

    def test_about_page_accessible_by_name(self):
        """The URL generated with static_pages is available."""
        urls_name = {
            "author": "about:author",
            "tech": "about:tech"
        }
        for name, reverse_name in urls_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse(reverse_name))
                self.assertEqual(response.status_code, 200)

    def test_about_page_uses_correct_template(self):
        """
        The correct pattern is applied
        to staticpages when queried
        """
        urls_name = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }
        for url, reverse_name in urls_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, url)
