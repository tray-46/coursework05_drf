from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    """
    Represent a service user
    """

    email = models.EmailField(unique=True, verbose_name="Почта", help_text="Укажите почту")
    telegram_chat_id = models.CharField(
        max_length=32, null=True, blank=True, verbose_name="Chat_id пользователя телеграм"
    )

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
