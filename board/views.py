from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from .models import Boards, Comment, Post
from .serializers import BoardSerializer, CommentSerializer, PostSerializer, AuthorSerializer


class BoardViewSet(viewsets.ModelViewSet):
    queryset = Boards.objects.all().select_related('author')
    serializer_class = BoardSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        return super().perform_create(serializer)

    def perform_update(self, serializer):
        board = self.get_object()

        if board.author == self.request.user:
            serializer.save()
            return super().perform_update(serializer)

        raise PermissionDenied('접근권한이 없습니다.')

    def perform_destroy(self, instance):
        if instance.author == self.request.user:
            instance.delete()
        else:
            raise PermissionDenied('접근권한이 없습니다.')


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().select_related('author', 'board')
    serializer_class = PostSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        qs = Post.objects.filter(board_id=self.kwargs['board_pk'])
        return qs

    def perform_create(self, serializer):
        board = get_object_or_404(Boards, pk=self.kwargs['board_pk'])
        serializer.save(author=self.request.user, board=board)
        return super().perform_create(serializer)

    def perform_update(self, serializer):
        post = self.get_object()

        if post.author == self.request.user:
            serializer.save()
            return super().perform_update(serializer)

        raise PermissionDenied('접근권한이 없습니다.')

    def perform_destroy(self, instance):
        if instance.author == self.request.user:
            instance.delete()
        else:
            raise PermissionDenied('접근권한이 없습니다.')

    @action(detail=True, methods=['GET', 'POST'])
    def like(self, request, *args, **kwarg):
        post = self.get_object()
        user = self.request.user

        if self.request.method == "GET":
            if post.like_post.exists():
                data = post.like_post.all()
                serializer = AuthorSerializer(data=data, many=True)
                serializer.is_valid()
                return Response(data=serializer.data, status=status.HTTP_200_OK)

            raise ValidationError('post like not exists')
        elif self.request.method == "POST":
            if not post.like_post.filter(pk=user.pk).exists():
                post.like_post.add(user)
                return Response(status=status.HTTP_201_CREATED)
            raise ValidationError('user exists')

    @like.mapping.delete
    def delete_like(self, request, *args, **kwargs):
        post = self.get_object()
        user = self.request.user

        if post.like_post.filter(pk=user.pk).exists():
            post.like_post.remove(user)
            return Response(status=status.HTTP_204_NO_CONTENT)

        raise ValidationError('user not exists')


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().select_related('author', 'post')
    serializer_class = CommentSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        qs = Comment.objects.filter(post_id=self.kwargs['post_pk'])
        return qs

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs['post_pk'])
        serializer.save(author=self.request.user, post=post)
        return super().perform_create(serializer)

    def perform_update(self, serializer):
        comment = self.get_object()

        if comment.author == self.request.user:
            serializer.save()
            return super().perform_update(serializer)

        raise PermissionDenied('접근권한이 없습니다.')

    def perform_destroy(self, instance):
        if instance.author == self.request.user:
            instance.delete()
        else:
            raise PermissionDenied('접근권한이 없습니다.')

    @action(detail=True, methods=['GET', 'POST'])
    def like(self, request, *args, **kwarg):
        comment = self.get_object()
        user = self.request.user

        if self.request.method == "GET":
            if comment.like_comment.exists():
                data = comment.like_comment.all()
                serializer = AuthorSerializer(data=data, many=True)
                serializer.is_valid()
                return Response(data=serializer.data, status=status.HTTP_200_OK)

            raise ValidationError('post like not exists')
        elif self.request.method == "POST":
            if not comment.like_comment.filter(pk=user.pk).exists():
                comment.like_comment.add(user)
                return Response(status=status.HTTP_201_CREATED)
            raise ValidationError('user exists')

    @like.mapping.delete
    def delete_like(self, request, *args, **kwargs):
        comment = self.get_object()
        user = self.request.user

        if comment.like_comment.filter(pk=user.pk).exists():
            comment.like_comment.remove(user)
            return Response(status=status.HTTP_204_NO_CONTENT)

        raise ValidationError('user not exists')
