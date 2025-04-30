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


# forms.py
from django import forms
from django.contrib.auth.models import User
from .models import Sale

class SaleForm(forms.ModelForm):
    customer_name = forms.CharField(
        label='اسم العميل',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_customer_name'})
    )
    customer_phone = forms.CharField(
        label='رقم الهاتف',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    shipping_company = forms.CharField(
        label='شركة الشحن',
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    notes = forms.CharField(
        label='ملاحظات',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2})
    )
    invoice_date = forms.DateField(
        label='تاريخ الفاتورة',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

    class Meta:
        model = Sale
        fields = ['sale_payment_method', 'sale_currency', 'sale_status', 'sale_address']
        widgets = {
            'sale_payment_method': forms.Select(attrs={'class': 'form-control'}),
            'sale_currency': forms.Select(attrs={'class': 'form-control'}),
            'sale_status': forms.Select(attrs={'class': 'form-control'}),
            'sale_address': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_customer_name(self):
        name = self.cleaned_data['customer_name']
        try:
            user = User.objects.get(username=name)
            return user
        except User.DoesNotExist:
            raise forms.ValidationError("العميل غير موجود")

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.sale_customer = self.cleaned_data['customer_name']
        if commit:
            instance.save()
        return instance

# forms.py (تابع)

from .models import SaleItem
from django.forms import modelformset_factory

class SaleItemForm(forms.ModelForm):
    class Meta:
        model = SaleItem
        fields = ['sale_item_name', 'sale_quantity', 'sale_unit_price']
        widgets = {
            'sale_item_name': forms.TextInput(attrs={'class': 'form-control item-name-autocomplete'}),
            'sale_quantity': forms.NumberInput(attrs={'class': 'form-control quantity-input', 'step': 'any'}),  # إضافة class هنا
            'sale_unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
        }



SaleItemFormSet = modelformset_factory(
    SaleItem,
    form=SaleItemForm,
    extra=1,
    can_delete=True
)
