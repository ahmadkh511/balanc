from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView , TemplateView , View
from django.urls import reverse_lazy
from django.views import View
from django.http import JsonResponse
from .forms import ProductForm, PriceTypeForm , ShippingForm , CurrencyForm , StatusForm
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Sum
from django.core.mail import EmailMessage
from openpyxl import Workbook  #التصدير إلى Excel:
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json
from django.core.files.storage import default_storage
from django.conf import settings
import os
from django.views import View




from .models import (
    Invoice, 
    InvoiceItem, 
    PriceType, 
    Product, 
    Shipping_com_m, 
    Currency, 
    User, 
    Status, 
    Purchase, 
    PurchaseItem, 
    Barcode
)



#======================================================================================


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_logo_url'] = self.request.session.get('company_logo_url', None)
        context['logo_width'] = self.request.session.get('logo_width', 200)  # قيمة افتراضية
        context['logo_height'] = self.request.session.get('logo_height', 100)  # قيمة افتراضية
        return context

    def post(self, request, *args, **kwargs):
        if 'company_logo' in request.FILES:
            # حفظ الصورة المرفوعة
            uploaded_file = request.FILES['company_logo']
            file_path = os.path.join('company_logos', uploaded_file.name)
            file_name = default_storage.save(file_path, uploaded_file)
            company_logo_url = default_storage.url(file_name)

            # حفظ رابط الصورة وأبعادها في الجلسة
            request.session['company_logo_url'] = company_logo_url
            request.session['logo_width'] = int(request.POST.get('logo_width', 200))
            request.session['logo_height'] = int(request.POST.get('logo_height', 100))

        return self.get(request, *args, **kwargs)



# Invoice
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


class InvoiceUpdateView(UpdateView):
    model = Invoice
    template_name = 'invoice/invoice_form.html'
    fields = '__all__'
    success_url = reverse_lazy('invoice_list')

    def get_context_data(self, **kwargs):
        # الحصول على السياق الحالي
        context = super().get_context_data(**kwargs)
        
        # إضافة قائمة المستخدمين والحالات والعملات إلى السياق
        context['users'] = User.objects.all()
        context['statuses'] = Status.objects.all()
        context['currencies'] = Currency.objects.all()
        
        return context


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


# === Purchase ===


class PurchaseListView(ListView):
    model = Purchase
    template_name = 'purchase/purchase_list.html'
    context_object_name = 'purchases'
    paginate_by = 4  # عرض 4 فواتير في كل صفحة

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # حساب الإجمالي العام لجميع فواتير المشتريات
        context['total_amount'] = Purchase.objects.aggregate(Sum('total_amount'))['total_amount__sum']
        
        # حساب إجمالي الفواتير المعروضة في الصفحة الحالية
        current_page_purchases = context['purchases']
        page_total = sum(purchase.total_amount for purchase in current_page_purchases)
        context['page_total'] = page_total

        return context




class PurchaseCreateView(View):
    template_name = 'purchase/purchase_form.html'

    def get(self, request, *args, **kwargs):
        suppliers = User.objects.all()
        statuses = Status.objects.all()
        currencies = Currency.objects.all()

        return render(request, self.template_name, {
            'suppliers': suppliers,
            'statuses': statuses,
            'currencies': currencies,
        })

    def post(self, request, *args, **kwargs):
        try:
            supplier = User.objects.get(id=request.POST.get('supplier_id'))
            currency = Currency.objects.get(id=request.POST.get('currency'))
            status = Status.objects.get(id=request.POST.get('status'))

            purchase = Purchase.objects.create(
                supplier=supplier,
                supplier_phone=request.POST.get('supplier_phone'),
                purchase_address=request.POST.get('purchase_address'),
                receiving_method=request.POST.get('receiving_method'),
                receiving_number=request.POST.get('receiving_number'),
                payment_method=request.POST.get('payment_method'),
                currency=currency,
                status=status,
                total_amount=0,
            )

            total_amount = 0
            item_counter = 0

            while True:
                item_name = request.POST.get(f'item_name_{item_counter}')
                if not item_name:
                    break

                barcode_value = request.POST.get(f'barcode_{item_counter}')
                barcode = Barcode.objects.filter(barcode=barcode_value).first()
                if not barcode and barcode_value:
                    barcode = Barcode.objects.create(barcode=barcode_value)

                quantity = int(request.POST.get(f'quantity_{item_counter}', 0))
                unit_price = float(request.POST.get(f'unit_price_{item_counter}', 0))
                discount = float(request.POST.get(f'discount_{item_counter}', 0))
                addition = float(request.POST.get(f'addition_{item_counter}', 0))
                tax = float(request.POST.get(f'tax_{item_counter}', 0))

                total = (quantity * unit_price) - discount + addition + ((quantity * unit_price) * tax / 100)
                total_amount += total

                PurchaseItem.objects.create(
                    purchase=purchase,
                    item_name=item_name,
                    barcode=barcode,
                    quantity=quantity,
                    unit_price=unit_price,
                    discount=discount,
                    addition=addition,
                    tax=tax,
                    total=total,
                )

                item_counter += 1

            purchase.total_amount = total_amount
            purchase.save()

            return redirect('purchase_list')

        except Exception as e:
            print(f"Error: {e}")
            return redirect('purchase_create')



def autocomplete_barcodes(request):
    if 'term' in request.GET:
        search_term = request.GET.get('term')  # الحصول على الكلمة التي يبحث عنها المستخدم
        barcodes = Barcode.objects.filter(barcode__icontains=search_term)[:10]  # البحث عن الباركودات المطابقة
        results = [{'id': barcode.id, 'label': barcode.barcode} for barcode in barcodes]  # تحضير البيانات للاستجابة
        return JsonResponse(results, safe=False)  # إرجاع البيانات كـ JSON
    return JsonResponse([], safe=False)  # إرجاع قائمة فارغة إذا لم يتم إدخال كلمة بحث



class PurchaseUpdateView(UpdateView):
    model = Purchase
    template_name = 'purchase/purchase_form.html'
    fields = '__all__'
    success_url = reverse_lazy('purchase_list')

    def get_context_data(self, **kwargs):
        # الحصول على السياق الحالي
        context = super().get_context_data(**kwargs)
        
        # إضافة قائمة الموردين والحالات والعملات إلى السياق
        context['suppliers'] = User.objects.all()
        context['statuses'] = Status.objects.all()
        context['currencies'] = Currency.objects.all()
        
        return context
    




class PurchaseDeleteView(DeleteView):
    model = Purchase
    template_name = 'purchase/purchase_confirm_delete.html'
    success_url = reverse_lazy('purchase_list')




class PurchaseDetailView(DetailView):
    model = Purchase
    template_name = 'purchase/purchase_detail.html'
    context_object_name = 'purchase'



class PurchaseItemCreateView(CreateView):
    model = PurchaseItem
    template_name = 'purchaseitem_form.html'
    fields = '__all__'
    success_url = reverse_lazy('purchase_list')











class PurchaseItemUpdateView(UpdateView):
    model = PurchaseItem
    template_name = 'purchaseitem_form.html'
    fields = '__all__'
    success_url = reverse_lazy('purchase_list')


class PurchaseItemDeleteView(DeleteView):
    model = PurchaseItem
    template_name = 'purchaseitem_confirm_delete.html'
    success_url = reverse_lazy('purchase_list')




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



def export_invoice_pdf(request, pk):
    invoice = Invoice.objects.get(pk=pk)
    html_string = render_to_string('export/invoice_template.html', {'invoice': invoice})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=invoice_{invoice.uniqueId}.pdf'

    # تحويل HTML إلى PDF
    pisa_status = pisa.CreatePDF(html_string, dest=response)
    if pisa_status.err:
        return HttpResponse('حدث خطأ أثناء إنشاء PDF.')
    return response

def send_invoice_email(request, pk):
    invoice = Invoice.objects.get(pk=pk)
    
    # التحقق من وجود البريد الإلكتروني
    if not hasattr(invoice.customer, 'email') or not invoice.customer.email:
        return HttpResponse('بريد العميل غير متوفر، لا يمكن إرسال الفاتورة.')

    subject = f'فاتورة رقم: {invoice.uniqueId}'
    message = 'مرحبًا، مرفق نسخة من الفاتورة.'
    email_from = 'wcomsy@gmail.com'
    recipient_list = [invoice.customer.email]

    # إنشاء PDF
    html_string = render_to_string('export/invoice_template.html', {'invoice': invoice})
    pdf = BytesIO()
    pisa.CreatePDF(html_string, dest=pdf)

    # إرسال البريد الإلكتروني
    email = EmailMessage(subject, message, email_from, recipient_list)
    email.attach(f'invoice_{invoice.uniqueId}.pdf', pdf.getvalue(), 'application/pdf')
    
    try:
        email.send()
        return HttpResponse('تم إرسال الفاتورة بنجاح.')
    except Exception as e:
        return HttpResponse(f'حدث خطأ أثناء إرسال البريد الإلكتروني: {str(e)}')

def export_invoice_excel(request, pk):
    invoice = Invoice.objects.get(pk=pk)
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename=invoice_{invoice.uniqueId}.xlsx'

    wb = Workbook()
    ws = wb.active
    ws.title = "فاتورة"

    # إضافة البيانات
    ws.append(['المنتج', 'الكمية', 'السعر الفردي', 'الخصم', 'الإضافة', 'الضريبة', 'المجموع'])
    for item in invoice.items.all():
        ws.append([item.product_name, item.quantity, item.unit_price, item.discount, item.addition, item.tax, item.total])

    wb.save(response)
    return response



#===============================


def export_purchase_pdf(request, pk):
    purchase = Purchase.objects.get(pk=pk)
    html_string = render_to_string('export/purchase_template.html', {'purchase': purchase})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=purchase_{purchase.uniqueId}.pdf'

    # تحويل HTML إلى PDF
    pisa_status = pisa.CreatePDF(html_string, dest=response)
    if pisa_status.err:
        return HttpResponse('حدث خطأ أثناء إنشاء PDF.')
    return response


def send_purchase_email(request, pk):
    purchase = Purchase.objects.get(pk=pk)
    
    # التحقق من وجود البريد الإلكتروني
    if not hasattr(purchase.supplier, 'email') or not purchase.supplier.email:
        return HttpResponse('بريد المورد غير متوفر، لا يمكن إرسال الفاتورة.')

    subject = f'فاتورة مشتريات رقم: {purchase.uniqueId}'
    message = 'مرحبًا، مرفق نسخة من فاتورة المشتريات.'
    email_from = 'wcomsy@gmail.com'
    recipient_list = [purchase.supplier.email]

    # إنشاء PDF
    html_string = render_to_string('export/purchase_template.html', {'purchase': purchase})
    pdf = BytesIO()
    pisa.CreatePDF(html_string, dest=pdf)

    # إرسال البريد الإلكتروني
    email = EmailMessage(subject, message, email_from, recipient_list)
    email.attach(f'purchase_{purchase.uniqueId}.pdf', pdf.getvalue(), 'application/pdf')
    
    try:
        email.send()
        return HttpResponse('تم إرسال فاتورة المشتريات بنجاح.')
    except Exception as e:
        return HttpResponse(f'حدث خطأ أثناء إرسال البريد الإلكتروني: {str(e)}')
    

def export_purchase_excel(request, pk):
    purchase = Purchase.objects.get(pk=pk)
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = f'attachment; filename=purchase_{purchase.uniqueId}.xlsx'

    wb = Workbook()
    ws = wb.active
    ws.title = "فاتورة مشتريات"

    # إضافة البيانات
    ws.append(['الصنف', 'الكمية', 'السعر الفردي', 'الخصم', 'الإضافة', 'الضريبة', 'المجموع'])
    for item in purchase.items.all():
        ws.append([item.item_name, item.quantity, item.unit_price, item.discount, item.addition, item.tax, item.total])

    wb.save(response)
    return response

def autocomplete_suppliers(request):
    term = request.GET.get('term')
    suppliers = User.objects.filter(username__icontains=term)[:10]  # تحديد أول 10 نتائج
    supplier_list = [{'id': supplier.id, 'label': supplier.username} for supplier in suppliers]
    return JsonResponse(supplier_list, safe=False)

def autocomplete_items(request):
    term = request.GET.get('term')  # الحصول على النص المدخل من المستخدم
    if term:
        products = Product.objects.filter(product_name__icontains=term)[:10]  # البحث عن أول 10 منتجات تطابق النص
        product_list = [{'id': product.id, 'label': product.product_name, 'price': product.purchase_price} for product in products]
    else:
        product_list = []
    return JsonResponse(product_list, safe=False)  # إرجاع البيانات كـ JSON

