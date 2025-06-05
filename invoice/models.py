from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from uuid import uuid4
from django.utils.text import slugify
from django.db import models
from django.db.models import Q

from django.db import models

from django.db import models
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



#  START  PURCHASE  ============================



class Purchase(models.Model):
    date = models.DateField(verbose_name='التاريخ', editable=True)
    supplier = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("المورد"))
    supplier_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("رقم الهاتف"))
    purchase_address = models.TextField(blank=True, null=True, verbose_name=_("العنوان"))
    receiving_method = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("طريقة الاستلام"))
    receiving_number = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("رقم الاستلام"))
    payment_method = models.ForeignKey('Payment_method', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("طريقة الدفع"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("ملاحظات"))
    currency = models.ForeignKey('Currency', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("العملة"))
    purchase_date = models.DateField(blank=True, null=True, verbose_name=_("تاريخ الشراء"))
    purchase_type = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("نوع الشراء"))
    status = models.ForeignKey('Status', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("حالة الفاتورة"))
    due_date = models.DateField(blank=True, null=True, verbose_name=_("تاريخ الاستحقاق"))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, verbose_name=_("المجموع الكلي"))
    
    global_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_("الخصم العام"))
    global_addition = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_("الإضافة العامة"))
    global_tax = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name=_("الضريبة العامة (%)"))

    # Utility fields
    uniqueId = models.CharField(null=True, blank=True, max_length=100, verbose_name=_("الرقم المسلسل"))
    slug = models.SlugField(max_length=225, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"فاتورة شراء #{self.uniqueId or self.id} - {self.supplier}"
    
    def get_absolute_url(self):
        return reverse('purchase_detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = _("فاتورة شراء")
        verbose_name_plural = _("فواتير الشراء")
        
    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[1]
            self.slug = slugify(f'{self.supplier.username if self.supplier else "مورد غير معروف"} {self.uniqueId}')
        self.slug = slugify(f'{self.supplier.username if self.supplier else "مورد غير معروف"} {self.uniqueId}')
        self.last_updated = timezone.localtime(timezone.now())
        super(Purchase, self).save(*args, **kwargs)

    @property
    def subtotal(self):
        """المجموع الأساسي للسلع فقط (بدون ضريبة أو إضافات)"""
        return sum(item.total for item in self.items.all()) if hasattr(self, 'items') else 0

    @property
    def taxable_amount(self):
        """المبلغ الخاضع للضريبة (يساوي subtotal)"""
        return self.subtotal

    @property
    def tax_amount(self):
        """حساب الضريبة على المبلغ الخاضع فقط"""
        return (self.taxable_amount * (self.global_tax / 100)) if self.global_tax else 0

    @property
    def after_tax(self):
        """المجموع بعد الضريبة وقبل الخصم/الإضافة"""
        return self.taxable_amount + self.tax_amount

    @property
    def final_total(self):
        """المجموع النهائي بعد كل العمليات"""
        return self.after_tax + (self.global_addition or 0) - (self.global_discount or 0)

    def calculate_totals(self):
        """دالة محدثة لحساب جميع المجاميع"""
        self.total_amount = self.final_total
        self.save()

    @property
    def subtotal_after_discount(self):
        """يحسب المجموع بعد الخصم والإضافة"""
        return float(self.subtotal) + float(self.global_addition) - float(self.global_discount)



class PurchaseItemBarcode(models.Model):
    """جدول وسيط لإدارة علاقة Many-to-Many بين PurchaseItem و Barcode"""
    purchase_item = models.ForeignKey('PurchaseItem', on_delete=models.CASCADE, verbose_name=_("عنصر الشراء"))
    barcode = models.ForeignKey('Barcode', on_delete=models.CASCADE, verbose_name=_("الباركود"))
    is_primary = models.BooleanField(default=False, verbose_name=_("باركود رئيسي"))
    
    class Meta:
        verbose_name = _('علاقة باركود عنصر شراء')
        verbose_name_plural = _('علاقات باركود عناصر الشراء')
        unique_together = ('purchase_item', 'barcode')

    def __str__(self):
        return f"{self.purchase_item.item_name} - {self.barcode.barcode_in}"

    @classmethod
    def delete_all_by_purchase(cls, purchase_id):
        """دالة لحذف جميع الباركودات المرتبطة بالفاتورة"""
        cls.objects.filter(purchase_item__purchase__id=purchase_id).delete()


class PurchaseItem(models.Model):
    purchase = models.ForeignKey('Purchase', on_delete=models.CASCADE, related_name='items', verbose_name=_("فاتورة الشراء"))
    item_name = models.CharField(max_length=255, verbose_name=_("اسم الصنف"))
    quantity = models.PositiveIntegerField(verbose_name=_("الكمية"))
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("سعر الوحدة"))
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name=_("المجموع"))
    barcodes = models.ManyToManyField('Barcode', through='PurchaseItemBarcode', verbose_name=_("الباركودات"))
    image = models.ImageField(upload_to='invoice_items/%y/%m/%d/', max_length=100 , blank=True, null=True, verbose_name=_("الصورة"))
    
    class Meta:
        verbose_name = _('عنصر فاتورة الشراء')
        verbose_name_plural = _('عناصر فواتير الشراء')

    def __str__(self):
        return f'{self.item_name} - {self.purchase.supplier.username}'

    def save(self, *args, **kwargs):
        # حساب المجموع البسيط بدون خصم أو إضافة أو ضريبة
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        
    @property
    def primary_barcode(self):
        """الحصول على الباركود الرئيسي"""
        try:
            return self.purchaseitembarcode_set.get(is_primary=True).barcode
        except PurchaseItemBarcode.DoesNotExist:
            return None





class Barcode(models.Model):
    barcode_in = models.CharField(max_length=255,  verbose_name=_("الباركود الداخل"))
    barcode_out = models.CharField(max_length=255,  blank=True, null=True, verbose_name=_("الباركود الخارج"))
    suffix = models.CharField(max_length=10, blank=True, null=True, verbose_name=_("اللاحقة"))
    notes = models.TextField(blank=True, verbose_name=_("ملاحظات"))

    # الحقول المساعدة
    uniqueId = models.CharField(max_length=100, unique=True, blank=True, null=True, verbose_name=_("الرقم المسلسل"))
    slug = models.SlugField(max_length=225, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True, verbose_name=_("تاريخ الإنشاء"))
    last_updated = models.DateTimeField(auto_now=True, verbose_name=_("آخر تحديث"))

    class Meta:
        verbose_name = _('باركود')
        verbose_name_plural = _('الباركودات')

    def __str__(self):
        return self.barcode_in

    def save(self, *args, **kwargs):
        if self.barcode_out:
            if Barcode.objects.filter(Q(barcode_in=self.barcode_out) | Q(barcode_out=self.barcode_out)).exclude(pk=self.pk).exists():
                raise ValueError("الباركود الخارج لا يمكن أن يتطابق مع أي باركود داخلي أو خارجي آخر.")
        
        if not self.uniqueId:
            self.uniqueId = str(uuid4())
        
        if not self.slug:
            self.slug = slugify(f'barcode-{self.uniqueId}')
        
        super(Barcode, self).save(*args, **kwargs)


#SALE -----------------------------------------------
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
from uuid import uuid4
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.conf import settings # أضف هذا السطر

# استيراد مكتبة num2words
from num2words import num2words 

User = get_user_model()

class Sale(models.Model):
    sale_date = models.DateField(verbose_name='تاريخ البيع', editable=True)
    sale_customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("العميل"))
    sale_customer_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("رقم الهاتف"))
    sale_address = models.TextField(blank=True, null=True, verbose_name=_("العنوان"))
    sale_receiving_method = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("طريقة التسليم"))
    sale_receiving_number = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("رقم التسليم"))
    sale_payment_method = models.ForeignKey('Payment_method', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("طريقة الدفع"))
    sale_notes = models.TextField(blank=True, null=True, verbose_name=_("ملاحظات"))
    sale_currency = models.ForeignKey('Currency', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("العملة"))
    sale_invoice_date = models.DateField(blank=True, null=True, verbose_name=_("تاريخ الفاتورة"))
    sale_type = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("نوع الفاتورة"))
    sale_status = models.ForeignKey('Status', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("حالة الفاتورة"))
    sale_shipping_company = models.ForeignKey('Shipping_com_m', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("  شركة الشحن"))
    sale_shipping_num = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("رقم الشحنة"))
    sale_due_date = models.DateField(blank=True, null=True, verbose_name=_("تاريخ الاستحقاق"))
    sale_total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, verbose_name=_("المجموع الكلي"))
    sale_image = models.ImageField(upload_to='sale_image/%y/%m/%d/', max_length=100 , blank=True, null=True, verbose_name=_("صورة الفاتورة "))
    sale_global_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_("الخصم العام"))
    sale_global_addition = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name=_("الإضافة العامة"))
    sale_global_tax = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name=_("الضريبة العامة (%)"))

    # الحقل الجديد: لربط الفاتورة بالمستخدم (البائع) الذي أنشأها
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # يشير إلى نموذج المستخدم النشط (User المدمج لديك)
        on_delete=models.SET_NULL, # إذا حُذف المستخدم، يصبح الحقل NULL بدلاً من حذف الفاتورة
        null=True,                 # يمكن أن يكون هذا الحقل فارغًا في قاعدة البيانات
        blank=True,                # يمكن أن يكون فارغًا في الفورم
        related_name='created_sales', # اسم العلاقة العكسية: يسمح لك بالوصول إلى فواتير المستخدم من خلال user.created_sales.all()
        verbose_name=_("أنشئت بواسطة") # الاسم الظاهر في لوحة الإدارة
    )




    # Utility fields
    uniqueId = models.CharField(null=True, blank=True, max_length=100, verbose_name=_("الرقم المسلسل"))
    slug = models.SlugField(max_length=225, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"فاتورة بيع #{self.uniqueId or self.id} - {self.sale_customer}"

    def get_absolute_url(self):
        return reverse('sale_detail', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = _("فاتورة بيع")
        verbose_name_plural = _("فواتير البيع")
        permissions = [
            ("can_view_all_sales", "Can view all sales records") #الجزء الأول ("can_view_all_sales") هو codename (الاسم البرمجي) للإذن. هذا ما ستستخدمه في الكود (مثال: user.has_perm('sales.can_view_all_sales')).الجزء الثاني ("Can view all sales records") هو الاسم القابل للقراءة (verbose name) الذي سيظهر في لوحة إدارة Django.
        ]
        



    def save(self, *args, **kwargs):
        if self.date_created is None:
            self.date_created = timezone.localtime(timezone.now())
        if self.uniqueId is None:
            self.uniqueId = str(uuid4()).split('-')[1]
        self.slug = slugify(f'{self.sale_customer.username if self.sale_customer else "عميل غير معروف"} {self.uniqueId}')
        self.last_updated = timezone.localtime(timezone.now())
        super(Sale, self).save(*args, **kwargs)
        
    @property
    def sale_subtotal(self):
        """المجموع الفرعي لجميع بنود الفاتورة"""
        return sum(item.sale_total for item in self.items.all()) if hasattr(self, 'items') else 0
        

    @property
    def sale_taxable_amount(self):
        """المبلغ الخاضع للضريبة"""
        return self.sale_subtotal
    
    @property
    def sale_tax_amount(self):
        """قيمة الضريبة"""
        return (self.sale_taxable_amount * (self.sale_global_tax / 100)) if self.sale_global_tax else 0
    
    @property
    def sale_after_tax(self):
        """المبلغ بعد الضريبة"""
        return self.sale_taxable_amount + self.sale_tax_amount
    
    @property
    def sale_final_total(self):
        """الإجمالي النهائي بعد الخصم والإضافة"""
        return self.sale_after_tax + (self.sale_global_addition or 0) - (self.sale_global_discount or 0)
    
    def calculate_totals(self):
        """حساب جميع المجاميع وحفظها"""
        self.sale_total_amount = self.sale_final_total
        self.save()
    
    @property
    def sale_subtotal_after_discount(self):
        """المجموع الفرعي بعد الخصم والإضافة"""
        return float(self.sale_subtotal) + float(self.sale_global_addition) - float(self.sale_global_discount)

    @property
    def total_amount_in_words(self):
        """
        تحويل الإجمالي النهائي إلى كلمات عربية.
        تستخدم مكتبة num2words.
        """
        if self.sale_final_total is not None:
            try:
                # تحويل الرقم إلى عدد صحيح للتعامل معه بشكل أفضل مع num2words إذا لم تكن هناك كسور هامة
                # أو استخدمه كما هو إذا كانت num2words تدعم الكسور جيدًا
                # سنقوم بتحويله إلى float أولاً لضمان التوافق مع num2words
                amount_as_float = float(self.sale_final_total)

                # استخدام num2words مع اللغة العربية
                words = num2words(amount_as_float, lang='ar')

                # الحصول على اسم العملة، أو استخدام "ليرة سورية" كافتراضي
                # تأكد من أن نموذج Currency لديه حقل 'currency_name'
                currency_name = self.sale_currency.currency_name if self.sale_currency else "ليرة سورية"

                # تنسيق النص النهائي
                return f"{words} {currency_name} "
            except Exception as e:
                # لتسجيل الأخطاء في حال فشل التحويل (مهم جداً للتصحيح)
                print(f"Error converting sale_final_total to words for Sale ID {self.pk}: {e}")
                # في حالة الخطأ، أرجع نصًا فارغًا أو نصًا يفيد بالخطأ بدلاً من تعليق التطبيق
                return ""
        return ""


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    item_name = models.CharField(max_length=255, verbose_name=_("اسم المادة"))
    quantity = models.PositiveIntegerField(verbose_name=_("الكمية"))
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("السعر"))
    notes = models.TextField(blank=True, null=True, verbose_name=_("ملاحظات"))
    barcodes = models.JSONField(blank=True, null=True, verbose_name=_("الباركودات"))
    sale_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, verbose_name=_("إجمالي البند"))
    sale_item_image = models.ImageField(upload_to='sale_items_image/%y/%m/%d/', max_length=100 , blank=True, null=True, verbose_name=_("صورة المادة "))
    class Meta:
        verbose_name = _("بند الفاتورة")
        verbose_name_plural = _("بنود الفاتورة")

    def save(self, *args, **kwargs):
        # حساب الإجمالي تلقائيًا قبل الحفظ
        self.sale_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item_name} - {self.quantity} × {self.unit_price} = {self.sale_total}"



class SaleItemBarcode(models.Model):
    sale_item = models.ForeignKey('SaleItem', on_delete=models.CASCADE)
    barcode = models.ForeignKey('Barcode', on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False, verbose_name="باركود رئيسي")

    class Meta:
        unique_together = ('sale_item', 'barcode')

    def __str__(self):
        return f"{self.sale_item.product.product_name} - {self.barcode.barcode_out}"




class Product(models.Model):
    product_name = models.CharField(max_length=255, verbose_name=_("اسم المادة"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("سعر البيع"), default=0)
    price_types = models.ManyToManyField('PriceType', verbose_name=_("أنواع الأسعار"), blank=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("سعر الشراء"), default=0)
    profit_rate = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("نسبة الربح"), default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("الضريبة"), default=0)
    barcode = models.CharField(max_length=100, unique=True, verbose_name=_("الباركود"), blank=True, null=True)
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

    def get_price(self):
        """حساب سعر البيع بناء على سعر الشراء ونسبة الربح"""
        if self.price and self.price > 0:
            return self.price
        return self.purchase_price * (1 + (self.profit_rate / 100))








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
        verbose_name_plural = _('حالات الفواتير')

    def __str__(self):
        return self.status_types

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f'{self.status_types} {self.uniqueId}')
        super(Status, self).save(*args, **kwargs)


# Shipping Company
class Shipping_com_m(models.Model):
    shipping_company_name = models.CharField(max_length=255, blank=True , verbose_name=_(" شركة الشحن "))

    notes = models.TextField(blank=True , verbose_name=_(" العملة "))  

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


#Currency
class Currency(models.Model):
    currency_name = models.CharField(max_length=100, verbose_name=_("العملة"))
    description = models.TextField(blank=True, null=True, verbose_name=_("البيان"))

    class Meta:
        verbose_name = _('العملة')
        verbose_name_plural = _('العملات')

    def __str__(self):
        return self.currency_name
    






# payment_method
class Payment_method(models.Model):
    payment_method_name = models.CharField(max_length=255, blank=True, verbose_name=_("طريقة الدفع"))
    payment_method_notes = models.TextField(blank=True, verbose_name=_("البيان"))  

    # Utility fields
    uniqueId = models.UUIDField(default=uuid4, editable=False, unique=True, verbose_name=_("الرقم المسلسل"))
    slug = models.SlugField(max_length=225, unique=True, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('طريقة الدفع')
        verbose_name_plural = _('طرق الدفع')

    def __str__(self):
        return self.payment_method_name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f'{self.payment_method_name} {self.uniqueId}')
        super(Payment_method, self).save(*args, **kwargs)




#PriceType
class PriceType(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("نوع السعر"))
    description = models.TextField(blank=True, null=True, verbose_name=_("الوصف"))

    class Meta:
        verbose_name = _('نوع السعر')
        verbose_name_plural = _('أنواع الأسعار')

    def __str__(self):
        return self.name
    
