from api.permissions import IsAdminOrModeratorOrAuthorOrReadOnly
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from reviews.models import Category, Genre, Review, Title
from users.models import User

from .filters import TitleFilter
from .permissions import IsAdminOrReadOnly
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, GetTokenSerializer,
                          ReviewSerializer, SignUpSerializer, TitleSerializer,
                          TitleSerializerWithSlugFields, UserSerializer)
from .utils import get_tokens_for_user
from .validators import validate_username_or_email_exists
from .viewsets import CreateListDelVS


class TitleViewSet(viewsets.ModelViewSet):
    """
    Supports all request methods
    uses a different serializer for list and retrieve
    can filter by category and genre slugs + year and name
    """
    serializer_class = TitleSerializer
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    permission_classes = (IsAdminOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TitleSerializer
        return TitleSerializerWithSlugFields


class GenreViewSet(CreateListDelVS):

    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    permission_classes = (IsAdminOrReadOnly, )
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class CategoryViewSet(CreateListDelVS):

    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = (IsAdminOrReadOnly, )
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Supports all request methods except PUT.
    Access rights: administrator, moderator, author or read-only.
    """
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminOrModeratorOrAuthorOrReadOnly,)

    def get_title(self):
        return get_object_or_404(
            Title, pk=self.kwargs.get('title_id')
        )

    def perform_create(self, serializer):
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)

    def get_queryset(self):
        return self.get_title().reviews.all()


class CommentViewSet(viewsets.ModelViewSet):
    """
    Supports all request methods except PUT.
    Access rights: administrator, moderator, author or read-only.
    """
    serializer_class = CommentSerializer
    permission_classes = (IsAdminOrModeratorOrAuthorOrReadOnly,)

    def get_review(self):
        return get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title=self.kwargs.get('title_id')
        )

    def perform_create(self, serializer):
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)

    def get_queryset(self):
        return self.get_review().сomments.all()


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def send_confirmation_code(request):
    """
    If both passed fields are unique creates a new user
    otherwise fetches an existing one
    sends code
    """
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email, username = serializer.validated_data.values()
    if not User.objects.filter(email=email, username=username).exists():
        validate_username_or_email_exists(
            username=username,
            email=email
        )
        user = User.objects.create(
            username=username, email=email
        )
    user = User.objects.get(username=username)
    confirmation_code = default_token_generator.make_token(user)
    user.confirmation_code = confirmation_code
    user.save()
    send_mail(
        'Код подтверждения Yamdb',
        f'Ваш код подтверждения: {confirmation_code}',
        settings.DEFAULT_FROM_EMAIL,
        [email]
    )
    return Response(
        serializer.validated_data,
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_token(request):
    """
    Checks confirmation code, if its OK gives jwt token
    """
    serializer = GetTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User, username=serializer.validated_data['username']
    )
    confirmation_code = serializer.validated_data['confirmation_code']
    if default_token_generator.check_token(user, confirmation_code):
        token = get_tokens_for_user(user)
        response = {'token': str(token['access'])}
        return Response(response, status=status.HTTP_200_OK)
    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


class UserViewSet(viewsets.ModelViewSet):
    """
    Supports all methods except PUT
    Accessible by admin only
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrReadOnly, permissions.IsAuthenticated)
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request, pk=None):
        """
        This action method allows users to access their own profiles
        and patch them at api/v1/users/me
        """
        user = request.user
        if request.method == "GET":
            serializer = self.get_serializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == "PATCH":
            if 'role' in request.data and not (user.is_admin or user.is_staff):
                return Response(
                    {"Naughty boy"},
                    status=status.HTTP_403_FORBIDDEN
                )
            serializer = self.get_serializer(
                user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        return None
