from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

User = get_user_model()


def validate_year(value):
    if value > timezone.now().year:
        raise ValidationError(
            'Year field can\'t be greater than the current year.',
            params={'value': value},
        )


class Category(models.Model):
    name = models.CharField(max_length=256, verbose_name='Name')
    slug = models.SlugField(unique=True, verbose_name='Slug')

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name[:15]


class Genre(models.Model):
    name = models.CharField(max_length=256, verbose_name='Name')
    slug = models.SlugField(unique=True, verbose_name='Slug')

    class Meta:
        verbose_name = 'genre'
        verbose_name_plural = 'genres'

    def __str__(self):
        return self.name[:15]


class Title(models.Model):
    name = models.CharField(max_length=200, verbose_name='Name')
    year = models.IntegerField(
        validators=(validate_year, ), verbose_name='Year'
    )
    description = models.TextField(blank=True, verbose_name='Description')
    genre = models.ManyToManyField(Genre, through='TitleGenre')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True,
        related_name='titles', verbose_name='Category'
    )

    class Meta:
        verbose_name = 'title'
        verbose_name_plural = 'titles'

    def __str__(self):
        return self.name[:15]


class TitleGenre(models.Model):
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='genres',
        verbose_name='Title'
    )
    genre = models.ForeignKey(
        Genre, on_delete=models.CASCADE, related_name='titles',
        verbose_name='Genre'
    )

    class Meta:
        verbose_name = 'title and genre'
        verbose_name_plural = 'titles and genres'

    def __str__(self):
        return f'Title: {self.title_id} <---> Genre: {self.genre_id}'


class Review(models.Model):
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews',
        verbose_name='Title'
    )
    text = models.TextField(verbose_name='Text')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews',
        verbose_name='Author'
    )
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='Score'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Publication date'
    )

    class Meta:
        verbose_name = 'review'
        verbose_name_plural = 'reviews'
        constraints = (
            models.UniqueConstraint(
                name='unique_title_author',
                fields=('title', 'author', ),
            ),
        )

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments',
        verbose_name='Review'
    )
    text = models.TextField(verbose_name='Text')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments',
        verbose_name='Author'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name='Publication date'
    )

    class Meta:
        verbose_name = 'comment'
        verbose_name_plural = 'comments'

    def __str__(self):
        return self.text[:15]
