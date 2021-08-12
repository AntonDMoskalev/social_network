from django.forms import ModelForm, widgets
from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {'text': 'Текст',
                  'group': 'Группы',
                  'image': 'Изображние'}
        help_texts = {'text': 'Введите текст',
                      'group': 'Выберите из списка',
                      'image': 'Загрузить изображение'}


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {'text': 'Оставьте комментарий'}
        widgets = {'text': widgets.Textarea(attrs={'class': 'form-control'}), }
