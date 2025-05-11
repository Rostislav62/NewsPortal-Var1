# # Путь: news/urls.py

from django.urls import path, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from . import views


from .views_auth import (
    RegisterView,
    ActivateAccountView,
    LoginView,
    ProfileView,
    ChangePasswordView,
    PermissionDeniedView,
    CustomPasswordChangeView,
    CustomPasswordChangeDoneView,
)


from .views import (
    ArticleListView,
    ArticleDetailView,
    ArticleCreateView,
    ArticleEditView,
    ArticleDeleteView,
    ArticleSearchView,
)


urlpatterns = [
    # Главная страница
    path('', views.home, name='home'),

    # Административная панель
    path('admin/', admin.site.urls),

    # Просмотр и детали статей и новостей
    # path('news/', views.article_list, name='article_list'),
    path('news/', ArticleListView.as_view(), name='article_list'),
    # path('news/<int:id>/', views.article_detail, name='article_detail'),
    path('news/<int:id>/', ArticleDetailView.as_view(), name='article_detail'),

    # Поиск статей и новостей
    # path('news/search/', article_search, name='article_search'),
    path('news/search/', ArticleSearchView.as_view(), name='article_search'),


    # Универсальные маршруты для создания, редактирования и удаления статей и новостей
    # path('create/', create_post, name='create_post'),  # Универсальный маршрут для создания статей и новостей
    path('create/', ArticleCreateView.as_view(), name='create_post'),
    # path('edit/<int:pk>/', edit_post, name='edit_post'),  # Универсальный маршрут для редактирования статей и новостей
    path('edit/<int:pk>/', ArticleEditView.as_view(), name='edit_post'),
    # path('delete/<int:pk>/', delete_post, name='delete_post'),  # Универсальный маршрут для удаления статей и новостей
    path('delete/<int:pk>/', ArticleDeleteView.as_view(), name='delete_post'),


    # path('login/', auth_views.LoginView.as_view(template_name='news/login.html'), name='login'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # path('register/', views.register, name='register'),
    path('register/', RegisterView.as_view(), name='register'),

    # Профиль пользователя и изменение пароля
    # path('profile/', views.profile_view, name='profile'),
    path('profile/', ProfileView.as_view(), name='profile'),
    # path('edit_profile/', edit_profile, name='edit_profile'),
    path('edit_profile/', ProfileView.as_view(), name='edit_profile'),
    # path('password_change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('change-password/', CustomPasswordChangeView.as_view(), name='change_password'),


    # Разрешение на доступ
    # path('permission_denied/', views.permission_denied_view, name='permission_denied'),
    path('permission-denied/', PermissionDeniedView.as_view(), name='permission_denied'),

    # # Подписка на категорию
    path('subscribe/<int:category_id>/', views.subscribe_to_category, name='subscribe_to_category'),

    # Временное решение: перенаправление с /accounts/login/ на /login/
    path('accounts/', include('allauth.urls')),
    path('accounts/login/', lambda request: redirect('login'), name='accounts_login_redirect'),

    # URL, который будет обрабатывать активацию пользователя при переходе по ссылке.
    # path('activate/<int:user_id>/', views.activate_account, name='activate_account'),
    path('activate/<int:user_id>/', ActivateAccountView.as_view(), name='activate_account'),


    # Сброс пароля по email
    # Маршрут для запроса сброса пароля
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='news/password_reset.html'),
         name='password_reset'),

    # Маршрут для уведомления об отправке письма
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='news/password_reset_done.html'),
         name='password_reset_done'),

    # Маршрут для сброса пароля по ссылке из письма
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='news/password_reset_confirm.html'),
         name='password_reset_confirm'),

    # Изменение пароля для авторизованных пользователей
    path('password_change/', CustomPasswordChangeView.as_view(), name='password_change'),  # Форма изменения пароля
    path('password-change-done/', CustomPasswordChangeDoneView.as_view(), name='password_change_done'),  # Уведомление об успешной смене пароля


    # Маршрут для уведомления об успешном сбросе пароля
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='news/password_reset_complete.html'),
         name='password_reset_complete'),


    # Проверка лимита постов перед перенаправлением на создание
    path('check_post_limit/', views.check_post_limit, name='check_post_limit'),

]
