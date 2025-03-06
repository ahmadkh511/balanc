from django.contrib import admin
from .models import Invoice , InvoiceItem , Product , PriceType , Shipping_com_m

# Register your models here.


admin.site.register(Invoice)

admin.site.register(InvoiceItem)

admin.site.register(Product)

admin.site.register(PriceType)

admin.site.register(Shipping_com_m)






