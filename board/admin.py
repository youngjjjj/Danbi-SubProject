from django.contrib import admin
from .models import Boards, Comment


@admin.register(Boards)
class BoardsAdmin(admin.ModelAdmin):
    pass


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass
