from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin)
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from api.filters import TitleFilter
from api.permissions import (IsAdmin, IsAdminModeratorAuthorOrReadOnly,
                             IsAdminOrReadOnly)
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, ReviewSerializer,
                             SignupSerializer, TitleReadSerializer,
                             TitleWriteSerializer, TokenSerializer,
                             UserSerializer)
from reviews.models import Category, Genre, Review, Title


User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = SignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.data.get('username')
    email = serializer.data.get('email')

    try:
        user, _ = User.objects.get_or_create(username=username, email=email)
    except IntegrityError as err:
        return Response(
            {'detail': str(err)}, status=status.HTTP_400_BAD_REQUEST
        )
    else:
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            'YamDB confirmation code',
            f'Hello, your confirmation code is: "{confirmation_code}"',
            'no-reply@yamdb.com',
            (user.email, ),
            fail_silently=False,
        )

        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_jwt_token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.data.get('username')
    user = get_object_or_404(User, username=username)
    confirmation_code = serializer.data.get('confirmation_code')

    if default_token_generator.check_token(user, confirmation_code):
        token = RefreshToken.for_user(user).access_token
        return Response({'token': str(token)}, status=status.HTTP_200_OK)
    return Response(
        {'detail': 'Enter valid confirmation code and try again.'},
        status=status.HTTP_400_BAD_REQUEST
    )


class CDLViewSet(ListModelMixin, CreateModelMixin, DestroyModelMixin,
                 viewsets.GenericViewSet):
    pass


class CategoryViewSet(CDLViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrReadOnly, )
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    filter_backends = (SearchFilter, )
    search_fields = ('name', )

    lookup_field = 'slug'


class GenreViewSet(CDLViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrReadOnly, )
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

    filter_backends = (SearchFilter, )
    search_fields = ('name', )

    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrReadOnly, )

    filter_backends = (filters.DjangoFilterBackend, )
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsAdminModeratorAuthorOrReadOnly, )

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,
                          IsAdminModeratorAuthorOrReadOnly, )

    def get_queryset(self):
        review = get_object_or_404(
            Review, title_id=self.kwargs.get('title_id'),
            id=self.kwargs.get('review_id')
        )
        return review.comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsAdmin, )

    filter_backends = (SearchFilter, )
    search_fields = ('username', )

    lookup_field = 'username'

    @action(detail=False, methods=('GET', 'PATCH', ),
            permission_classes=(IsAuthenticated, ))
    def me(self, request):
        user = get_object_or_404(User, id=request.user.id)

        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save(role=user.role)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
