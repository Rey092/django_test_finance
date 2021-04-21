from decimal import Decimal

from celery import shared_task
import requests
from requests.exceptions import HTTPError


@shared_task
def parse_monobank():
    from .models import Currency # noqa
    url = 'https://api.monobank.ua/bank/currency'

    try:
        response = requests.get(url)
        response.raise_for_status()
    except HTTPError as http_err:
        # TODO: log http_error
        raise http_err
    except Exception as err:
        # TODO: log err
        raise err

    cr_iso4217 = {
        'USD': 840,
        'UAH': 980,
    }
    currency = 1
    source = 1

    currency_last = Currency.objects.filter(currency=currency, source=source).last()
    data = response.json()

    for row in data:
        # codeA should be 'USD' and codeB should be 'UAH'. codes by ISO-4217.
        if row["currencyCodeA"] == cr_iso4217["USD"] and row["currencyCodeB"] == cr_iso4217["UAH"]:

            buy = round(Decimal(row['rateBuy']), 2)
            sell = round(Decimal(row['rateSell']), 2)

            if currency_last is None or (currency_last.buy != buy and currency_last.sell != sell):
                Currency(currency=currency, source=source, buy=buy, sell=sell).save()
