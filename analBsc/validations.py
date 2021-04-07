from django.core.exceptions import ValidationError

from . import utils


def validate_binance_blockchain_address(address: str):
    try:
        utils.ping_address(address)
    except ValueError:
        raise ValidationError(
            f'{address} is invalid adress',
            params={'value': address},
        )
