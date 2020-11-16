from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views as v

router = DefaultRouter()
router.register('board', v.BoardViewSet, basename='board')
router.register(r'board/(?P<board_pk>\d+)/post', v.PostViewSet, basename='post')
router.register(r'board/(?P<board_pk>\d+)/post/(?P<post_pk>\d+)/comment', v.CommentViewSet, basename='comment')

urlpatterns = [
    path("", include(router.urls)),
]
