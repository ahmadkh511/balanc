from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from uuid import uuid4
from django.utils.text import slugify





class Invoice(models.Model):
    date = models.DateField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("العميل"))
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("رقم الهاتف"))
    address = models.TextField(blank=True, null=True, verbose_name=_("العنوان"))
    shipping_company = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("شركة الشحن"))
    shipping_num = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("رقم الشحنة"))
    payment_method = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("طريقة الدفع"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("ملاحظات"))
    currency = models.ForeignKey('Currency', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("العملة"))
    invoice_date = models.DateField(blank=True, null=True, verbose_name=_("تاريخ الفاتورة"))
    invoice_type = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("نوع الفاتورة"))
    status = models.ForeignKey('Status', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("حالة الفاتورة"))
    due_date = models.DateField(blank=True, null=True, verbose_name=_("تاريخ الاستحقاق"))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, verbose_name=_("المجموع الكلي"))

    # Utility fields
    uniqueId = models.CharField(null=True, blank=True, max_length=100, verbose_name=_("الرقم المسلسل"))
    slug = models.SlugField(max_length=225, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = _('فاتورة')
        verbose_name_plural = _('الفواتير')

    def __str__(self):
        return f'{self.customer.username if self.customer else "عميل غير معروف"} - {self.shipping_company}'

    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[1]
            self.slug = slugify(f'{self.customer.username if self.customer else "عميل غير معروف"} {self.uniqueId}')
        self.slug = slugify(f'{self.customer.username if self.customer else "عميل غير معروف"} {self.uniqueId}')
        self.last_updated = timezone.localtime(timezone.now())
        super(Invoice, self).save(*args, **kwargs)


class InvoiceItem(models.Model):
    invoice = models.ForeignKey('Invoice', on_delete=models.CASCADE, related_name='items', verbose_name=_("الفاتورة"))
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("المنتج"))
    product_name = models.CharField(max_length=255, verbose_name=_("اسم المنتج"))
    quantity = models.PositiveIntegerField(verbose_name=_("الكمية"))
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("سعر الوحدة"))
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name=_("الخصم"))
    addition = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name=_("الإضافة"))
    tax = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("الضريبة"))
    image = models.ImageField(upload_to='invoice_items/%y/%m/%d/', max_length=100 , blank=True, null=True, verbose_name=_("الصورة"))
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name=_("المجموع"))  # حقل جديد
    slug = models.SlugField(max_length=225, unique=True, blank=True, null=True, verbose_name=_("الرابط الفريد"))

    class Meta:
        verbose_name = _('عنصر الفاتورة')
        verbose_name_plural = _('عناصر الفواتير')

    def __str__(self):
        return f'{self.product_name} - {self.invoice.customer.username}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f'{self.product_name}-{uuid4().hex[:8]}')
        super().save(*args, **kwargs)





from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from uuid import uuid4
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

class Purchase(models.Model):
    date = models.DateField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))
    supplier = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("المورد"))
    supplier_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("رقم الهاتف"))
    purchase_address = models.TextField(blank=True, null=True, verbose_name=_("العنوان"))
    receiving_method = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("طريقة الاستلام"))
    receiving_number = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("رقم الاستلام"))
    payment_method = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("طريقة الدفع"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("ملاحظات"))
    currency = models.ForeignKey('Currency', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("العملة"))
    purchase_date = models.DateField(blank=True, null=True, verbose_name=_("تاريخ الشراء"))
    purchase_type = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("نوع الشراء"))
    status = models.ForeignKey('Status', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("حالة الفاتورة"))
    due_date = models.DateField(blank=True, null=True, verbose_name=_("تاريخ الاستحقاق"))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, verbose_name=_("المجموع الكلي"))

    # Utility fields
    uniqueId = models.CharField(null=True, blank=True, max_length=100, verbose_name=_("الرقم المسلسل"))
    slug = models.SlugField(max_length=225, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = _('فاتورة مشتريات')
        verbose_name_plural = _('فواتير المشتريات')

    def __str__(self):
        return f'{self.supplier.username if self.supplier else "مورد غير معروف"} - {self.receiving_method}'

    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[1]
            self.slug = slugify(f'{self.supplier.username if self.supplier else "مورد غير معروف"} {self.uniqueId}')
        self.slug = slugify(f'{self.supplier.username if self.supplier else "مورد غير معروف"} {self.uniqueId}')
        self.last_updated = timezone.localtime(timezone.now())
        super(Purchase, self).save(*args, **kwargs)

class PurchaseItem(models.Model):
    purchase = models.ForeignKey('Purchase', on_delete=models.CASCADE, related_name='items', verbose_name=_("فاتورة الشراء"))
    item_name = models.CharField(max_length=255, verbose_name=_("اسم الصنف"))
    barcode = models.ForeignKey('Barcode', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("الباركود"))
    quantity = models.PositiveIntegerField(verbose_name=_("الكمية"))
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("سعر الوحدة"))
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name=_("الخصم"))
    addition = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name=_("الإضافة"))
    tax = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("الضريبة"))
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name=_("المجموع"))

    class Meta:
        verbose_name = _('عنصر فاتورة الشراء')
        verbose_name_plural = _('عناصر فواتير الشراء')

    def __str__(self):
        return f'{self.item_name} - {self.purchase.supplier.username}'

class Barcode(models.Model):
    barcode = models.CharField(max_length=255, unique=True, verbose_name=_("الباركود"))
    notes = models.TextField(blank=True, verbose_name=_("ملاحظات"))

    class Meta:
        verbose_name = _('باركود')
        verbose_name_plural = _('الباركودات')

    def __str__(self):
        return self.barcode










































class Status(models.Model):
    status_types = models.CharField(max_length=255, verbose_name=_("حالة الفاتورة"))
    status_description = models.TextField(blank=True, null=True, verbose_name=_("الوصف"))

    # Utility fields
    uniqueId = models.UUIDField(default=uuid4, editable=False, unique=True, verbose_name=_("الرقم المسلسل"))
    slug = models.SlugField(max_length=225, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('حالة الفاتورة')
        verbose_name_plural = _('حالة الفوالفواتير')

    def __str__(self):
        return self.status_types

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f'{self.status_types} {self.uniqueId}')
        super(Status, self).save(*args, **kwargs)




class Product(models.Model):
    product_name = models.CharField(max_length=255, verbose_name=_("اسم المادة"))
    price_types = models.ManyToManyField('PriceType', verbose_name=_("أنواع الأسعار"))
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("سعر الشراء"))
    profit_rate = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("نسبة الربح"))
    tax = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("الضريبة"))
    barcode = models.CharField(max_length=100, unique=True, verbose_name=_("الباركود"))
    description = models.TextField(blank=True, null=True, verbose_name=_("الوصف"))

    # Utility fields
    uniqueId = models.UUIDField(default=uuid4, editable=False, unique=True, verbose_name=_("الرقم المسلسل"))
    slug = models.SlugField(max_length=225, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('مادة')
        verbose_name_plural = _('المواد')

    def __str__(self):
        return self.product_name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f'{self.product_name} {self.uniqueId}')
        super(Product, self).save(*args, **kwargs)



# Shipping Company
class Shipping_com_m(models.Model):
    shipping_company_name = models.CharField(max_length=255, blank=True)

    
    notes = models.TextField(blank=True)  

    # Utility fields
    uniqueId = models.UUIDField(default=uuid4, editable=False, unique=True, verbose_name=_("الرقم المسلسل"))
    slug = models.SlugField(max_length=225, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('شركة الشحن')
        verbose_name_plural = _('شركات الشحن')

    def __str__(self):
        return self.shipping_company_name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f'{self.shipping_company_name} {self.uniqueId}')
        super(Shipping_com_m, self).save(*args, **kwargs)



#PriceType
class PriceType(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("نوع السعر"))
    description = models.TextField(blank=True, null=True, verbose_name=_("الوصف"))

    class Meta:
        verbose_name = _('نوع السعر')
        verbose_name_plural = _('أنواع الأسعار')

    def __str__(self):
        return self.name
    


#Currency
class Currency(models.Model):
    currency_name = models.CharField(max_length=100, verbose_name=_(" العملة "))
    description = models.TextField(blank=True, null=True, verbose_name=_("البيان"))

    class Meta:
        verbose_name = _('العملة ')
        verbose_name_plural = _(' العملات')

    def __str__(self):
        return self.Currency_name
    

# payment_method
class Payment_method(models.Model):
    payment_method_name = models.CharField(max_length=255, blank=True)
    payment_method_notes = models.TextField(blank=True)  

    # Utility fields
    uniqueId = models.UUIDField(default=uuid4, editable=False, unique=True, verbose_name=_("الرقم المسلسل"))
    slug = models.SlugField(max_length=225, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _(' طريقة الدفع')
        verbose_name_plural = _(' طرق الدفع')

    def __str__(self):
        return self.payment_method_name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f'{self.payment_method_name} {self.uniqueId}')
        super(Payment_method, self).save(*args, **kwargs)