# Путь: NewsPortal/news/filters.py
import django_filters
from django.contrib.auth.models import User
from .models import Article, Category, Rating, Profile
from django import forms


class ArticleFilter(django_filters.FilterSet):
    """
    Фильтр для статей по различным полям.
    """
    title = django_filters.CharFilter(lookup_expr='icontains', label='Название')
    content = django_filters.CharFilter(lookup_expr='icontains', label='Содержание')

    # Фильтр по дате публикации (выбор даты)
    publication_date = django_filters.DateFilter(
        field_name='publication_date',
        lookup_expr='gt',
        label='Позже даты',
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    # Фильтр по категории
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        label='Категория',
        empty_label='Все'
    )

    # Фильтр по рейтингу
    rating = django_filters.ModelChoiceFilter(
        queryset=Rating.objects.all(),
        label='Рейтинг',
        empty_label='Все'
    )

    # Фильтр по автору (с использованием User)
    author_profile = django_filters.ModelChoiceFilter(
        queryset=User.objects.filter(groups__name='authors'),  # Только пользователи из группы 'authors'
        label='Автор',
        field_name='author_profile__user',  # Используем связь через Profile с User
        empty_label='Все'
    )

    # Фильтр по типу статьи
    article_type = django_filters.ChoiceFilter(
        choices=[('', 'Все'), (True, 'Статья'), (False, 'Новость')],
        label='Тип статьи',
        empty_label='Все'
    )

    class Meta:
        model = Article
        fields = ['title', 'content', 'author_profile', 'publication_date', 'category', 'rating', 'article_type']
