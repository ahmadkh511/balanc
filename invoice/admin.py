from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Invoice, InvoiceItem, Product, PriceType, Shipping_com_m , Status , Currency ,Payment_method , Barcode



# تعريف InvoiceResource
class InvoiceResource(resources.ModelResource):
    class Meta:
        model = Invoice

# تسجيل Invoice باستخدام الديكوراتور
@admin.register(Invoice)
class InvoiceAdmin(ImportExportModelAdmin):
    resource_class = InvoiceResource

# تعريف InvoiceItemResource
class InvoiceItemResource(resources.ModelResource):
    class Meta:
        model = InvoiceItem

# تسجيل InvoiceItem باستخدام الديكوراتور
@admin.register(InvoiceItem)
class InvoiceItemAdmin(ImportExportModelAdmin):
    resource_class = InvoiceItemResource



@admin.register(Barcode)
class BarcodeAdmin(admin.ModelAdmin):
    list_display = ('barcode', 'notes')

# تسجيل النماذج الأخرى
admin.site.register(Product)
admin.site.register(PriceType)
admin.site.register(Shipping_com_m)
admin.site.register(Status)
admin.site.register(Currency)
admin.site.register(Payment_method)