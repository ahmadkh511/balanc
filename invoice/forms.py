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


class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = ['status_types', 'status_description']


class ShippingForm(forms.ModelForm):
    class Meta:
        model = Shipping_com_m
        fields = ['shipping_company_name', 'notes']


class PriceTypeForm(forms.ModelForm):
    class Meta:
        model = PriceType
        fields = ['name', 'description']  


class CurrencyForm(forms.ModelForm):
    class Meta:
        model = Currency
        fields = ['currency_name', 'description']  


class BarcodeForm(forms.ModelForm):
    class Meta:
        model = Barcode
        fields = ['barcode_in', 'barcode_out' , 'notes'  ]  


class payment_methodForm(forms.ModelForm):
    class Meta:
        model = Payment_method
        fields = ['payment_method_name', 'payment_method_notes'  ]  





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


class SaleForm(forms.ModelForm):
    """نموذج فاتورة المبيعات"""
    class Meta:
        model = Sale
        fields = ['sale_date', 'sale_customer', 'sale_customer_phone', 'sale_address', 
                 'sale_status', 'sale_payment_method', 'sale_currency', 
                 'sale_shipping_company', 'sale_shipping_num', 'sale_notes', 
                 'sale_global_discount', 'sale_global_addition', 'sale_global_tax', 
                 'sale_total_amount']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sale_date'].widget = forms.DateInput(attrs={'type': 'date'})
        self.fields['sale_customer'].widget = forms.HiddenInput()
        self.fields['sale_status'].required = False
        self.fields['sale_shipping_company'].required = False
        self.fields['sale_shipping_num'].required = False
        self.fields['sale_global_discount'].initial = 0
        self.fields['sale_global_addition'].initial = 0
        self.fields['sale_global_tax'].initial = 0
        self.fields['sale_total_amount'].initial = 0

class SaleItemForm(forms.ModelForm):
    """نموذج عنصر فاتورة المبيعات"""
    sale_item_image = forms.ImageField(
        required=False, 
        label='صورة المادة',
        widget=forms.FileInput(attrs={
            'accept': 'image/*',
            'class': 'form-control item-image'
        })
    )
    
    class Meta:
        model = SaleItem
        fields = ['item_name', 'quantity', 'unit_price', 'notes', 'sale_item_image', 'barcodes']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['item_name'].widget = forms.HiddenInput()
        self.fields['barcodes'].widget = forms.HiddenInput()
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

SaleItemFormSet = forms.inlineformset_factory(
    Sale, SaleItem,
    form=SaleItemForm,
    extra=0,
    can_delete=True
)
