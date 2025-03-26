from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
from rest_framework import routers

from api.views import RecipesViewSet, TagViewSet, UserViewSet

router = DefaultRouter()

router.register(r'tags', TagViewSet, basename='tag')
router.register(r'recipes', RecipesViewSet, basename='recipes')
router.register(r'users', UserViewSet, basename='users')



urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/', include('djoser.urls.authtoken')),
    path('api-token-auth/', views.obtain_auth_token)
]
