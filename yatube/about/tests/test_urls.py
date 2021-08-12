from django.test import TestCase, Client


class AboutURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.guest_client = Client()

    def test_url_about_tech_status_guest_client(self):
        """Checking template availability"""
        url_names = {
            'author': '/about/author/',
            'tech': '/about/tech/',
        }
        for code, url in url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)
