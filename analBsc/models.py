from django.db import models
import random
import string
import hashlib


class AddressInfo(models.Model):
    address = models.CharField(max_length=45, unique=True)
    value_buy = models.PositiveIntegerField()
    value_sold = models.PositiveIntegerField()
    value_FromStack = models.PositiveIntegerField()
    value_ToStack = models.PositiveIntegerField()
    dfxBalance = models.PositiveIntegerField()
    stDfxBalance = models.PositiveIntegerField()
    lpFarmingBalance = models.PositiveIntegerField()
    userDfxAmountFromStDFX = models.PositiveIntegerField()
    userDfxAmountFromCakeLP = models.PositiveIntegerField()
    sumOfDfxOfUser = models.PositiveIntegerField()


class Profile(models.Model):
    external_id = models.PositiveIntegerField(
        verbose_name='ID пользователя',
        null=True,
        blank=True
    )
    blockchain_address = models.CharField(
        verbose_name='Адрес Пользователя',
        unique=True,
        max_length=200,
        blank=False,
    )
    user_name = models.TextField(
        verbose_name='Имя пользователя',
        null=True,
        blank=True
    )
    disabled = models.BooleanField(
        verbose_name='Пользователь активен',
        default=True
    )
    password = models.CharField(
        max_length=150,
        unique=True
    )
    password_used = models.BooleanField(
        verbose_name='Пароль использован',
        default=False
    )
    sum_to_sell = models.PositiveIntegerField(
        verbose_name='Разрешенный лимит на продажу за отрезок времени',
        blank=True,
        null=True
    )
    start_selling = models.DateTimeField(
        verbose_name='Время начала продажи для клиента',
        blank=True,
        null=True
    )
    stop_selling = models.DateTimeField(
        verbose_name='Время конца продажи для клиента',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Профиль"

    def authorize(self, username: str, chat_id: int):
        self.user_name = username
        self.password_used = True
        self.external_id = chat_id
        self.save()
