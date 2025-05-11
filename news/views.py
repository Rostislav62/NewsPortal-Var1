# Путь: news/views.py
# Этот файл содержит представления для работы с новостями, пользователями и профилем.
# Он включает в себя классы представлений и общие вспомогательные методы, которые минимизируют дублирование кода.

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import update_session_auth_hash, authenticate, login
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.cache import cache
from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.http import HttpResponseBadRequest, JsonResponse
from django.utils import timezone
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import cache_page
from django.core.mail import send_mail
from django.conf import settings

from .models import Article, Category, Rating, Profile
from .forms import CustomUserChangeForm, CustomUserCreationForm
from .tasks import send_new_article_notification
from .utils import get_article_cache_key, get_category_by_id
from .email_utils import EmailContentBuilder, send_custom_email
from .filters import ArticleFilter
from .mixins import is_author_or_superuser, custom_user_passes_test




@cache_page(60)  # Кэшируем главную страницу на 1 минуту
def home(request):
    """
    Представление для главной страницы сайта.
    Кэширование установлено на 1 минуту.
    """
    return render(request, 'news/home.html')


class BaseArticleView(View):
    """
    Базовый класс для работы с представлениями, связанными со статьями.
    Содержит общие методы для работы с кэшем, пагинацией и уведомлениями.
    """

    def get_articles(self, queryset=None, page_number=1, items_per_page=10):
        """
        Получение списка статей с поддержкой пагинации.

        :param queryset: Запрос статей, если None - используется Article.objects.all().
        :param page_number: Номер страницы для пагинации.
        :param items_per_page: Количество элементов на странице.
        :return: Объект пагинации и общее количество статей.
        """
        queryset = queryset or Article.objects.all().order_by('-publication_date')
        paginator = Paginator(queryset, items_per_page)

        try:
            page_obj = paginator.get_page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.get_page(1)
        except EmptyPage:
            page_obj = paginator.get_page(paginator.num_pages)

        return page_obj, queryset.count()

    def get_article(self, pk, article_type):
        """
        Получение объекта статьи по ID и проверка типа статьи.

        :param pk: ID статьи.
        :param article_type: Тип статьи, '0' для обычных статей, '1' для новостей.
        :return: Объект статьи или HttpResponseBadRequest при некорректном типе.
        """
        if article_type not in ['0', '1']:
            return HttpResponseBadRequest("Invalid article_type")

        type_value = article_type == '1'
        return get_object_or_404(Article, pk=pk, article_type=type_value)

    def clear_article_cache(self, article):
        """
        Очистка кэша для статьи.

        :param article: Объект статьи.
        """
        cache_key = get_article_cache_key(article.id, article.publication_date)
        cache.delete(cache_key)

    def get_article_from_cache(self, article_id, publication_date):
        """
        Получение статьи из кэша, если она была закэширована ранее.

        :param article_id: ID статьи.
        :param publication_date: Дата публикации статьи.
        :return: HTML-ответ или None, если кэш отсутствует.
        """
        cache_key = get_article_cache_key(article_id, publication_date)
        return cache.get(cache_key)

    def set_article_to_cache(self, article, response, timeout=300):
        """
        Сохранение статьи в кэш на указанный промежуток времени.

        :param article: Объект статьи.
        :param response: HTML-ответ, который будет закэширован.
        :param timeout: Время кэширования в секундах.
        """
        cache_key = get_article_cache_key(article.id, article.publication_date)
        cache.set(cache_key, response, timeout)

    def send_article_notification(self, article, use_celery=True):
        """
        Отправка уведомления подписчикам категории о новой статье.

        :param article: Объект статьи, для которой отправляется уведомление.
        :param use_celery: Использовать ли Celery для асинхронной отправки.
        """
        if use_celery:
            send_new_article_notification.delay(article.id)
        else:
            subscribers = article.category.subscribers.all()
            for subscriber in subscribers:
                subject, message = EmailContentBuilder.generate_notification_email(article, subscriber=subscriber)
                send_custom_email(subject, message, [subscriber.email], html_message=True)


class ArticleListView(BaseArticleView):
    """
    Представление для отображения списка статей.
    Использует метод пагинации и фильтрации из базового класса BaseArticleView.
    """
    template_name = 'news/article_list.html'
    paginate_by = 10

    def get(self, request):
        # Получение страницы и списка статей с учетом пагинации.
        page_number = request.GET.get('page', 1)
        page_obj, total_count = self.get_articles(page_number=page_number, items_per_page=self.paginate_by)

        return render(request, self.template_name, {
            'page_obj': page_obj,
            'total_count': total_count,
        })


class ArticleDetailView(BaseArticleView):
    """
    Представление для отображения детальной информации о статье.
    Проверяет наличие статьи в кэше перед загрузкой.
    """
    template_name = 'news/article_detail.html'

    def get(self, request, id):
        article = get_object_or_404(Article, id=id)

        # Попытка загрузить статью из кэша
        cached_response = self.get_article_from_cache(article.id, article.publication_date)
        if cached_response:
            return cached_response

        # Рендеринг и сохранение в кэш
        response = render(request, self.template_name, {
            'article': article,
            'user_is_author': request.user == article.author_profile.user,
        })
        self.set_article_to_cache(article, response)
        return response


class ArticleCreateView(LoginRequiredMixin, UserPassesTestMixin, BaseArticleView):
    """
    Представление для создания новой статьи.
    Проверяет права доступа пользователя и обрабатывает GET и POST запросы.
    """
    template_name = 'news/create_news.html'

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='authors').exists()

    def get(self, request):
        article_type = request.GET.get('article_type')
        if article_type not in ['news', 'article']:
            return HttpResponseBadRequest("Invalid article_type")

        # Определяем шаблон в зависимости от типа статьи
        self.template_name = 'news/create_news.html' if article_type == 'news' else 'news/articles/create_article.html'
        return render(request, self.template_name, {'categories': Category.objects.all()})

    def post(self, request):
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        article_type = request.GET.get('article_type')

        if not title or not content or not category_id:
            return render(request, self.template_name, {
                'error': 'Все поля должны быть заполнены.',
                'categories': Category.objects.all()
            })

        # Создание новой статьи
        category = get_category_by_id(category_id)
        article = Article.objects.create(
            title=title,
            author_profile=request.user.profile,
            content=content,
            publication_date=timezone.now(),
            article_type=(article_type == 'news'),
            category=category,
        )
        self.send_article_notification(article)
        return redirect('article_list')


class ArticleEditView(LoginRequiredMixin, UserPassesTestMixin, BaseArticleView):
    """
    Представление для редактирования существующей статьи.
    Проверяет права доступа пользователя и обновляет статью.
    """
    template_name = 'news/edit_news.html'

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='authors').exists()

    def get(self, request, pk):
        article_type = request.GET.get('article_type')
        article = self.get_article(pk, article_type)
        self.template_name = 'news/edit_news.html' if article.article_type else 'news/articles/edit_article.html'
        return render(request, self.template_name, {'article': article})

    def post(self, request, pk):
        article_type = request.GET.get('article_type')
        article = self.get_article(pk, article_type)

        title = request.POST.get('title')
        content = request.POST.get('content')
        if not title or not content:
            return render(request, self.template_name, {
                'error': 'Все поля должны быть заполнены.',
                'article': article
            })

        self.clear_article_cache(article)
        article.title = title
        article.content = content
        article.publication_date = timezone.now()
        article.save()
        return redirect('article_detail', id=article.pk)


class ArticleDeleteView(LoginRequiredMixin, UserPassesTestMixin, BaseArticleView):
    """
    Представление для удаления существующей статьи.
    Проверяет права доступа пользователя и удаляет статью.
    """
    template_name = 'news/delete_news.html'

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(name='authors').exists()

    def get(self, request, pk):
        article_type = request.GET.get('article_type')
        article = self.get_article(pk, article_type)
        self.template_name = 'news/delete_news.html' if article.article_type else 'news/articles/delete_article.html'
        return render(request, self.template_name, {'item': article})

    def post(self, request, pk):
        article_type = request.GET.get('article_type')
        article = self.get_article(pk, article_type)

        self.clear_article_cache(article)
        article.delete()
        return redirect('article_list')



class ArticleSearchView(BaseArticleView):
    """
    Представление для поиска и фильтрации статей.
    """
    template_name = 'news/article_search.html'
    paginate_by = 10

    def get(self, request):
        # Получаем все статьи, отсортированные по дате публикации
        queryset = Article.objects.all().order_by('-publication_date')

        # Фильтрация по типу статья или новость
        article_type_filter = request.GET.get('article_type')
        if article_type_filter == '1':
            queryset = queryset.filter(article_type=False)  # Статья
        elif article_type_filter == '0':
            queryset = queryset.filter(article_type=True)  # Новость

        # Фильтрация по автору (используем связь через user, а не profile)
        author_filter = request.GET.get('author_profile')
        if author_filter:
            queryset = queryset.filter(author_profile__user__id=author_filter)

        # Фильтрация по рейтингу
        rating_filter = request.GET.get('type')
        if rating_filter:
            queryset = queryset.filter(rating__value=rating_filter)

        # Фильтрация по содержимому
        content_filter = request.GET.get('content')
        if content_filter:
            queryset = queryset.filter(content__icontains=content_filter)

        # Фильтрация по категории
        category_filter = request.GET.get('category')
        if category_filter:
            queryset = queryset.filter(category__id=category_filter)

        # Применяем фильтры через ArticleFilter
        filterset = ArticleFilter(request.GET, queryset=queryset)
        queryset = filterset.qs

        # Пагинация
        paginator = Paginator(queryset, self.paginate_by)
        page_number = request.GET.get('page')

        try:
            page_obj = paginator.get_page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.get_page(1)
        except EmptyPage:
            page_obj = paginator.get_page(paginator.num_pages)

        # Получаем список авторов, состоящих в группе 'authors' (теперь через User)
        authors_group = Group.objects.get(name="authors")
        authors = User.objects.filter(groups=authors_group)

        # Получаем список категорий и рейтингов
        categories = Category.objects.all()
        ratings = Rating.objects.all()

        return render(request, self.template_name, {
            'filterset': filterset,
            'page_obj': page_obj,
            'filter_params': request.GET.urlencode(),
            'authors': authors,
            'ratings': ratings,
            'categories': categories,
        })


# @csrf_protect  # Защита от CSRF должна быть включена
# @login_required
# def subscribe_to_category(request, category_id):
#     """
#     Представление для подписки пользователя на категорию и отправки уведомления.
#     """
#     # Получаем категорию по ID
#     category = get_object_or_404(Category, id=category_id)
#
#     # Проверяем, если пользователь ещё не подписан на категорию то подписываем
#     if request.user not in category.subscribers.all():
#         category.subscribers.add(request.user)
#
#         # Создаём письмо о подписке
#         subject, message = EmailContentBuilder.generate_subscription_email(request.user, category)
#
#         # Отправка письма пользователю
#         send_custom_email(subject, message, [request.user.email], html_message=False)
#
#     return redirect('article_detail')

# from django.shortcuts import get_object_or_404, redirect
# from django.views.decorators.csrf import csrf_protect
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from .models import Article, Category
# from .views import BaseArticleView  # Импортируем для использования метода clear_article_cache
# from .email_utils import send_custom_email, EmailContentBuilder

@csrf_protect
@login_required
def subscribe_to_category(request, category_id):
    """
    Представление для подписки пользователя на категорию и отправки уведомления.
    Очистка кэша для статьи, если подписка выполнена.
    """
    # Получаем категорию по ID
    category = get_object_or_404(Category, id=category_id)

    # Получаем ID статьи из POST-запроса
    article_id = request.POST.get('article_id')
    article = get_object_or_404(Article, id=article_id)

    # Проверяем, если пользователь ещё не подписан на категорию
    if request.user not in category.subscribers.all():
        category.subscribers.add(request.user)

        # Очищаем кэш для статьи
        base_article_view = BaseArticleView()
        base_article_view.clear_article_cache(article)

        # Создаём письмо о подписке
        subject, message = EmailContentBuilder.generate_subscription_email(request.user, category)

        # Отправка письма пользователю
        send_custom_email(subject, message, [request.user.email], html_message=False)

        # # Отображение сообщения об успешной подписке
        # messages.success(request, f'Вы успешно подписались на категорию {category.name}.')

    # Перенаправляем обратно на страницу статьи
    return redirect('article_detail', id=article.id)


# Функция для проверки лимита публикаций
@user_passes_test(is_author_or_superuser, login_url='permission_denied')
def check_post_limit(request):
    """
    Проверка лимита публикаций за последние 24 часа и перенаправление на создание поста или страницу с сообщением.
    """
    # Получаем текущего пользователя и тип статьи
    user = request.user
    article_type = request.GET.get('article_type')

    # Проверяем, что параметр article_type указан и корректен
    if article_type not in ['news', 'article']:
        return HttpResponseBadRequest("Invalid article_type parameter")

    # Определяем лимиты для пользователя
    post_limit = 5 if user.groups.filter(name='premium').exists() else 3

    # Определяем временную метку для проверки публикаций за последние 24 часа
    time_threshold = timezone.now() - timezone.timedelta(days=1)

    # Считаем количество публикаций текущего пользователя за последние 24 часа
    posts_last_24_hours = Article.objects.filter(
        author_profile=user.profile,
        publication_date__gte=time_threshold
    ).count()

    # Проверка превышения лимита
    if posts_last_24_hours < post_limit:
        # Лимит не превышен, перенаправляем на страницу создания поста с параметром `article_type`
        return redirect(f'/create/?article_type={article_type}')
    else:
        # Лимит превышен, отправляем уведомление по email
        group_name = 'premium' if user.groups.filter(name='premium').exists() else 'basic'
        subject, message = EmailContentBuilder.generate_limit_email(user, post_limit, group_name)

        # Отправка письма пользователю
        send_custom_email(subject, message, [user.email], html_message=False)

        # Лимит превышен, отображаем сообщение об ошибке
        error_message = f"Вы не можете публиковать более {post_limit} постов в сутки."
        return render(request, 'news/post_limit_exceeded.html', {'error_message': error_message})

