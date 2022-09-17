from django.shortcuts import render, get_object_or_404, redirect, resolve_url
from . models import Post, Comment
from . forms import PostForm, CommentForm
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q


def index(request):
    page_number = request.GET.get('page', '1')
    kw = request.GET.get('kw', '')
    post_list = Post.objects.order_by('-pub_date')
    if kw:
        post_list = post_list.filter(
            Q(subject__icontains=kw) |
            Q(content__icontains=kw) |
            Q(author__username__icontains=kw) |
            Q(comment__comment__icontains=kw) |
            Q(comment__author__username__icontains=kw)
        ).distinct()  # 하나의 포스트에 달린 복수의 댓글이 모두 검색조건에 해당하는 경우, 검색결과에 동일한 포스트가 반복되어 표시되므로 중복을 제거하기 위함
    paginator = Paginator(post_list, 10)
    page_obj = paginator.get_page(page_number)
    context = {'post_list': page_obj, 'page': page_number, 'kw': kw}
    return render(request, 'chemblog/index.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.pub_date = timezone.now()
            comment.post_id = post.id
            comment.save()
            return redirect('{}#comment_{}'.format(resolve_url('chemblog:post_detail', post_id=post.id), comment.id))
    # Sort by
    if request.GET.get('sortby') == 'best':
        comment_list = post.comment_set.all().order_by('-voter')
    else:
        comment_list = post.comment_set.all().order_by('-pub_date')
    # comment_list = Comment.objects.order_by('-pub_date') 로 코딩하는 실수를 하여
    # 각각의 post entry 마다 모든 comment 객체가 나타났었음
    page_number = request.GET.get('page', 1)
    paginator = Paginator(comment_list, 10)
    page_obj = paginator.get_page(page_number)
    context = {'post': post, 'page_obj': page_obj}
    return render(request, 'chemblog/post_detail.html', context)


@login_required(login_url='common:login')
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.pub_date = timezone.now()
            post.save()
            return redirect('chemblog:index')
    else:
        form = PostForm()
    return render(request, 'chemblog/post_form.html', {'form': form})


@login_required(login_url='common:login')
def post_modify(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        messages.error(request, 'You are not authorized to make this modification')
        return redirect('chemblog:post_detail', post_id=post.id)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.modify_date = timezone.now()
            post.save()
            return redirect('chemblog:post_detail', post_id=post.id)

    else:
        form = PostForm(instance=post)
    # 만약 여기서 else를 생략하면 form.is_valid()가 False인 경우에도 템플릿에서 구현한 오류 메시지가 나타나지 않는다.
    # 그 이유는 form.is_valid()가 False 이면 form = PostForm(instance=post)가 렌더링 되기 때문이다.
    # 하지만 else 가 있다면 당연히 form = PostForm(instance=post)을 건너뛰고 그 아래의 return 구문을 실행한다는 뜻이다.
    return render(request, 'chemblog/post_form.html', {'form': form})


@login_required(login_url='common:login')
def post_delete(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        messages.error(request, 'You are not authorized to make this modification')
        return redirect('chemblog:post_detail', post_id=post.id)
    post.delete()
    return redirect('chemblog:index')


@login_required(login_url='common:login')
def post_vote(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user == post.author:
        messages.error(request, "Cannot make recommendation for one's own post")
    else:
        post.voter.add(request.user)
    return redirect('chemblog:post_detail', post_id=post.id)


@login_required(login_url='common:login')
def comment_vote(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user == comment.author:
        messages.error(request, "Cannot make recommendation for your own comment")
    else:
        comment.voter.add(request.user)
    return redirect('{}#comment_{}'.format(resolve_url('chemblog:post_detail', post_id=comment.post.id), comment.id))


@login_required(login_url='common:login')
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author:
        messages.error(request, 'You are not authorized to remove this comment')
    else:
        comment.delete()
    return redirect('chemblog:post_detail', post_id=comment.post.id)
