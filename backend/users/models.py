from django.contrib.auth.models import AbstractUser
from django.db import models


class MyUser(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Никнейм пользователя'
    )
    first_name = models.CharField(max_length=150, unique=True, verbose_name='Имя пользователя')
    last_name = models.CharField(max_length=150, unique=True, verbose_name='Фамилия пользователя')
    email = models.EmailField(max_length=256, unique=True, verbose_name='Почта пользователя')
    password = models.CharField(max_length=100, unique=True, verbose_name='Пароль пользователя')
    avatar = models.ImageField(verbose_name='Аватар пользователя',
                               upload_to='avatars',
                               blank=False
                               )


    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'