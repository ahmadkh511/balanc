from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView , TemplateView
from django.urls import reverse_lazy
from .models import Invoice, InvoiceItem, PriceType , Product , Shipping_com_m , Currency , User , Status
from django.views.generic import View
from django.views import View
from django.http import JsonResponse
from .forms import ProductForm, PriceTypeForm , ShippingForm , CurrencyForm , StatusForm
import json
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Sum


class HomeView(TemplateView):
    template_name = 'home.html'


class InvoiceListView(ListView):
    model = Invoice
    template_name = 'invoice/invoice_list.html'
    context_object_name = 'invoices'
    paginate_by = 4  # عرض 4 فواتير في كل صفحة

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # حساب الإجمالي العام لجميع الفواتير
        context['total_amount'] = Invoice.objects.aggregate(Sum('total_amount'))['total_amount__sum']
        
        # حساب إجمالي الفواتير المعروضة في الصفحة الحالية
        current_page_invoices = context['invoices']
        page_total = sum(invoice.total_amount for invoice in current_page_invoices)
        context['page_total'] = page_total

        return context


from django.shortcuts import render, redirect
from django.views import View
from .models import Invoice, InvoiceItem, Product, Status, User

from django.shortcuts import render, redirect
from django.views import View
from .models import Invoice, InvoiceItem, Product, Status, Currency, User

class InvoiceCreateView(View):
    template_name = 'invoice/invoice_form.html'

    def get(self, request, *args, **kwargs):
        # تمرير قائمة المستخدمين والحالات والعملات إلى القالب
        users = User.objects.all()
        statuses = Status.objects.all()  # جلب جميع الحالات
        currencies = Currency.objects.all()  # جلب جميع العملات

        return render(request, self.template_name, {
            'users': users,
            'statuses': statuses,  # إضافة الحالات إلى السياق
            'currencies': currencies,  # إضافة العملات إلى السياق
        })

    def post(self, request, *args, **kwargs):
        # جلب حالة الفاتورة باستخدام الـ id
        status_id = request.POST.get('status')
        try:
            status = Status.objects.get(id=status_id)  # الحصول على كائن Status
        except Status.DoesNotExist:
            # إذا لم يتم العثور على الحالة، يمكنك إرجاع خطأ أو تعيين حالة افتراضية
            status = Status.objects.first()  # تعيين أول حالة كحالة افتراضية

        # جلب العملة باستخدام الـ id
        currency_id = request.POST.get('currency')
        try:
            currency = Currency.objects.get(id=currency_id)  # الحصول على كائن Currency
        except Currency.DoesNotExist:
            # إذا لم يتم العثور على العملة، يمكنك إرجاع خطأ أو تعيين عملة افتراضية
            currency = Currency.objects.first()  # تعيين أول عملة كعملة افتراضية

        # حفظ بيانات الفاتورة
        invoice = Invoice.objects.create(
            date=request.POST.get('date'),
            customer_id=request.POST.get('customer_id'),  # استخدام customer_id بدلًا من customer
            phone_number=request.POST.get('phone_number'),
            address=request.POST.get('address'),
            shipping_company=request.POST.get('shipping_company'),
            shipping_num=request.POST.get('shipping_num'),
            payment_method=request.POST.get('payment_method'),
            currency=currency,  # تعيين كائن Currency
            status=status,  # تعيين كائن Status
        )

        # معالجة عناصر الفاتورة
        item_counter = 0
        total_amount = 0  # متغير لحساب الإجمالي العام

        while True:
            product_id = request.POST.get(f'product_id_{item_counter}')
            if not product_id:
                break  # توقف إذا لم يكن هناك المزيد من العناصر

            product = Product.objects.get(id=product_id)
            quantity = float(request.POST.get(f'quantity_{item_counter}', 0))
            unit_price = float(request.POST.get(f'unit_price_{item_counter}', 0))
            discount = float(request.POST.get(f'discount_{item_counter}', 0))
            addition = float(request.POST.get(f'addition_{item_counter}', 0))
            tax = float(request.POST.get(f'tax_{item_counter}', 0))
            image = request.FILES.get(f'image_{item_counter}')

            # حساب المجموع للعنصر الحالي
            item_total = (quantity * unit_price) - discount + addition + tax
            total_amount += item_total  # إضافة المجموع إلى الإجمالي العام

            # حفظ عنصر الفاتورة
            InvoiceItem.objects.create(
                invoice=invoice,
                product=product,  # ربط المنتج بالفاتورة
                product_name=product.product_name,  # حفظ اسم المنتج
                quantity=quantity,
                unit_price=unit_price,
                discount=discount,
                addition=addition,
                tax=tax,
                image=image,
                total=item_total,  # حفظ المجموع للعنصر
            )

            item_counter += 1

        # تحديث الإجمالي العام في الفاتورة
        invoice.total_amount = total_amount
        invoice.save()

        return redirect('invoice_list')





def autocomplete_customers(request):
    term = request.GET.get('term')
    users = User.objects.filter(username__icontains=term)[:10]  # تحديد أول 10 نتائج
    user_list = [{'id': user.id, 'label': user.username} for user in users]
    return JsonResponse(user_list, safe=False)



def autocomplete_products(request):
    term = request.GET.get('term')  # الحصول على النص المدخل من المستخدم
    if term:
        products = Product.objects.filter(product_name__icontains=term)[:10]  # البحث عن أول 10 منتجات تطابق النص
        product_list = [{'id': product.id, 'label': product.product_name, 'price': product.purchase_price} for product in products]
    else:
        product_list = []
    return JsonResponse(product_list, safe=False)  # إرجاع البيانات كـ JSON



class InvoiceUpdateView(UpdateView):
    model = Invoice
    template_name = 'invoice/invoice_form.html'
    fields = '__all__'
    success_url = reverse_lazy('invoice_list')


class InvoiceDeleteView(DeleteView):
    model = Invoice
    template_name = 'invoice/invoice_confirm_delete.html'
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


# Status Views
class StatusListView(ListView):
    model = Status
    template_name = 'status/status_list.html'
    context_object_name = 'status'

class StatusCreateView(CreateView):
    model = Status
    form_class = StatusForm  # استخدام النموذج (Form)
    template_name = 'status/status_form.html'
    success_url = reverse_lazy('status_list')

class StatusUpdateView(UpdateView):
    model = Status
    form_class = StatusForm  # استخدام النموذج (Form)
    template_name = 'status/status_form.html'
    success_url = reverse_lazy('status_list')

class StatusDeleteView(DeleteView):
    model = Status
    template_name = 'status/status_confirm_delete.html'
    success_url = reverse_lazy('status_list')

class StatusDetailView(DetailView):
    model = Status
    template_name = 'status/status_detail.html'
    context_object_name = 'status'



# Shipping Views
class ShippingListView(ListView):
    model = Shipping_com_m
    template_name = 'shipping/shipping_list.html'
    context_object_name = 'shipping'

class ShippingCreateView(CreateView):
    model = Shipping_com_m
    form_class = ShippingForm  # استخدام النموذج (Form)
    template_name = 'shipping/shipping_form.html'
    success_url = reverse_lazy('shipping_list')

class ShippingUpdateView(UpdateView):
    model = Shipping_com_m
    form_class = ShippingForm  # استخدام النموذج (Form)
    template_name = 'shipping/shipping_form.html'
    success_url = reverse_lazy('shipping_list')

class ShippingDeleteView(DeleteView):
    model = Shipping_com_m
    template_name = 'shipping/shipping_confirm_delete.html'
    success_url = reverse_lazy('shipping_list')


class ShippingDetailView(DetailView):
    model = Shipping_com_m
    template_name = 'shipping/shipping_detail.html'
    context_object_name = 'shipping'


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

class PriceTypeDetailView(DetailView):
    model = PriceType
    template_name = 'invoice/priceType_detail.html'
    context_object_name = 'PriceType'














# Currency Views
class CurrencyListView(ListView):
    model = Currency
    template_name = 'currency/currency_list.html'
    context_object_name = 'currency'

class CurrencyCreateView(CreateView):
    model = Currency
    form_class = CurrencyForm  # استخدام النموذج (Form)
    template_name = 'currency/currency_form.html'
    success_url = reverse_lazy('currency_list')

class CurrencyUpdateView(UpdateView):
    model = Currency
    form_class = CurrencyForm  # استخدام النموذج (Form)
    template_name = 'currency/currency_form.html'
    success_url = reverse_lazy('currency_list')

class CurrencyDeleteView(DeleteView):
    model = Currency
    template_name = 'currency/currency_confirm_delete.html'
    success_url = reverse_lazy('currency_list')


class CurrencyDetailView(DetailView):
    model = Currency
    template_name = 'currency/currency_detail.html'
    context_object_name = 'currency'