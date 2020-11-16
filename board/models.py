from django.db import models as m
from django.conf import settings
# Create your models here.


class TimestampedModel(m.Model):
    created_at = m.DateTimeField(auto_now_add=True)
    updated_at = m.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Boards(TimestampedModel):
    author = m.ForeignKey(settings.AUTH_USER_MODEL, on_delete=m.CASCADE)
    title = m.CharField(max_length=50)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'board'
        ordering = ['-id']
        verbose_name = '게시판'


class Post(TimestampedModel):
    author = m.ForeignKey(settings.AUTH_USER_MODEL, on_delete=m.CASCADE)
    board = m.ForeignKey(Boards, on_delete=m.CASCADE)
    title = m.CharField(max_length=50)
    content = m.TextField()
    like_post = m.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='post_like')

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'post'
        ordering = ['-id']
        verbose_name = '게시글'


class Comment(TimestampedModel):
    author = m.ForeignKey(settings.AUTH_USER_MODEL, on_delete=m.CASCADE)
    post = m.ForeignKey(Post, on_delete=m.CASCADE)
    text = m.CharField(max_length=255)
    like_comment = m.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='comment_like')

    def __str__(self):
        return f'{self.author}님이 작성한 댓글 {self.text} 입니다.'

    class Meta:
        db_table = 'comment'
        ordering = ['-id']
        verbose_name = '댓글'
