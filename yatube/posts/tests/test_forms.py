from posts.models import Post
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Post
from http import HTTPStatus
import shutil
import tempfile
from django.conf import settings
import io
from PIL import Image

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create(username='test')
        cls.form = PostForm()
        # Create object Post
        cls.post_test = Post.objects.create(
            text=("Рассказ о чёрном коте, "
                  "который всю жизнь страдал из за цвета своей шерсти"),
            pub_date="",
            author=cls.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Рекурсивно удаляем временную после завершения тестов
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Create authorized client
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCreateFormTests.user)
        # Create guest client
        self.guest_client = Client()

    def test_create_post_form(self):
        """Post creation check"""

        with io.BytesIO() as out:
            img = Image.new('RGBA', (10, 10), (255, 0, 0))
            img.save(out, 'GIF')
            small_gif = out.getvalue()

        form_data = {
            "text": 'кис-кис-кис-кис',
            "image": small_gif
        }
        # Remember the number of posts
        post_count = Post.objects.count()
        # Trying to create a post without authorization
        self.guest_client.post(reverse(
            'new_post'), data=form_data, follow=True)
        # Create a post by an authorized user
        response = self.authorized_client.post(reverse(
            'new_post'), data=form_data, follow=True)
        post_new = Post.objects.get(text='кис-кис-кис-кис')
        # Create a get by new post
        response_new_post = self.authorized_client.get(
            reverse(
                'post',
                kwargs={'username': post_new.author, 'post_id': post_new.pk})
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(response_new_post.status_code, HTTPStatus.OK)
        # Posts should increase by 1
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(post_new.text, 'кис-кис-кис-кис')
        self.assertEqual(post_new.author, PostCreateFormTests.user)
        self.assertEqual(post_new.group, None)

    def test_edit_post_form(self):
        """Checking post changes"""
        post = PostCreateFormTests.post_test
        post_count = Post.objects.count
        form_data = {
            'text': 'раз-два-три-четыре',
        }
        self.authorized_client.post(reverse(
            'post_edit',
            kwargs={
                'username': PostCreateFormTests.user,
                'post_id': post.id}),
            data=form_data, follow=True)
        post_create = Post.objects.get(text="раз-два-три-четыре")
        self.assertEqual(Post.objects.count, post_count)
        self.assertEqual(post_create, post)
        self.assertEqual(post_create.group, post.group)
        self.assertEqual(post_create.author, post.author)
