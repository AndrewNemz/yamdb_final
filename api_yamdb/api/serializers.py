from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User

from .validators import validate_username


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        exclude = ['id']


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        exclude = ['id']


class TitleSerializer(serializers.ModelSerializer):
    """
    Displays genre and category as dictionaries with name and slug
    """

    category = CategorySerializer()
    genre = GenreSerializer(many=True)
    rating = serializers.FloatField(required=False)

    class Meta:
        fields = '__all__'
        model = Title


class TitleSerializerWithSlugFields(TitleSerializer):
    """
    Serializer for unsafe methods, serializes category and genre from slugs
    """

    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        many=True, slug_field='slug',
        queryset=Genre.objects.all()
    )


class SignUpSerializer(serializers.ModelSerializer):
    """
    validates username against standard unicode regex and checks its not 'me'
    """
    email = serializers.EmailField(max_length=254, allow_blank=False)
    username = serializers.CharField(max_length=150, allow_blank=False,
                                     validators=[validate_username])

    class Meta:
        model = User
        fields = ('email', 'username')


class GetTokenSerializer(serializers.ModelSerializer):
    """
    Checks confirmation code against user's hidden field
    """
    username = serializers.CharField(
        required=True,
        max_length=150,
    )
    confirmation_code = serializers.CharField(
        required=True,
    )

    class Meta:
        model = User
        fields = (
            'username',
            'confirmation_code'
        )

    def validate(self, data):
        user = get_object_or_404(User, username=data['username'])
        if data['confirmation_code'] != user.confirmation_code:
            raise ValidationError('Неверный код подтверждения')
        return data


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for UserViewSet
    """

    class Meta:
        model = User
        fields = [
            'username', 'email',
            'first_name', 'last_name',
            'bio', 'role'
        ]


class ReviewSerializer(serializers.ModelSerializer):
    """
    Checks the author to write only one review for one title.
    """
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    title = serializers.PrimaryKeyRelatedField(read_only=True)

    def validate(self, data):
        title_id = self.context['view'].kwargs['title_id']
        author = self.context['request'].user
        if not self.context['request'].method == 'PATCH':
            if Review.objects.filter(title__id=title_id,
                                     author=author).exists():
                raise serializers.ValidationError(
                    'You can write only one review!'
                )
        return data

    class Meta:
        fields = '__all__'
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for CommentViewSet.
    """
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    review = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        fields = '__all__'
        model = Comment
