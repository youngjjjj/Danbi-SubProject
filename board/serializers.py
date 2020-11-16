from django.contrib.auth import get_user_model
from rest_framework import serializers as s
from .models import Boards, Comment, Post

User = get_user_model()


class AuthorSerializer(s.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username',
        ]


class BoardSerializer(s.ModelSerializer):
    author = AuthorSerializer(read_only=True)
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
            'title',
            'created_at',
            'updated_at',
        ]


class PostSerializer(s.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    is_author = s.SerializerMethodField("is_author_field")
    like_count = s.SerializerMethodField("like_count_field")
    is_like = s.SerializerMethodField("is_like_field")

    def is_author_field(self, post):
        if 'request' in self.context:
            user = self.context['request'].user
            return post.author == user

    def like_count_field(self, post):
        return post.like_post.count()

    def is_like_field(self, post):
        if 'request' in self.context:
            user = self.context['request'].user
            return post.like_post.filter(pk=user.pk).exists()

    class Meta:
        model = Post
        fields = [
            'author',
            'is_author',
            'is_like',
            'title',
            'content',
            'like_count',
            'created_at',
            'updated_at',
        ]


class CommentSerializer(s.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    is_author = s.SerializerMethodField("is_author_field")
    like_count = s.SerializerMethodField("like_count_field")
    is_like = s.SerializerMethodField("is_like_field")

    def is_author_field(self, comment):
        if 'request' in self.context:
            user = self.context['request'].user
            return comment.author == user

    def like_count_field(self, comment):
        return comment.like_comment.count()

    def is_like_field(self, comment):
        if 'request' in self.context:
            user = self.context['request'].user
            return comment.like_comment.filter(pk=user.pk).exists()

    class Meta:
        model = Comment
        fields = [
            'pk',
            'author',
            'is_author',
            'is_like',
            'text',
            'like_count',
            'created_at',
            'updated_at',
        ]