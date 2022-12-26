from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (CategoryViewSet, GenreViewSet, TitleViewSet, ReviewViewSet,
                    CommentViewSet, UserViewSet, get_jwt_token, signup)

v1_router = SimpleRouter()

v1_router.register('categories', CategoryViewSet)
v1_router.register('genres', GenreViewSet)
v1_router.register('titles', TitleViewSet)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews'
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments'
)
v1_router.register('users', UserViewSet)

v1_auth_urls = [
    path('signup/', signup),
    path('token/', get_jwt_token),
]

urlpatterns = [
    path('v1/auth/', include(v1_auth_urls)),
    path('v1/', include(v1_router.urls)),
]
