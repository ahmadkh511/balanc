# from ai

from pyexpat.errors import messages
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView , TemplateView , View

from django.urls import reverse_lazy

from django.http import JsonResponse
from .forms import ProductForm, PriceTypeForm , ShippingForm , CurrencyForm , StatusForm , BarcodeForm , payment_methodForm , PurchaseForm, PurchaseItemForm
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
from datetime import date, datetime
from django.db.models import Sum, Prefetch

from django.views.generic import ListView
from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.views.generic import UpdateView, CreateView, DeleteView
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.generic.edit import CreateView
from django.contrib.auth import get_user_model
from django.forms import modelformset_factory




User = get_user_model()








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
    Barcode , 
    Payment_method ,
    PurchaseItemBarcode ,
)




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

#===============================

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



# === Purchase ===

class PurchaseListView(ListView):
    model = Purchase
    template_name = 'purchase/purchase_list.html'
    context_object_name = 'purchases'
    paginate_by = 4

    def get_queryset(self):
        # تحسين الاستعلام ليشمل الباركودات المرتبطة
        return Purchase.objects.select_related(
            'supplier',
            'payment_method',
            'currency',
            'status'
        ).prefetch_related(
            Prefetch(
                'items',
                queryset=PurchaseItem.objects.prefetch_related(
                    Prefetch(
                        'purchaseitembarcode_set',
                        queryset=PurchaseItemBarcode.objects.select_related('barcode'),
                        to_attr='all_barcodes'
                    )
                )
            )
        ).order_by('-date_created')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # حساب الإجماليات
        context['total_amount'] = Purchase.objects.aggregate(
            Sum('total_amount')
        )['total_amount__sum'] or 0
        
        current_page_purchases = context['purchases']
        context['page_total'] = sum(
            purchase.total_amount for purchase in current_page_purchases
        ) if current_page_purchases else 0
        
        return context


class PurchaseCreateView(View):
    template_name = 'purchase/add_purchase.html'

    def get(self, request, *args, **kwargs):
        suppliers = User.objects.all()
        statuses = Status.objects.all()
        currencies = Currency.objects.all()
        payment_methods = Payment_method.objects.all()

        return render(request, self.template_name, {
            'suppliers': suppliers,
            'statuses': statuses,
            'currencies': currencies,
            'payment_methods': payment_methods,
            'today': timezone.now().date().isoformat(),
        })

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            # 1. التحقق من البيانات الأساسية
            supplier_id = request.POST.get('supplier_id')
            if not supplier_id:
                raise ValidationError("يجب اختيار المورد")
            
            # 2. الحصول على البيانات الأساسية
            supplier = User.objects.get(id=supplier_id)
            currency = Currency.objects.get(id=request.POST.get('currency'))
            status = Status.objects.get(id=request.POST.get('status'))
            payment_method = Payment_method.objects.get(id=request.POST.get('payment_method'))
            
            # 3. معالجة القيم الحسابية
            global_discount = float(request.POST.get('global_discount', 0))
            global_addition = float(request.POST.get('global_addition', 0))
            global_tax = float(request.POST.get('global_tax', 0))

            # 4. حساب قيمة السلع (subtotal)
            subtotal = 0
            purchase_items = []
            
            item_counter = 0
            while True:
                item_name = request.POST.get(f'item_name_{item_counter}')
                if not item_name:
                    break
                    
                quantity = float(request.POST.get(f'quantity_{item_counter}', 0))
                unit_price = float(request.POST.get(f'unit_price_{item_counter}', 0))
                item_total = quantity * unit_price
                subtotal += item_total
                
                purchase_items.append({
                    'item_name': item_name,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'total': item_total,
                    'barcodes': []
                })
                
                # جمع الباركودات
                for barcode_index in range(int(quantity)):
                    barcode_value = request.POST.get(f'barcode_{item_counter}_{barcode_index}')
                    if barcode_value:
                        purchase_items[-1]['barcodes'].append({
                            'value': barcode_value,
                            'is_primary': (barcode_index == 0)
                        })
                
                item_counter += 1

            # 5. الحسابات الضريبية حسب المطلوب
            tax_amount = (subtotal * (global_tax / 100)) if global_tax else 0
            after_tax = subtotal + tax_amount
            final_total = after_tax + global_addition - global_discount

            # 6. إنشاء فاتورة الشراء
            purchase = Purchase.objects.create(
                supplier=supplier,
                supplier_phone=request.POST.get('supplier_phone'),
                purchase_address=request.POST.get('purchase_address'),
                receiving_method=request.POST.get('receiving_method'),
                receiving_number=request.POST.get('receiving_number'),
                notes=request.POST.get('notes'),
                payment_method=payment_method,
                currency=currency,
                status=status,
                total_amount=final_total,
                date=request.POST.get('date') or timezone.now().date(),
                global_discount=global_discount,
                global_addition=global_addition,
                global_tax=global_tax,
            )

            # 7. إضافة العناصر والباركودات
            for item_data in purchase_items:
                purchase_item = PurchaseItem.objects.create(
                    purchase=purchase,
                    item_name=item_data['item_name'],
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price'],
                    total=item_data['total'],
                )

                for barcode_data in item_data['barcodes']:
                    barcode, created = Barcode.objects.get_or_create(
                        barcode_in=barcode_data['value'],
                        defaults={'barcode_out': barcode_data['value']}
                    )
                    PurchaseItemBarcode.objects.create(
                        purchase_item=purchase_item,
                        barcode=barcode,
                        is_primary=barcode_data['is_primary']
                    )

            messages.success(request, "تم حفظ الفاتورة بنجاح")
            return redirect('purchase_list')

        except User.DoesNotExist:
            messages.error(request, "المورد المحدد غير موجود")
        except (Currency.DoesNotExist, Status.DoesNotExist, Payment_method.DoesNotExist):
            messages.error(request, "حدث خطأ في أحد البيانات الأساسية")
        except ValueError as e:
            messages.error(request, f"قيمة غير صالحة: {str(e)}")
        except ValidationError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"حدث خطأ غير متوقع: {str(e)}")
        
        return redirect('purchase_create')

    def calculate_totals(self, purchase):
        """دالة مساعدة لحساب المجاميع"""
        subtotal = sum(item.total for item in purchase.items.all())
        tax_amount = (subtotal * (purchase.global_tax / 100)) if purchase.global_tax else 0
        purchase.total_amount = (subtotal + tax_amount) + purchase.global_addition - purchase.global_discount
        purchase.save()


#----------------------------------------

from decimal import Decimal
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from .models import Purchase, PurchaseItem

from django.db.models import Q
from django.views.generic.edit import UpdateView
from django.shortcuts import redirect
from decimal import Decimal

from .models import Purchase, PurchaseItem, PurchaseItemBarcode, Barcode


from django.views.generic.edit import UpdateView
from decimal import Decimal
from .models import Purchase, PurchaseItem, Barcode, PurchaseItemBarcode
from .forms import PurchaseForm  # ✅ استيراد النموذج الذي أنشأناه

class PurchaseUpdateView(UpdateView):
    """
    هذا الكلاس يسمح بتعديل فاتورة الشراء المحددة.
    """
    model = Purchase
    template_name = 'purchase/purchase_update.html'

    # ✅ نربط الفيو بالنموذج المخصص بدلًا من استخدام fields
    form_class = PurchaseForm

    def dispatch(self, request, *args, **kwargs):
        """
        يتم تنفيذ هذا التابع أولاً قبل get/post/...
        نستخدمه هنا لتحويل المستخدم إلى عرض تفاصيل الفاتورة إن لم يكن مسجلاً أو لا نريد تفعيل الصلاحيات الآن.
        """
        # حالياً نسمح لأي مستخدم بمشاهدة الصفحة، لكن لو أردنا لاحقاً حماية الصفحة، نعيد تفعيل LoginRequiredMixin
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        تجهيز البيانات التي سيتم تمريرها إلى القالب (context)
        نضيف إليه العناصر المرتبطة بالفاتورة مع باركوداتها
        """
        context = super().get_context_data(**kwargs)

        # جلب العناصر المرتبطة بالفاتورة مع الباركودات
        items = PurchaseItem.objects.filter(purchase=self.object).prefetch_related('purchaseitembarcode_set__barcode')

        enriched_items = []
        for item in items:
            # جمع كل الباركودات الخاصة بكل عنصر
            barcodes = [rel.barcode.barcode_in for rel in item.purchaseitembarcode_set.all()]
            enriched_items.append({
                'id': item.id,
                'item_name': item.item_name,
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'total': item.total,
                'barcodes': barcodes,
            })

        context['items'] = enriched_items
        return context

    def form_valid(self, form):
        """
        عندما يتم إرسال النموذج بنجاح:
        - نحذف العناصر القديمة
        - ننشئ عناصر جديدة بناءً على البيانات المرسلة
        - نربط الباركودات
        - نحسب الإجماليات
        """
        response = super().form_valid(form)

        # حذف العناصر القديمة المرتبطة بالفاتورة
        PurchaseItem.objects.filter(purchase=self.object).delete()

        # استخراج بيانات العناصر من الطلب
        items = self.request.POST.getlist('item_name[]')
        quantities = self.request.POST.getlist('quantity[]')
        prices = self.request.POST.getlist('price[]')

        for index, (name, qty, price) in enumerate(zip(items, quantities, prices)):
            if name.strip() == "":
                continue

            try:
                quantity = int(qty)
                unit_price = Decimal(price)
            except (ValueError, TypeError):
                continue

            # إنشاء عنصر جديد
            purchase_item = PurchaseItem.objects.create(
                purchase=self.object,
                item_name=name,
                quantity=quantity,
                unit_price=unit_price
            )

            # ربط الباركودات بهذا العنصر
            barcodes_key = f'barcodes_{index}[]'
            barcode_values = self.request.POST.getlist(barcodes_key)

            for i, barcode_value in enumerate(barcode_values):
                if barcode_value.strip() == "":
                    continue

                barcode_obj, _ = Barcode.objects.get_or_create(barcode_in=barcode_value.strip())
                PurchaseItemBarcode.objects.create(
                    purchase_item=purchase_item,
                    barcode=barcode_obj,
                    is_primary=(i == 0)
                )

        # تحديث الإجماليات
        self.object.calculate_totals()
        return response

    def get_success_url(self):
        """
        بعد التحديث الناجح، يتم إعادة التوجيه إلى صفحة تفاصيل الفاتورة
        """
        return self.object.get_absolute_url()






def autocomplete_suppliers(request):
    term = request.GET.get('term', '')
    suppliers = User.objects.filter(username__icontains=term).values('id', 'username')[:10]
    results = [{'id': s['id'], 'label': s['username']} for s in suppliers]
    return JsonResponse(results, safe=False)






def autocomplete_items(request):
    term = request.GET.get('term')
    items = PurchaseItem.objects.filter(
        item_name__icontains=term
    ).values_list('item_name', flat=True).distinct()[:10]
    return JsonResponse(list(items), safe=False)

def autocomplete_barcodes(request):
    term = request.GET.get('term')
    barcodes = Barcode.objects.filter(
        barcode_in__icontains=term
    ).values('id', 'barcode_in')[:10]
    results = [{'id': b['id'], 'label': b['barcode_in']} for b in barcodes]
    return JsonResponse(results, safe=False)



class PurchaseItemUpdateView(UpdateView):
    model = PurchaseItem
    form_class = PurchaseItemForm
    template_name = 'purchase/purchaseitem_update.html'
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # جعل حقول الأصناف للقراءة فقط
        for field in form.fields:
            form.fields[field].widget.attrs['readonly'] = True
            form.fields[field].widget.attrs['disabled'] = True
        return form
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # جلب الباركودات المرتبطة بالصنف
        context['barcodes'] = self.object.purchaseitembarcode_set.all()
        return context
    
    def get_success_url(self):
        return reverse('purchase_detail', kwargs={'pk': self.object.purchase.pk})

#-----------من اجل ادارة الباركودات  عند التعديل ---------

class ManageBarcodesView(UpdateView):
    model = PurchaseItem
    template_name = 'purchase/manage_barcodes.html'
    fields = []
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['barcodes'] = self.object.purchaseitembarcode_set.all()
        return context
    
    def get_success_url(self):
        return reverse('purchase_update', kwargs={'pk': self.object.purchase.pk})



class PurchaseItemCreateView(CreateView):
    model = PurchaseItem
    form_class = PurchaseItemForm
    template_name = 'purchase/purchaseitem_form.html'
    
    def get_initial(self):
        initial = super().get_initial()
        if 'purchase_id' in self.request.GET:
            initial['purchase'] = self.request.GET.get('purchase_id')
        return initial

    def get_success_url(self):
        return reverse('purchase_detail', kwargs={'pk': self.object.purchase.pk})


class PurchaseItemDeleteView(DeleteView):
    model = PurchaseItem
    template_name = 'purchase/purchaseitem_confirm_delete.html'
    
    def get_success_url(self):
        return reverse('purchase_detail', kwargs={'pk': self.object.purchase.pk})





from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from .models import Purchase, PurchaseItem, PurchaseItemBarcode, Barcode

class PurchaseDeleteView(DeleteView):
    model = Purchase
    template_name = 'purchase/purchase_confirm_delete.html'
    success_url = reverse_lazy('purchase_list')

    def delete(self, request, *args, **kwargs):
        """
        قبل حذف الفاتورة:
        - حذف العلاقات بين العناصر والباركودات
        - حذف الباركودات إذا كانت غير مرتبطة بأي عناصر أخرى
        """
        # الحصول على الفاتورة
        purchase = self.get_object()

        # حذف جميع العلاقات بين العناصر والباركودات
        purchase_items = PurchaseItem.objects.filter(purchase=purchase)
        for item in purchase_items:
            # حذف جميع العلاقات بين العناصر والباركودات
            item.purchaseitembarcode_set.all().delete()

        # الآن نقوم بحذف الفاتورة نفسها
        response = super().delete(request, *args, **kwargs)

        # حذف الباركودات الغير مرتبطة بأي عناصر أخرى
        barcodes = Barcode.objects.all()
        for barcode in barcodes:
            if barcode.purchaseitembarcode_set.count() == 0:  # لا يوجد أي عنصر مرتبط بهذا الباركود
                barcode.delete()

        return response








class PurchaseDetailView(DetailView):
    model = Purchase
    template_name = 'purchase/purchase_detail.html'
    context_object_name = 'purchase'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # جلب جميع عناصر الفاتورة مع الباركودات المرتبطة بها عبر الجدول الوسيط
        purchase_items = self.object.items.all().prefetch_related(
            'purchaseitembarcode_set__barcode'
        )
        
        context['purchase_items'] = purchase_items
        return context


class PurchaseItemUpdateView(UpdateView):
    model = PurchaseItem
    template_name = 'purchaseitem_form.html'
    fields = '__all__'
    success_url = reverse_lazy('purchase_list')


class PurchaseItemDetailView(DetailView):
    model = PurchaseItem
    template_name = 'purchases/purchaseitem_detail.html'


# Barcode Views
class barcodeListView(ListView):
    model = Barcode
    template_name = 'barcode/barcode_list.html'
    context_object_name = 'barcode'

class barcodeCreateView(CreateView):
    model = Barcode
    form_class = BarcodeForm  # استخدام النموذج (Form)
    template_name = 'barcode/barcode_form.html'
    success_url = reverse_lazy('barcode_list')

class barcodeUpdateView(UpdateView):
    model = Barcode
    form_class = BarcodeForm  # استخدام النموذج (Form)
    template_name = 'barcode/barcode_form.html'
    success_url = reverse_lazy('barcode_list')

class barcodeDeleteView(DeleteView):
    model = Barcode
    template_name = 'barcode/barcode_confirm_delete.html'
    success_url = reverse_lazy('barcode_list')

class barcodeDetailView(DetailView):
    model = Barcode
    template_name = 'barcode/barcode_detail.html'
    context_object_name = 'barcode'


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
    fields = ['status_types', 'status_description']

    def form_valid(self, form):
        self.object = form.save()
        return JsonResponse({
            'success': True,
            'id': self.object.id,
            'name': self.object.status_types
        })

    def form_invalid(self, form):
        return JsonResponse({
            'success': False,
            'errors': form.errors.as_json()
        }, status=400)


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
    fields = ['currency_name', 'description']

    def form_valid(self, form):
        self.object = form.save()
        return JsonResponse({
            'success': True,
            'id': self.object.id,
            'name': self.object.currency_name
        })

    def form_invalid(self, form):
        return JsonResponse({
            'success': False,
            'errors': form.errors.as_json()
        }, status=400)


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


# Payment_method Views
class payment_methodListView(ListView):
    model = Payment_method
    template_name = 'payment_method/payment_method_list.html'
    context_object_name = 'payment_method'


class payment_methodCreateView(CreateView):

    model = Payment_method
    fields = ['payment_method_name', 'payment_method_notes']

    def form_valid(self, form):
        self.object = form.save()
        return JsonResponse({
            'success': True,
            'id': self.object.id,
            'name': self.object.payment_method_name
        })

    def form_invalid(self, form):
        return JsonResponse({
            'success': False,
            'errors': form.errors.as_json()
        }, status=400)


class payment_methodUpdateView(UpdateView):
    model = Payment_method
    form_class = payment_methodForm  # استخدام النموذج (Form)
    template_name = 'payment_method/payment_method_form.html'
    success_url = reverse_lazy('payment_method_list')

class payment_methodDeleteView(DeleteView):
    model = Payment_method
    template_name = 'payment_method/payment_method_confirm_delete.html'
    success_url = reverse_lazy('payment_method_list')

class payment_methodDetailView(DetailView):
    model = Payment_method
    template_name = 'payment_method/payment_method_detail.html'
    context_object_name = 'payment_method'





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
    

def autocomplete_items(request):
    term = request.GET.get('term')
    items = PurchaseItem.objects.filter(
        item_name__icontains=term
    ).values_list('item_name', flat=True).distinct()
    return JsonResponse(list(items), safe=False)

def autocomplete_items(request):
    term = request.GET.get('term')  # الحصول على النص المدخل من المستخدم
    if term:
        products = Product.objects.filter(product_name__icontains=term)[:10]  # البحث عن أول 10 منتجات تطابق النص
        product_list = [{'id': product.id, 'label': product.product_name, 'price': product.purchase_price} for product in products]
    else:
        product_list = []
    return JsonResponse(product_list, safe=False)  # إرجاع البيانات كـ JSON


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