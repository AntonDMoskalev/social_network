from django.test import TestCase
from posts.models import Post, Group, User


class ModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create a record about the group in the database
        cls.group_test = Group.objects.create(
            title="Group of cat lovers",
            slug="cat",
            description="kitty-kitty-kitty")
        # Сreate a post in the database
        cls.post_test = Post.objects.create(
            text=("The story of a black cat, "
                  "who suffered all his life because of the color of his fur"),
            pub_date="",
            author=User.objects.create(username="test"),
            group=cls.group_test)

    def test_group_and_post_str_method(self):
        """__str__ return title for Group and for Post."""
        group = ModelTest.group_test
        expected_group_name = group.title
        text = ModelTest.post_test
        expected_text_name = text.text[:15]
        object_name = {
            expected_group_name: group,
            expected_text_name: text
        }
        for expected_name, value in object_name.items():
            with self.subTest(value=value):
                self.assertEqual(expected_name, str(value))
