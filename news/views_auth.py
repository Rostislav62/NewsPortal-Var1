# Путь: news/views_auth.py
# Этот файл содержит представления, связанные с авторизацией, регистрацией и профилем пользователя.
# Все представления организованы в виде классов для улучшения читаемости и управления логикой.

from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.models import Group, User
from django.http import HttpResponseBadRequest
from django.conf import settings
from django.contrib.auth import get_user_model


from .forms import CustomUserChangeForm, CustomUserCreationForm
from .email_utils import EmailContentBuilder, send_custom_email

# Импортируем классы из встроенных представлений Django
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView

class CustomPasswordChangeView(PasswordChangeView):
    """
    Кастомизированное представление для изменения пароля.
    """
    template_name = 'registration/password_change_form.html'
    success_url = reverse_lazy('password_change_done')

class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    """
    Кастомизированное представление для отображения успешного изменения пароля.
    """
    template_name = 'registration/password_change_done.html'



class BaseAuthView(View):
    """
    Базовый класс для представлений, связанных с авторизацией.
    Содержит общие методы для работы с пользователями и группами.
    """

    def add_user_to_group(self, user, group_name):
        """
        Добавление пользователя в указанную группу.

        :param user: Объект пользователя.
        :param group_name: Имя группы, в которую нужно добавить пользователя.
        """
        group = Group.objects.get(name=group_name)
        user.groups.add(group)

    def remove_user_from_group(self, user, group_name):
        """
        Удаление пользователя из указанной группы.

        :param user: Объект пользователя.
        :param group_name: Имя группы, из которой нужно удалить пользователя.
        """
        group = Group.objects.get(name=group_name)
        user.groups.remove(group)


class RegisterView(BaseAuthView):
    """
    Представление для регистрации новых пользователей.
    """
    template_name = 'registration/register.html'

    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Создание пользователя, но пока не активного
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            # Добавление пользователя в группу 'basic' по умолчанию
            self.add_user_to_group(user, 'basic')

            # Отправка приветственного письма
            email_variant = int(settings.WELCOME_EMAIL_VARIANT)
            subject, message = EmailContentBuilder.generate_welcome_email(user, variant=email_variant)
            send_custom_email(subject, message, [user.email], html_message=False)

            return redirect('login')  # Перенаправление на страницу входа
        return render(request, self.template_name, {'form': form})


class ActivateAccountView(BaseAuthView):
    """
    Представление для активации аккаунта пользователя по ссылке.
    """
    def get(self, request, user_id):
        User = get_user_model()
        user = get_object_or_404(User, pk=user_id)

        # Активация аккаунта пользователя
        user.is_active = True
        user.save()
        return redirect('login')


class LoginView(BaseAuthView):
    """
    Представление для входа пользователей в систему.
    """
    template_name = 'news/login.html'

    def get(self, request):
        form = AuthenticationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('article_list')  # Перенаправление на список статей
        return render(request, self.template_name, {'form': form})




class ProfileView(LoginRequiredMixin, BaseAuthView):
    """
    Представление для просмотра и редактирования профиля пользователя.
    """
    template_name_view = 'news/profile.html'   # Шаблон для просмотра профиля
    template_name_edit = 'news/edit_profile.html'  # Шаблон для редактирования профиля

    def get(self, request):
        # Определяем, какую страницу отображать (просмотр или редактирование)
        is_edit = 'edit' in request.path

        # Проверяем группы пользователя
        is_premium = request.user.groups.filter(name='premium').exists()
        is_author = request.user.groups.filter(name='authors').exists()

        form = CustomUserChangeForm(instance=request.user)

        template_name = self.template_name_edit if is_edit else self.template_name_view
        return render(request, template_name, {
            'form': form,
            'is_premium': is_premium,
            'is_author': is_author,
        })

    def post(self, request):
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()

            # Обработка группы 'premium'
            account_type = request.POST.get('account_type', 'False')  # Значение из формы (True/False)
            if account_type == 'True':
                self.add_user_to_group(user, 'premium')
            else:
                self.remove_user_from_group(user, 'premium')

            # Обработка группы 'authors'
            is_author = request.POST.get('is_author', 'False')  # Значение из формы (True/False)
            if is_author == 'True':
                self.add_user_to_group(user, 'authors')
            else:
                self.remove_user_from_group(user, 'authors')

            return redirect('profile')  # Перенаправление обратно на страницу профиля
        return render(request, self.template_name_edit, {'form': form})





class ChangePasswordView(LoginRequiredMixin, BaseAuthView):
    """
    Представление для изменения пароля пользователя.
    """
    template_name = 'news/password_change_form.html'
    success_url = reverse_lazy('profile')

    def get(self, request):
        form = PasswordChangeForm(request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Обновление сессии для пользователя после смены пароля
            update_session_auth_hash(request, user)
            return redirect(self.success_url)
        return render(request, self.template_name, {'form': form})


class PermissionDeniedView(View):
    """
    Представление для отображения страницы с сообщением о запрете доступа.
    """
    template_name = 'news/permission_denied.html'

    def get(self, request):
        if not request.user.is_authenticated:
            # Пользователь не залогинен
            message = "Вы должны войти или зарегистрироваться"
            redirect_url = 'login'
        elif request.user.is_authenticated and not request.user.groups.filter(name='authors').exists():
            # Пользователь залогинен, но не является автором
            message = "Вы имеете только право на просмотр постов. Чтобы писать посты, смените тип пользователя на Author."
            redirect_url = 'profile'
        else:
            # Если страница открыта по ошибке, перенаправляем на главную
            return redirect('/')

        # Рендерим сообщение с URL для перенаправления
        return render(request, self.template_name, {'message': message, 'redirect_url': redirect_url})
