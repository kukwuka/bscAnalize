from django.db import models
from django.contrib.auth.models import User

from . import validations


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
        validators=[validations.validate_binance_blockchain_address]
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
    coefficient = models.FloatField(
        verbose_name='Коэфициент пользователя',
        default= 1
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


class Admin(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True)
    external_id = models.PositiveIntegerField(
        verbose_name='ID пользователя',
        default=0
    )
    user_name = models.CharField(
        unique=True,
        max_length=200,
    )
