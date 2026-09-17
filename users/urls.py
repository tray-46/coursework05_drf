from django.urls import path

from users import views
from users.apps import UsersConfig

app_name = UsersConfig.name

urlpatterns = [
    path("users/register/", views.UserCreateAPIView.as_view(), name="user_register"),
    path("users/", views.UserListAPIView.as_view(), name="user_list"),
    path("users/<int:pk>/", views.UserRetrieveAPIView.as_view(), name="user_detail"),
    path("users/<int:pk>/update/", views.UserUpdateAPIView.as_view(), name="user_update"),
    path("users/<int:pk>/delete/", views.UserDestroyAPIView.as_view(), name="user_delete"),
    path("users/login/", views.TokenObtainPairView.as_view(), name="login"),
    path("users/token/refresh/", views.TokenRefreshView.as_view(), name="token_refresh"),
]
