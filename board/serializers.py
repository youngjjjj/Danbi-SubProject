from django.contrib.auth import get_user_model
from rest_framework import serializers as s
from .models import Boards, Comment

User = get_user_model()


class AuthorSerializers(s.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'pk',
            'username',
        ]


class BoardSerializer(s.ModelSerializer):
    author = AuthorSerializers(read_only=True)

    class Meta:
        model = Boards
        fields = [
            'pk',
            'author',
            'content',
        ]


class CommentSerializer(s.ModelSerializer):
    author = AuthorSerializers(read_only=True)

    class Meta:
        model = Comment
        fields = [
            'pk',
            'author',
            'text',
        ]