from django.db import models
from django.utils.timezone import now


class Currency(models.Model):
    CURRENCY_CHOICES = (
        (1, 'USD'),
        (2, 'EUR'),
    )
    SOURCE_CHOICES = (
        (1, 'MONOBANK'),
        (2, 'VKURSE'),
        (3, 'YAHOO'),
    )
    currency = models.PositiveSmallIntegerField(choices=CURRENCY_CHOICES)
    source = models.PositiveSmallIntegerField(choices=SOURCE_CHOICES)
    buy = models.DecimalField(max_digits=6, decimal_places=2)
    sell = models.DecimalField(max_digits=6, decimal_places=2)

    created = models.DateField(auto_now_add=True)
    updated = models.DateField(default=now)

    def __str__(self):
        return str({
            'currency': self.currency,
            'source': self.source,
            'buy': self.buy,
            'sell': self.sell,
            'created': self.created,
            'updated': self.updated
        })
