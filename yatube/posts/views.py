from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from .forms import PostForm, CommentForm
from .models import Post, Group, User, Follow
from django.views.decorators.http import require_GET
from django.core.cache import cache


@require_GET
def index(request):
    posts = cache.get('index_page')
    if posts is None:
        posts = Post.objects.all()
        cache.set('index_page', posts, timeout=20)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request,
                  'posts/index.html',
                  {'page': page, 'post': posts})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post = group.posts.all()

    paginator = Paginator(post, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request,
                  'posts/group.html',
                  {'page': page, 'post': post, 'group': group})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()

    paginator = Paginator(posts, 10)
    page_num = request.GET.get('page')
    page = paginator.get_page(page_num)

    following = False
    if (not request.user.is_anonymous
        and Follow.objects.filter(
            user=request.user, author=author).exists()):
        following = True

    return render(request,
                  'posts/profile.html', {
                      'posts': posts,
                      'author': author,
                      'page': page,
                      'following': following})


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = author.posts.get(pk=post_id)
    comments = post.comments.all()
    form = CommentForm()
    following = False
    if (not
        request.user.is_anonymous and Follow.objects.filter(
            user=request.user, author=author).exists()):
        following = True

    return render(request,
                  'posts/post.html', {
                      'author': author,
                      'post': post,
                      'username': request.user,
                      'post_id': post_id,
                      'comments': comments,
                      'form': form,
                      'following': following})


@login_required
def new_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('/')
        return render(request, 'posts/new_post.html', {'form': form})
    form = PostForm()
    return render(request,
                  'posts/new_post.html',
                  {'form': form})


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, pk=post_id)
    author = post.author
    if request.user != author:
        return redirect("post", username=username, post_id=post_id)
    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post)
    if form.is_valid():
        post = form.save(commit=False)
        post.save()
        return redirect("post", username=username, post_id=post_id)
    return render(request,
                  'posts/new_post.html',
                  {'form': form,
                   "username": username,
                   'post_id': post_id,
                   'post': post,
                   'is_edit': True})


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == "POST":
        form = CommentForm(request.POST or None)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect("post", username=username, post_id=post_id)
        return render(
            request, 'includes/comments.html', {
                'form': form,
                'username': request.user,
                'post_id': post_id})
    form = CommentForm()
    return render(
        request, 'includes/comments.html', {
            'form': form,
            'username': request.user,
            'post_id': post_id})


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)

    paginator = Paginator(posts, 10)
    page_num = request.GET.get('page')
    page = paginator.get_page(page_num)

    return render(request, "posts/follow.html", {'page': page})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author and (
        not Follow.objects.filter(
            user=request.user, author=author).exists()):
        Follow.objects.create(user=request.user, author=author)
        return redirect('profile', username)
    else:
        return redirect('profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    post_delete = Follow.objects.get(user=request.user, author=author)
    post_delete.delete()
    return redirect('profile', username)
