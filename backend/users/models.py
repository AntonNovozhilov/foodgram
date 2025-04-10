from django.contrib.auth.models import AbstractUser
from django.db import models



class MyUser(AbstractUser):
    username = models.CharField(max_length=150, unique=True, verbose_name='Уникальный юзернейм')
    first_name = models.CharField(max_length=150, verbose_name='Имя')
    last_name = models.CharField(max_length=150, verbose_name='Фамилия')
    email = models.EmailField(max_length=254, unique=True, verbose_name='Адрес электронной почты')
    avarat = models.ImageField(upload_to='avatar/', blank=True, null=True, verbose_name='Аватар')
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username}'
        
class Follow(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='follows')
    following = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='followers')

    class Meta:
        unique_together = ('user', 'following')
