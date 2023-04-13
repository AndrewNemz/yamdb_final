from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from users.models import User

from .validators import year_regex, year_validator


class Genre(models.Model):
    name = models.CharField(max_length=256, verbose_name='Genre name')
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Slug')

    class Meta:
        ordering = ['name']
        verbose_name = 'Genre'
        verbose_name_plural = 'Genres'

    def __str__(self) -> str:
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=256, verbose_name='Category name')
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Slug')

    class Meta:
        ordering = ['name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self) -> str:
        return self.name


class Title(models.Model):
    category = models.ForeignKey(
        Category, related_name='titles',
        on_delete=models.SET_NULL, null=True
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
    )
    name = models.CharField(max_length=256, verbose_name='Title name')
    year = models.PositiveSmallIntegerField(
        validators=[year_regex, year_validator],
        verbose_name='Release year'
    )
    description = models.CharField(max_length=1000, verbose_name='Description')

    class Meta:
        ordering = ['name']
        verbose_name = 'Title'
        verbose_name_plural = 'Titles'

    def __str__(self) -> str:
        return f'{self.category.name} {self.name}'


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Review title'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Review author'
    )
    text = models.TextField(verbose_name='Text')
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='Score'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Review date')

    class Meta:
        ordering = ['pub_date']
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_title_author'
            )
        ]

    def __str__(self):
        return f'{self.title}, {self.author}'


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='сomments',
        verbose_name='Comment review'
    )
    text = models.TextField(verbose_name='Text')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='сomments',
        verbose_name='Comment author'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Comment date')

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ['pub_date']

    def __str__(self):
        return self.text
