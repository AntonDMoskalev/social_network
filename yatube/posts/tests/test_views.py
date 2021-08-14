from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from posts.models import Group, Post, Follow
from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
import shutil
import tempfile
from django.core.cache import cache

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostGroupViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="test")
        cls.user_2 = User.objects.create(username='test_2')
        # Create object Group cat
        cls.test_group_cat = Group.objects.create(
            title="Группа любителей котов",
            slug="cat",
            description="кис-кис-кис")
        # Create object Group dog
        cls.test_group_dog = Group.objects.create(
            title="Группа любителей собак",
            slug="dog",
            description="гав-гав-гав")
        # Create object image
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        # Create object Post post_test
        cls.post_test = Post.objects.create(
            text=("Рассказ о чёрном коте, "
                  "который всю жизнь страдал из за цвета своей шерсти"),
            pub_date="",
            author=cls.user,
            group=cls.test_group_cat,
            image=uploaded)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Рекурсивно удаляем временную после завершения тестов
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Create authorized client
        self.user = PostGroupViewsTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)
        self.guest_client = Client()
        cache.clear()

    def test_views_use_correct_template(self):
        """Checking, that the Views class uses the appropriate template."""
        templates_pages_names = {
            'posts/index.html': reverse('index'),
            'posts/new_post.html': reverse('new_post'),
            'posts/group.html': (
                reverse(
                    'group_posts',
                    kwargs={'slug': PostGroupViewsTests.test_group_cat.slug})
            ),
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_take_correct_context(self):
        """The index template is rendered with the correct context."""
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(
            response.context['post'][0].text,
            PostGroupViewsTests.post_test.text)
        self.assertEqual(
            response.context['post'][0].author,
            PostGroupViewsTests.post_test.author)
        self.assertEqual(
            response.context['post'][0].group,
            PostGroupViewsTests.post_test.group)
        self.assertEqual(
            response.context['post'][0].image,
            PostGroupViewsTests.post_test.image)

    def test_group_pages_show_correct_context(self):
        """
        The group / <slug>
        template is well-formed with the correct context."""
        response = self.authorized_client.get(
            reverse(
                'group_posts',
                kwargs={'slug': PostGroupViewsTests.test_group_cat.slug}))
        self.assertEqual(
            response.context['group'].title,
            PostGroupViewsTests.test_group_cat.title)
        self.assertEqual(
            response.context['group'].slug,
            PostGroupViewsTests.test_group_cat.slug)
        self.assertEqual(
            response.context['group'].description,
            PostGroupViewsTests.test_group_cat.description)
        self.assertEqual(
            response.context['post'][0].text,
            PostGroupViewsTests.post_test.text)
        self.assertEqual(
            response.context['post'][0].author,
            PostGroupViewsTests.post_test.author)
        self.assertEqual(
            response.context['post'][0].group,
            PostGroupViewsTests.post_test.group)
        self.assertEqual(
            response.context['post'][0].image,
            PostGroupViewsTests.post_test.image)

    def test_new_post_show_correct_form(self):
        """
        Checking that the context is correctly passed to the
        / new / form."""
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_edit_post_show_correct_form(self):
        """
        Checking that the context is correctly passed to the
        / edit / form."""
        response = self.authorized_client.get(reverse(
            'post_edit',
            kwargs={
                'username': PostGroupViewsTests.user,
                'post_id': PostGroupViewsTests.post_test.pk}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_user_post_correct_context(self):
        """Checking for correct context passing to / username /."""
        response = self.authorized_client.get(reverse(
            'profile',
            kwargs={'username': PostGroupViewsTests.user}))
        self.assertEqual(
            response.context['page'][0].text,
            PostGroupViewsTests.post_test.text)
        self.assertEqual(
            response.context['page'][0].author,
            PostGroupViewsTests.post_test.author)
        self.assertEqual(
            response.context['page'][0].group,
            PostGroupViewsTests.post_test.group)
        self.assertEqual(
            response.context['page'][0].image,
            PostGroupViewsTests.post_test.image)

    def test_user_post_id_correct_context(self):
        """
        Checking the correct transfer of the context to the form
        / username / id /
        """
        response = self.authorized_client.get(reverse(
            'post',
            kwargs={
                'username': PostGroupViewsTests.user.username,
                'post_id': PostGroupViewsTests.post_test.pk}))
        self.assertEqual(
            response.context['post'].text,
            PostGroupViewsTests.post_test.text)
        self.assertEqual(
            response.context['post'].author,
            PostGroupViewsTests.post_test.author)
        self.assertEqual(
            response.context['post'].group,
            PostGroupViewsTests.post_test.group)
        self.assertEqual(
            response.context['post'].image,
            PostGroupViewsTests.post_test.image)

    def test_user_post_displayed_index(self):
        """Checking, post is displayed in index."""
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(
            response.context['post'][0].text,
            PostGroupViewsTests.post_test.text)

    def test_post_displayed_group_slug_post(self):
        """Checking, post is displayed in / group / slug post/."""
        response = self.authorized_client.get(
            reverse(
                'group_posts',
                kwargs={'slug': PostGroupViewsTests.test_group_cat.slug}))
        self.assertEqual(
            response.context['post'][0].text,
            PostGroupViewsTests.post_test.text)

    def test_post_no_displayed_in_no_slug_post(self):
        """Checking, post is not displayed in / group / slug not post /."""
        response = self.authorized_client.get(
            reverse(
                'group_posts',
                kwargs={'slug': PostGroupViewsTests.test_group_dog.slug}))
        post = response.context['post'].count()
        self.assertEqual(post, 0)

    def test_index_cach_20(self):
        """Checking that the cache keeps 20 seconds."""
        response = self.authorized_client.get(reverse('index'))
        post_count = response.context['post'].count()
        PostGroupViewsTests.post_test.delete
        self.assertEqual(
            response.context['post'].count(),
            post_count)

    def test_adding_subscribers(self):
        """Check subscription"""
        username = PostGroupViewsTests.user
        follower_count = username.following.count()
        # Check subscription
        self.authorized_client_2.post(reverse(
            'profile_follow', kwargs={'username': username}))
        follower_count_2 = username.following.count()
        self.assertEqual(follower_count + 1, follower_count_2)

    def test_del_subscribers(self):
        """Check unsubscription"""
        username = PostGroupViewsTests.user
        Follow.objects.create(user=PostGroupViewsTests.user_2, author=username)
        follower_count = username.following.count()
        self.authorized_client_2.post(reverse(
            'profile_unfollow', kwargs={'username': username}))
        follower_count_2 = username.following.count()
        self.assertEqual(follower_count - 1, follower_count_2)

    def test_post_follower(self):
        """Checking Subscribed Posts"""
        username_1 = PostGroupViewsTests.user

        self.authorized_client_2.post(reverse(
            'profile_follow', kwargs={'username': username_1}))
        response = self.authorized_client_2.get(reverse('follow_index'))
        # Checking the posts of the authors of the subscription
        self.assertEqual(
            response.context['page'][0].text,
            PostGroupViewsTests.post_test.text)
        # We check that the posts did not appear
        response = self.authorized_client.get(reverse('follow_index'))
        self.assertEqual(len(response.context['page'].object_list), 0)

        def test_create_comment_authorized_user(self):
            post = PostGroupViewsTests.post_test
            comment_count = post.comments.count()
            form_data = {'text': 'Пост супер бомба', 'post': post}
            self.authorized_client.post(reverse(
                'add_comment',
                kwargs={'username': post.author, 'post_id': post.pk}),
                data=form_data, follow=True)
            self.assertEqual(post.comments.count(), comment_count + 1)

    def test_create_comment_guest_user(self):
        post = PostGroupViewsTests.post_test
        comment_count = post.comments.count()
        form_data = {'text': 'Пост супер бомба', 'post': post}
        self.guest_client.post(
            reverse('add_comment',
                    kwargs={'username': post.author,
                            'post_id': post.pk}),
            data=form_data, follow=True)
        self.assertEqual(post.comments.count(), comment_count)


class PaginatorViewsTest(TestCase):
    """Checking paginator"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create object Post
        cls.base_group_test = Group.objects.create(
            title="Группа любителей котов",
            slug="cat",
            description="кис-кис-кис")
        # Create x13 object Post
        cls.user = User.objects.create(username="test")
        for i in range(0, 13):
            cls.base_post_test = Post.objects.create(
                text=("Рассказ о чёрном коте, "
                      "который всю жизнь страдал "
                      "из за цвета своей шерсти" + str(i)),
                pub_date="",
                author=cls.user,
                group=cls.base_group_test)
        cache.clear()

    def setUp(self):
        # Create guest Client
        self.client = Client()

    def test_first_page_contains_ten_post(self):
        """Check, only 10 posts are displayed on the first page"""
        page_object = {
            10: reverse('index'),
            3: reverse('index') + '?page=2'
        }
        for count_object, url in page_object.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(
                    len(response.context['page'].object_list), count_object)
