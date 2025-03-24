from django.contrib.auth.models import AbstractUser
from django.db import models


class MyUser(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Уникальный юзернейм'
    )
    first_name = models.CharField(max_length=150, unique=True, verbose_name='Имя')
    last_name = models.CharField(max_length=150, unique=True, verbose_name='Фамилия')
    email = models.EmailField(max_length=254, unique=True, verbose_name='Адрес электронной почты')
    password = models.CharField(max_length=100, verbose_name='Пароль')
    avatar = models.ImageField(verbose_name='Ссылка на аватар',
                               upload_to='avatars',
                               blank=False,
                               default='/frontend/build/static/media/userpic-icon.2e3faa821bb5398be2c6.jpg'
                               )
    is_subscribed = models.BooleanField(blank=False, verbose_name='Подписан ли текущий пользователь на этого')


    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Subscriptions(models.Model):
    author = models.ForeignKey(MyUser,
                               verbose_name='Автор рецепта',
                               on_delete=models.CASCADE,
                               related_name='subscriptions'
                            )
    subscription = models.ForeignKey(MyUser,
                                    verbose_name='Подписчик',
                                    on_delete=models.CASCADE,
                                    related_name='subscription'
                                )

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'

    def __str__(self):
        return f'{self.subscription} подписался на {self.author}'