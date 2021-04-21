from django.contrib import admin

from .models import Currency


class CurrencyAdmin(admin.ModelAdmin):
    list_display = ["currency", 'source', 'buy', 'sell', 'created', 'updated']
    search_fields = ['currency', 'source']

    class Meta:
        model = Currency


admin.site.register(Currency, CurrencyAdmin)
