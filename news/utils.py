# # Путь: NewsPortal/news/utils.py
#
# from django.core.cache import cache
#
# def get_article_cache_key(article_id, publication_date):
#     """
#     Создаёт уникальный ключ для кэширования статьи на основе её ID и даты последнего изменения.
#     """
#     return f"article_{article_id}_{publication_date}"

from django.core.cache import cache
from django.shortcuts import get_object_or_404
from .models import Category  # Импортируем модель Category, чтобы использовать её в функции

def get_article_cache_key(article_id, publication_date):
    """
    Создаёт уникальный ключ для кэширования статьи на основе её ID и даты последнего изменения.
    """
    return f"article_{article_id}_{publication_date}"

def get_category_by_id(category_id):
    """
    Возвращает объект категории по его ID.
    :param category_id: ID категории
    :return: Объект категории или 404, если не найдено
    """
    return get_object_or_404(Category, id=category_id)
