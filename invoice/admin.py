from django.contrib import admin
from .models import Invoice , InvoiceItem , Product , PriceType

# Register your models here.


admin.site.register(Invoice)

admin.site.register(InvoiceItem)

admin.site.register(Product)

admin.site.register(PriceType)





