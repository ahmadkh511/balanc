from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView , TemplateView
from django.urls import reverse_lazy
from .models import Invoice, InvoiceItem, PriceType , Product


from django.views.generic import View










class HomeView(TemplateView):
    template_name = 'home.html'

# invoice/views.py

class InvoiceListView(ListView):
    model = Invoice
    template_name = 'invoice_list.html'
    context_object_name = 'invoices'



from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import User
from .models import Invoice, InvoiceItem
import json

class InvoiceCreateView(View):
    template_name = 'invoice/invoice_form.html'

    def get(self, request, *args, **kwargs):
        # تمرير قائمة المستخدمين إلى القالب
        users = User.objects.all()
        return render(request, self.template_name, {'users': users})

    def post(self, request, *args, **kwargs):
        # حفظ بيانات الفاتورة
        invoice = Invoice.objects.create(
            date=request.POST.get('date'),
            customer_id=request.POST.get('customer_id'),  # استخدام customer_id بدلًا من customer
            phone_number=request.POST.get('phone_number'),
            address=request.POST.get('address'),
            shipping_company=request.POST.get('shipping_company'),
            shipping_num=request.POST.get('shipping_num'),
            payment_method=request.POST.get('payment_method'),
            currency=request.POST.get('currency'),
        )

        # معالجة عناصر الفاتورة
        item_counter = 0
        while True:
            product_name = request.POST.get(f'product_name_{item_counter}')
            if not product_name:
                break  # توقف إذا لم يكن هناك المزيد من العناصر

            quantity = request.POST.get(f'quantity_{item_counter}')
            unit_price = request.POST.get(f'unit_price_{item_counter}')
            discount = request.POST.get(f'discount_{item_counter}')
            addition = request.POST.get(f'addition_{item_counter}')
            tax = request.POST.get(f'tax_{item_counter}')
            image = request.FILES.get(f'image_{item_counter}')  # الصورة (إذا تم تحميلها)

            # حفظ عنصر الفاتورة
            InvoiceItem.objects.create(
                invoice=invoice,
                product_name=product_name,
                quantity=quantity,
                unit_price=unit_price,
                discount=discount,
                addition=addition,
                tax=tax,
                image=image,  # حفظ الصورة
            )

            item_counter += 1

        return redirect('invoice_list')
    
from django.http import JsonResponse
from django.contrib.auth.models import User

def autocomplete_customers(request):
    query = request.GET.get('term', '')  # الحصول على النص الذي كتبه المستخدم
    customers = User.objects.filter(username__icontains=query)  # البحث عن العملاء المطابقين
    results = [{'id': customer.id, 'label': customer.username} for customer in customers]  # تحضير النتائج
    return JsonResponse(results, safe=False)  # إرجاع النتائج كـ JSON






















class InvoiceUpdateView(UpdateView):
    model = Invoice
    template_name = 'invoice_form.html'
    fields = '__all__'
    success_url = reverse_lazy('invoice_list')


class InvoiceDeleteView(DeleteView):
    model = Invoice
    template_name = 'invoice_confirm_delete.html'
    success_url = reverse_lazy('invoice_list')


class InvoiceDetailView(DetailView):
    model = Invoice
    template_name = 'invoice/invoice_detail.html'
    context_object_name = 'invoice'


class InvoiceItemCreateView(CreateView):
    model = InvoiceItem
    template_name = 'invoiceitem_form.html'
    fields = '__all__'
    success_url = reverse_lazy('invoice_list')


class InvoiceItemUpdateView(UpdateView):
    model = InvoiceItem
    template_name = 'invoiceitem_form.html'
    fields = '__all__'
    success_url = reverse_lazy('invoice_list')


class InvoiceItemDeleteView(DeleteView):
    model = InvoiceItem
    template_name = 'invoiceitem_confirm_delete.html'
    success_url = reverse_lazy('invoice_list')



from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from .models import Product, PriceType
from .forms import ProductForm, PriceTypeForm

# Product Views
class ProductListView(ListView):
    model = Product
    template_name = 'invoice/product_list.html'
    context_object_name = 'products'

class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm  # استخدام النموذج (Form)
    template_name = 'invoice/product_form.html'
    success_url = reverse_lazy('product_list')

class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm  # استخدام النموذج (Form)
    template_name = 'invoice/product_form.html'
    success_url = reverse_lazy('product_list')

class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'invoice/product_confirm_delete.html'
    success_url = reverse_lazy('product_list')

class ProductDetailView(DetailView):
    model = Product
    template_name = 'invoice/product_detail.html'
    context_object_name = 'product'

# PriceType Views
class PriceTypeListView(ListView):
    model = PriceType
    template_name = 'invoice/pricetype_list.html'
    context_object_name = 'pricetypes'

class PriceTypeCreateView(CreateView):
    model = PriceType
    form_class = PriceTypeForm  # استخدام النموذج (Form)
    template_name = 'invoice/pricetype_form.html'
    success_url = reverse_lazy('pricetype_list')

class PriceTypeUpdateView(UpdateView):
    model = PriceType
    form_class = PriceTypeForm  # استخدام النموذج (Form)
    template_name = 'invoice/pricetype_form.html'
    success_url = reverse_lazy('pricetype_list')

class PriceTypeDeleteView(DeleteView):
    model = PriceType
    template_name = 'invoice/pricetype_confirm_delete.html'
    success_url = reverse_lazy('pricetype_list')