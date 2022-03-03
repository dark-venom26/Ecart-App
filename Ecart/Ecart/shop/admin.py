from django.contrib import admin
from .models import OrderUpdate, Product, Contact, Order

# Register your models here.
admin.site.register(Product)
admin.site.register(Contact)
admin.site.register(Order)
admin.site.register(OrderUpdate)