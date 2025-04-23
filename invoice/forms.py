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
