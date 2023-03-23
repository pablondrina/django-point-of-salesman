from django.contrib import admin
from salesman.core.utils import get_salesman_model


Basket = get_salesman_model('Basket')
BasketItem = get_salesman_model('BasketItem')


class BasketItemInline(admin.TabularInline):
    model = BasketItem
    extra = 0
    
    
@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    inlines = [BasketItemInline]
