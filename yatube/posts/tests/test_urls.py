from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls.base import reverse
from posts.models import Group, Post
from django.core.cache import cache


User = get_user_model()


class PostGroupURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="test")
        # Changing base_group_test text will affect base_post_test
        cls.base_group_test = Group.objects.create(
            title="Группа любителей котов",
            slug="cat",
            description="кис-кис-кис")
        # Create object Post
        cls.base_post_test = Post.objects.create(
            text=("Рассказ о чёрном коте,"
                  "который всю жизнь страдал из за цвета своей шерсти"),
            pub_date="",
            author=cls.user,
            group=cls.base_group_test)
        # Check urls authorized client
        cls.url_authorized = {
            'new_post': reverse('new_post'),
            'post_edit': reverse(
                'post_edit',
                kwargs={'username': cls.user,
                        'post_id': cls.base_post_test.pk})
        }
        # Check urls guest client
        cls.url_guest = {
            'index': reverse('index'),
            'group_slug': reverse(
                'group_posts', kwargs={'slug': cls.base_group_test.slug}),
            'user_profile': reverse('profile', kwargs={'username': cls.user}),
            "post_id": reverse(
                'post',
                kwargs={'username': cls.user,
                        'post_id': cls.base_post_test.pk}),
        }

    def setUp(self):
        # Create guest client
        self.guest_client = Client()
        # Create authorized client
        self.user = PostGroupURLTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # Create authorized client 2
        self.user2 = User.objects.create(username='test2')
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)

    def test_url_status_guest_client(self):
        """
        Checking the availability of address templates
        guest client
        """
        for code, url in PostGroupURLTests.url_guest.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_status_authorized_client(self):
        """
        Checking the availability of address templates
        autorized_client
        """
        for code, url in PostGroupURLTests.url_authorized.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_status_post_edit_and_new_guest_client(self):
        """Redirect when an anonymous user tries to edit and new post."""
        for code, url in PostGroupURLTests.url_authorized.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_url_status_post_edit__no_author_client(self):
        """Redirecting when trying to edit a post not by the author."""
        response = self.authorized_client2.get(
            PostGroupURLTests.url_authorized['post_edit'])
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_url_status_404(self):
        response = self.guest_client.get('/test404/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """The URL uses the matching pattern."""
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group.html': '/group/cat/',
            'posts/new_post.html': '/new/',
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_urls_edit_correct_template(self):
        """Template validation"""
        cache.clear()
        response = self.authorized_client.get(
            PostGroupURLTests.url_authorized['post_edit'])
        self.assertTemplateUsed(response, 'posts/new_post.html')

    def test_post_edit_url_redirect_no_author_post(self):
        """The page / <username> / <post_id> / edit / will redirect NOT the author
        of the post to the page /<username>/<post_id>/.
        """
        response = self.authorized_client2.get(
            PostGroupURLTests.url_authorized['post_edit'], follow=True)
        self.assertRedirects(
            response, PostGroupURLTests.url_guest['post_id'])

    def test_post_edit_url_redirect_anonymous_on_login(self):
        """The page /<username>/<post_id>/edit/ will redirect the anonymous user
        to the login page.
        """
        response = self.guest_client.get(
            f'/{PostGroupURLTests.user}/{self.base_post_test.pk}/edit/',
            follow=True)
        self.assertRedirects(
            response, (
                f'/auth/login/?next=/{PostGroupURLTests.user}/'
                f'{self.base_post_test.pk}/edit/'))
