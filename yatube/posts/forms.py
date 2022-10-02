from django.forms import ModelForm, widgets
from django.utils.translation import gettext_lazy as _
from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {'text': _('Текст'),
                  'group': _('Группы'),
                  'image': _('Изображние')}
        help_texts = {'text': _('Введите текст'),
                      'group': _('Выберите из списка'),
                      'image': _('Загрузить изображение')}


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {'text': _('Оставьте комментарий')}
        widgets = {'text': widgets.Textarea(attrs={'class': 'form-control'}), }
