from django import forms
from .models import InvoiceItem, Product, PriceType , Shipping_com_m , Currency , Status , Barcode , Payment_method

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

