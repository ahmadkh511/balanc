from django import forms
from .models import(

InvoiceItem, Product, PriceType , Shipping_com_m , Currency ,
Status , Barcode , Payment_method , Purchase
)


class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['product_name', 'quantity', 'unit_price', 'discount', 'addition', 'tax', 'image']



class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'price_types', 'purchase_price', 'profit_rate', 'tax', 'barcode', 'description']
        widgets = {
            'price_types': forms.CheckboxSelectMultiple,  # استخدام CheckboxSelectMultiple لأنواع الأسعار
        }


from django import forms
from django.core.exceptions import ValidationError
from .models import Status

class StatusForm(forms.ModelForm):
    """
    Form for creating and updating invoice statuses with validation
    """
    class Meta:
        model = Status
        fields = ['status_types', 'status_description']
        widgets = {
            'status_types': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل نوع حالة الفاتورة'
            }),
            'status_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'أدخل وصفاً لحالة الفاتورة (اختياري)'
            }),
        }
        labels = {
            'status_types': 'نوع الحالة',
            'status_description': 'الوصف'
        }
        help_texts = {
            'status_types': 'أدخل اسم حالة الفاتورة (مثال: مدفوعة، معلقة، إلخ)',
            'status_description': 'وصف مفصل لحالة الفاتورة (اختياري)'
        }

    def clean_status_types(self):
        """
        Validate that status type is unique (case insensitive)
        """
        status_types = self.cleaned_data.get('status_types')
        queryset = Status.objects.filter(status_types__iexact=status_types)
        
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
            
        if queryset.exists():
            raise ValidationError('حالة الفاتورة هذه مسجلة مسبقاً')
            
        return status_types

    def clean(self):
        """
        Additional form-wide validation
        """
        cleaned_data = super().clean()
        # Add any additional validation logic here
        return cleaned_data



from django import forms
from django.core.exceptions import ValidationError
from .models import Shipping_com_m


class ShippingForm(forms.ModelForm):
    """
    Form for creating and updating shipping companies with validation
    """
    class Meta:
        model = Shipping_com_m
        fields = ['shipping_company_name', 'notes']
        widgets = {
            'shipping_company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل اسم شركة الشحن'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'أدخل أي ملاحظات (اختياري)'
            }),
        }
        labels = {
            'shipping_company_name': 'اسم الشركة',
            'notes': 'ملاحظات'
        }
        help_texts = {
            'shipping_company_name': 'يجب أن يكون الاسم أكثر من حرفين',
            'notes': 'أي معلومات إضافية عن شركة الشحن'
        }

    def clean_shipping_company_name(self):
        """
        Validate that shipping company name is unique (case insensitive)
        and has minimum length
        """
        name = self.cleaned_data.get('shipping_company_name')
        
        if len(name) < 3:
            raise ValidationError('يجب أن يكون اسم الشركة أكثر من حرفين')
            
        queryset = Shipping_com_m.objects.filter(shipping_company_name__iexact=name)
        
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
            
        if queryset.exists():
            raise ValidationError('شركة الشحن هذه مسجلة مسبقاً')
            
        return name

    def clean(self):
        """
        Additional form-wide validation
        """
        cleaned_data = super().clean()
        # Add any additional validation logic here
        return cleaned_data



class PriceTypeForm(forms.ModelForm):
    class Meta:
        model = PriceType
        fields = ['name', 'description']  



class CurrencyForm(forms.ModelForm):
    """نموذج العملة مع تحسينات وخصائص إضافية"""
    currency_name = forms.CharField(
        label='اسم العملة',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل اسم العملة'
        }),
        max_length=100,
        required=True
    )
    
    description = forms.CharField(
        label='الوصف',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'أدخل وصفاً للعملة (اختياري)'
        }),
        required=False
    )

    class Meta:
        model = Currency
        fields = ['currency_name', 'description']
        error_messages = {
            'currency_name': {
                'required': 'اسم العملة مطلوب',
                'max_length': 'يجب ألا يتجاوز اسم العملة 100 حرف'
            }
        }

    def clean_currency_name(self):
        """تنظيف وتحقق إضافي لاسم العملة"""
        currency_name = self.cleaned_data.get('currency_name')
        if not currency_name:
            raise forms.ValidationError("اسم العملة مطلوب")
        return currency_name.strip()  # إزالة المسافات الزائدة





class BarcodeForm(forms.ModelForm):
    class Meta:
        model = Barcode
        fields = ['barcode_in', 'barcode_out' , 'notes'  ]  



from django import forms
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.http import JsonResponse
from .models import Payment_method

class payment_methodForm(forms.ModelForm):
    class Meta:
        model = Payment_method
        fields = ['payment_method_name', 'payment_method_notes']
        widgets = {
            'payment_method_name': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'payment_method_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            })
        }




class PurchaseItemForm(forms.Form):
    item_name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'اسم الصنف'
        })
    )
    quantity = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'placeholder': 'الكمية'
        })
    )
    unit_price = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': 'سعر الوحدة'
        })
    )

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', '')
        super().__init__(*args, **kwargs)
        
        # تعيين IDs فريدة للحقول
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['id'] = f'id_{prefix}{field_name}'







# تحويل  الفيو للمشتريات الى      طريقة الفورم



class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = [
            'date', 'supplier', 'supplier_phone', 'purchase_address',
            'receiving_method', 'receiving_number', 'payment_method', 'notes',
            'currency', 'purchase_date', 'purchase_type', 'status', 'due_date',
            'global_discount', 'global_addition', 'global_tax'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget.attrs['readonly'] = True  # جعل التاريخ غير قابل للتعديل
        self.fields['date'].widget.attrs['class'] = 'form-control'





#  SALE ------------------------



from django import forms
from django.contrib.auth.models import User
from .models import Sale
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django import forms
from django.contrib import messages
from django.shortcuts import redirect
from django.http import JsonResponse
from django.db.models import Sum
from django.utils import timezone
from .models import Sale, SaleItem, Product, User
from django.forms import inlineformset_factory


from django import forms
from django.forms import inlineformset_factory
from django.db.models import Q
from django.contrib.auth import get_user_model
from .models import Sale, SaleItem, Product

User = get_user_model()
from django import forms
from django.forms import inlineformset_factory
from .models import Sale, SaleItem
# forms.py
from django import forms
from .models import Sale, SaleItem, Product

from django import forms
from .models import Sale, SaleItem, Product

from django import forms
from .models import Sale, SaleItem, Product

from django import forms
from .models import Sale


# تعريفات الفورم
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from .models import Sale, SaleItem, User

class FileUploadSecurity:
    """كلاس مسؤول عن التحقق الأمني للملفات المرفوعة"""
    ALLOWED_MIME_TYPES = ['image/jpeg', 'image/png', 'image/webp']
    MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB

    @classmethod
    def validate_file(cls, uploaded_file):
        """التحقق الأساسي من الملف"""
        if uploaded_file.size > cls.MAX_FILE_SIZE:
            raise ValidationError(f"حجم الملف يتجاوز الحد المسموح ({cls.MAX_FILE_SIZE/1024/1024}MB)")
        
        ext = uploaded_file.name.split('.')[-1].lower()
        if ext not in ['jpg', 'jpeg', 'png', 'webp']:
            raise ValidationError("نوع الملف غير مسموح به")

class SaleForm(forms.ModelForm):
    """نموذج فاتورة المبيعات مع التحسينات الأمنية"""
    class Meta:
        model = Sale
        fields = ['sale_date', 'sale_customer', 'sale_customer_phone', 
                 'sale_address', 'sale_status', 'sale_payment_method',
                 'sale_currency', 'sale_shipping_company', 'sale_shipping_num',
                 'sale_notes', 'sale_global_discount', 'sale_global_addition',
                 'sale_global_tax', 'sale_total_amount']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sale_date'].widget = forms.DateInput(attrs={'type': 'date'})
        self.fields['sale_customer'].widget = forms.HiddenInput()
        self.fields['sale_status'].required = False
        self.fields['sale_shipping_company'].required = False
        self.fields['sale_shipping_num'].required = False
        
        # تعيين القيم الافتراضية
        for field in ['sale_global_discount', 'sale_global_addition', 
                     'sale_global_tax', 'sale_total_amount']:
            self.fields[field].initial = 0

    def clean_sale_customer(self):
        """التحقق من صحة العميل"""
        customer = self.cleaned_data.get('sale_customer')
        if not customer:
            raise ValidationError("يجب اختيار عميل صحيح")
        return customer

    def clean_sale_global_discount(self):
        """التحقق من أن الخصم غير سالب"""
        discount = self.cleaned_data.get('sale_global_discount', 0)
        if discount < 0:
            raise ValidationError("قيمة الخصم لا يمكن أن تكون سالبة")
        return discount

    def clean_sale_global_addition(self):
        """التحقق من أن الإضافة غير سالبة"""
        addition = self.cleaned_data.get('sale_global_addition', 0)
        if addition < 0:
            raise ValidationError("قيمة الإضافة لا يمكن أن تكون سالبة")
        return addition

    def clean_sale_global_tax(self):
        """التحقق من أن الضريبة بين 0 و 100"""
        tax = self.cleaned_data.get('sale_global_tax', 0)
        if not (0 <= tax <= 100):
            raise ValidationError("قيمة الضريبة يجب أن تكون بين 0 و 100")
        return tax

class SaleItemForm(forms.ModelForm):
    """نموذج عناصر الفاتورة مع التحسينات الأمنية"""
    sale_item_image = forms.ImageField(
        required=False,
        validators=[FileExtensionValidator(
            allowed_extensions=['jpg', 'jpeg', 'png', 'webp'],
            message="يُسمح فقط بملفات الصور من نوع JPG, PNG أو WEBP"
        )],
        widget=forms.FileInput(attrs={
            'accept': 'image/*',
            'class': 'form-control item-image'
        })
    )

    class Meta:
        model = SaleItem
        fields = ['item_name', 'quantity', 'unit_price', 
                 'notes', 'sale_item_image', 'barcodes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['item_name'].widget = forms.HiddenInput()
        self.fields['barcodes'].widget = forms.HiddenInput()
        
        # إعدادات واجهة المستخدم
        self.fields['quantity'].widget.attrs.update({
            'min': '1',
            'class': 'form-control quantity'
        })
        self.fields['unit_price'].widget.attrs.update({
            'min': '0',
            'step': '0.01',
            'class': 'form-control unit-price'
        })
        self.fields['notes'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'ملاحظات'
        })

    def clean_item_name(self):
        """التحقق من أن اسم المادة غير فارغ"""
        name = self.cleaned_data.get('item_name')
        if not name:
            raise ValidationError("يجب إدخال اسم المادة")
        return name

    def clean_quantity(self):
        """التحقق من أن الكمية أكبر من الصفر"""
        qty = self.cleaned_data.get('quantity', 1)
        if qty <= 0:
            raise ValidationError("يجب أن تكون الكمية أكبر من الصفر")
        return qty

    def clean_unit_price(self):
        """التحقق من أن السعر غير سالب"""
        price = self.cleaned_data.get('unit_price', 0)
        if price < 0:
            raise ValidationError("يجب أن يكون السعر قيمة موجبة")
        return price

    def clean_sale_item_image(self):
        """التحقق الأمني من الصورة المرفوعة"""
        image = self.cleaned_data.get('sale_item_image')
        if image:
            try:
                FileUploadSecurity.validate_file(image)
            except ValidationError as e:
                raise ValidationError(str(e))
        return image

# تعريف FormSet
SaleItemFormSet = forms.inlineformset_factory(
    Sale,
    SaleItem,
    form=SaleItemForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)







































