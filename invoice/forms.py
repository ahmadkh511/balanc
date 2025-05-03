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



class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = [
            'sale_date',
            'sale_customer',
            'sale_customer_phone',
            'sale_address',
            'sale_receiving_method',
            'sale_receiving_number',
            'sale_payment_method',
            'sale_notes',
            'sale_currency',
            'sale_invoice_date',
            'sale_type',
            'sale_status',
            'sale_due_date',
            'sale_global_discount',
            'sale_global_addition',
            'sale_global_tax',
        ]





class SaleItemForm(forms.ModelForm):
    class Meta:
        model = SaleItem
        fields = ['item_name', 'quantity', 'unit_price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # جلب جميع المنتجات وتخصيص عرضها في القائمة المنسدلة
        self.fields['item_name'].queryset = Product.objects.all()
        self.fields['item_name'].label_from_instance = lambda obj: obj.product_name

SaleItemFormSet = inlineformset_factory(
    Sale, SaleItem,
    form=SaleItemForm,
    extra=1,
    can_delete=True
)