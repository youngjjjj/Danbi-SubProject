from django.contrib.auth import get_user_model
from rest_framework import serializers as s
from .models import Boards, Comment

User = get_user_model()


class AuthorSerializers(s.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username',
        ]


class BoardSerializer(s.ModelSerializer):
    author = AuthorSerializers(read_only=True)
    is_author = s.SerializerMethodField("is_author_field")

    def is_author_field(self, board):
        if 'request' in self.context:
            user = self.context['request'].user
            return board.author == user

    class Meta:
        model = Boards
        fields = [
            'pk',
            'author',
            'is_author',
            'content',
        ]


class CommentSerializer(s.ModelSerializer):
    author = AuthorSerializers(read_only=True)
    is_author = s.SerializerMethodField("is_author_field")

    def is_author_field(self, comment):
        if 'request' in self.context:
            user = self.context['request'].user
            return comment.author == user

    class Meta:
        model = Comment
        fields = [
            'pk',
            'author',
            'is_author',
            'text',
        ]