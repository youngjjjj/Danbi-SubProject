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
    content = m.TextField()

    def __str__(self):
        return self.content

    class Meta:
        db_table = 'board'
        ordering = ['-id']
        verbose_name = '게시판'


class Comment(TimestampedModel):
    author = m.ForeignKey(settings.AUTH_USER_MODEL, on_delete=m.CASCADE)
    board = m.ForeignKey(Boards, on_delete=m.CASCADE)
    text = m.CharField(max_length=255)

    def __str__(self):
        return f'{self.author}님이 작성한 댓글 {self.text} 입니다.'

    class Meta:
        db_table = 'comment'
        ordering = ['-id']
        verbose_name = '댓글'





