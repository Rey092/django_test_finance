from decimal import Decimal

from celery import shared_task
from django.utils.datetime_safe import datetime
import requests
from requests.exceptions import HTTPError
from yahoofinancials import YahooFinancials


@shared_task
def parse_monobank():
    from .models import Currency  # noqa
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


@shared_task
def parse_vkurse():
    from .models import Currency  # noqa
    url = 'http://vkurse.dp.ua/course.json'

    try:
        response = requests.get(url)
        response.raise_for_status()
    except HTTPError as http_err:
        # TODO: log http_error
        raise http_err
    except Exception as err:
        # TODO: log err
        raise err

    currency_map = {
        'Dollar': 1,
        'Euro': 2,
    }

    source = 2

    data = response.json()

    for curr_key, curr_values in data.items():

        if curr_key in currency_map:

            currency = currency_map[curr_key]
            currency_last = Currency.objects.filter(currency=currency, source=source).last()

            buy = round(Decimal(curr_values['buy']), 2)
            sell = round(Decimal(curr_values['sale']), 2)

            if currency_last is None or (currency_last.buy != buy and currency_last.sell != sell):
                Currency(currency=currency, source=source, buy=buy, sell=sell).save()


@shared_task
def parse_yahoo():
    from .models import Currency  # noqa
    currencies = ['USDUAH=X']
    yahoo_financials_currencies = YahooFinancials(currencies)
    today = datetime.now().strftime("%Y-%m-%d")

    try:
        usd_course = \
            yahoo_financials_currencies.get_historical_price_data(today, today, "daily")['USDUAH=X']['prices'][0][
                'close']
    except HTTPError as http_err:
        # TODO: log http_error
        raise http_err
    except Exception as err:
        # TODO: log err
        raise err

    currency = 1
    source = 3
    buy = round(Decimal(usd_course), 2)
    sell = buy

    currency_last = Currency.objects.filter(currency=currency, source=source).last()

    if currency_last is None or (currency_last.buy != buy and currency_last.sell != sell):
        Currency(currency=currency, source=source, buy=buy, sell=sell).save()
