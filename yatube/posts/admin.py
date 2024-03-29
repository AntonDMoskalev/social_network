from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Post, Group, Comment, Follow


class PostAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "pub_date", "author")
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = _("-пусто-")


class GroupAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "description")
    search_fields = ("title",)
    list_filter = ("slug",)
    empty_value_display = _("-пусто-")


class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "text")
    search_fields = ("text",)
    list_filter = ("author",)
    empty_value_display = _("-пусто-")


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = ('user',)
    list_display = ('author', 'user',)
    empty_value_display = _("-пусто-")


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
