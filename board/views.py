from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404

from .models import Boards, Comment
from .serializers import BoardSerializer, CommentSerializer


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


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().select_related('author', 'board')
    serializer_class = CommentSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        qs = Comment.objects.filter(board_id=self.kwargs['board_pk'])
        return qs

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        board = get_object_or_404(Boards, pk=self.kwargs['board_pk'])
        serializer.save(author=self.request.user, board=board)
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


