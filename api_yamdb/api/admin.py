from django.contrib import admin
from reviews.models import Category, Comment, Genre, Review, Title

admin.site.register(
    [Title, Genre, Category, Review, Comment]
)
