from django.contrib import admin

from .models import Follow, MyUser


@admin.register(MyUser)
class MyUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email')
    search_fields = ('email', 'username')


@admin.register(Follow)
class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = ['user', 'following']