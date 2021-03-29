from django.db import models


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
