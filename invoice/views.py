# Standard library imports
import json
import logging
import os
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

# تأكد من أن هذه النماذج مستوردة من models.py الخاص بك
from .models import (
    Sale, SaleItem, Barcode, Product, # تأكد أن Customer موجود رغم أننا لا نستخدمه مباشرة في SaleListView
    Shipping_com_m, Currency, Payment_method, Status, SaleItemBarcode # SaleItemBarcode أيضاً
)
# تأكد من أن هذه الفورمز مستوردة من forms.py الخاص بك
from .forms import (
    SaleForm, SaleItemFormSet, BarcodeForm, ProductForm, 
    ShippingForm, 
    CurrencyForm, payment_methodForm
)
# Django core imports
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.files.storage import default_storage
from django.db import transaction
from django.db.models import Q, Prefetch, Sum, Avg, Max, Count
from django.forms import modelformset_factory, inlineformset_factory
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import (
    ListView, CreateView, UpdateView, 
    DeleteView, DetailView, TemplateView, View
)


from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied # استيراد هذا الاستثناءok
from django.http import Http404



from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, DeleteView
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Prefetch
import logging

from .models import Sale, SaleItemBarcode


# External libraries
from openpyxl import Workbook
from PIL import Image, UnidentifiedImageError
from xhtml2pdf import pisa
import magic

# Local models
from .models import (
    Barcode,
    Currency,
    Invoice,
    InvoiceItem,
    Payment_method,
    PriceType,
    Product,
    Purchase,
    PurchaseItem,
    PurchaseItemBarcode,
    Sale,
    SaleItem,
    SaleItemBarcode,
    Shipping_com_m,
    Status,
    User
)

# Local forms
from .forms import (
    BarcodeForm,
    CurrencyForm,
    payment_methodForm,
    PriceTypeForm,
    ProductForm,
    PurchaseForm,
    PurchaseItemForm,
    SaleForm,
    SaleItemForm,
    SaleItemFormSet,
    ShippingForm,
    StatusForm
)

# Initialize user model and logger
User = get_user_model()
logger = logging.getLogger(__name__)



from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Prefetch, Q, Sum, Avg, Max, Count
from django.http import JsonResponse, Http404 # تأكد من استيراد Http404 و JsonResponse
from django.core.exceptions import PermissionDenied, ValidationError # تأكد من استيراد ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model
import logging
from decimal import Decimal
import os
import magic # قد تحتاج لتثبيت python-magic: pip install python-magic
from PIL import Image, UnidentifiedImageError # قد تحتاج لتثبيت Pillow: pip install Pillow
from uuid import uuid4
from django.template.defaultfilters import slugify # إذا كنت تستخدم slugify في models.py

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin # أبقينا PermissionRequiredMixin لـ Create/Update/Delete
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Prefetch, Q, Sum, Avg, Max, Count
from django.http import JsonResponse, Http404
from django.core.exceptions import PermissionDenied, ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model
import logging
from decimal import Decimal
import os
import magic
from PIL import Image, UnidentifiedImageError
from uuid import uuid4
from django.template.defaultfilters import slugify # إذا كنت تستخدمها

# تأكد من أن هذه النماذج مستوردة من models.py الخاص بك
from .models import (
    Sale, SaleItem, Barcode, Product,
    Shipping_com_m, Currency, Payment_method, Status, SaleItemBarcode # SaleItemBarcode أيضاً
)
# تأكد من أن هذه الفورمز مستوردة من forms.py الخاص بك
# لاحظ أنني سأستخدم SaleItemFormSet مباشرة من forms.py
from .forms import SaleForm, SaleItemForm, FileUploadSecurity # سنحتاج SaleItemForm أيضاً

# لإنشاء SaleItemFormSet بشكل ديناميكي
from django.forms import inlineformset_factory

from django.db.models import Q, Sum, Avg, Max, Count, Prefetch
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
import logging


from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin # تأكد من استيرادها إن لم تكن موجودة
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied


from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied # استيراد هذا الاستثناءok
from django.http import Http404


from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.db.models import Prefetch, Q, Sum, Avg, Max, Count
from django.core.exceptions import PermissionDenied
from django.contrib import messages
import logging

from .models import Sale, SaleItemBarcode, Status, Payment_method, Currency


from .models import Sale, SaleItemBarcode, Status, Payment_method, Currency



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
                    barcode_in=barcode_data['value']
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

#  الكود المعتمد
#----------------------------------------

class PurchaseUpdateView(UpdateView):
    model = Purchase
    template_name = 'purchase/purchase_update.html'  # قالب الفاتورة
    form_class = PurchaseForm  # النموذج الذي سيتم استخدامه للتعديل

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # جلب العناصر المرتبطة بالفاتورة والباركودات المرتبطة بها
        items = PurchaseItem.objects.filter(purchase=self.object).prefetch_related('purchaseitembarcode_set__barcode')

        enriched_items = []  # قائمة لتخزين العناصر مع الباركودات
        for item in items:
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
        response = super().form_valid(form)

        # حفظ نسخة من كل باركود مرتبط بالفاتورة القديمة قبل الحذف
        old_barcodes = set(
            PurchaseItemBarcode.objects
            .filter(purchase_item__purchase=self.object)
            .values_list('barcode__barcode_in', flat=True)
        )

        # حذف العناصر القديمة المرتبطة بالفاتورة
        PurchaseItem.objects.filter(purchase=self.object).delete()

        # استخراج البيانات الجديدة من POST
        items = self.request.POST.getlist('item_name[]')
        quantities = self.request.POST.getlist('quantity[]')
        prices = self.request.POST.getlist('price[]')

        # تعقب الباركودات الجديدة بعد التعديل
        new_barcodes = set()

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

            # الحصول على الباركودات المدخلة لهذا العنصر
            barcodes_key = f'barcodes_{index}[]'
            barcode_values = self.request.POST.getlist(barcodes_key)

            for i, barcode_value in enumerate(barcode_values):
                clean_value = barcode_value.strip()
                if clean_value == "":
                    continue

                # تعقّب الباركود الجديد
                new_barcodes.add(clean_value)

                # استخدام الحقل barcode_in فقط
                barcode_obj, _ = Barcode.objects.get_or_create(barcode_in=clean_value)

                PurchaseItemBarcode.objects.create(
                    purchase_item=purchase_item,
                    barcode=barcode_obj,
                    is_primary=(i == 0)
                )

        # حذف الباركودات القديمة التي لم تعد مستخدمة
        unused_barcodes = old_barcodes - new_barcodes
        if unused_barcodes:
            Barcode.objects.filter(barcode_in__in=unused_barcodes).delete()

        # إعادة حساب المجاميع
        self.object.calculate_totals()
        return response

    def get_success_url(self):
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



class PurchaseDeleteView(DeleteView):
    model = Purchase
    template_name = 'purchase/purchase_confirm_delete.html'
    context_object_name = 'purchase'

    def get_object(self, queryset=None):
        return get_object_or_404(Purchase, id=self.kwargs['pk'])

    def post(self, request, *args, **kwargs):
        purchase = self.get_object()

        # الحصول على الباركودات المرتبطة بالفاتورة
        barcodes_links = PurchaseItemBarcode.objects.filter(purchase_item__purchase=purchase)

        if barcodes_links.exists():
            if request.POST.get('confirm_delete') == 'yes':
                # 1. جمع كل كائنات الباركود المرتبطة بالفاتورة
                barcodes_to_delete = [entry.barcode for entry in barcodes_links]

                # 2. حذف العلاقات بين PurchaseItem و Barcode
                barcodes_links.delete()

                # 3. حذف الباركودات من جدول Barcode نفسه
                for barcode in barcodes_to_delete:
                    barcode.delete()

                # 4. حذف الفاتورة
                purchase.delete()

                messages.success(request, "تم حذف الفاتورة وجميع الباركودات المرتبطة بها بنجاح.")
                return HttpResponseRedirect(reverse('purchase_list'))
            else:
                # المستخدم لم يؤكد الحذف بعد
                messages.warning(request, "تأكد من أنك تريد حذف الفاتورة والباركودات المرتبطة بها.")
                return render(request, self.template_name, {
                    'purchase': purchase,
                    'barcodes': barcodes_links
                })

        else:
            # لا توجد باركودات، نحذف الفاتورة فقط
            purchase.delete()
            messages.success(request, "تم حذف الفاتورة بنجاح.")
            return HttpResponseRedirect(reverse('purchase_list'))





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









#######################################################




# الحصول على نموذج المستخدم النشط
User = get_user_model()

# لتسجيل الأخطاء
logger = logging.getLogger(__name__)

# تعريف SaleItemFormSet هنا ليتم استخدامه في Views
# تأكد أن SaleItem هو النموذج الفرعي و Sale هو النموذج الأب
SaleItemFormSet = inlineformset_factory(Sale, SaleItem, form=SaleItemForm, extra=1, can_delete=True)




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

class StatusListView(PermissionRequiredMixin, ListView):
    """
    View for listing all invoice statuses with permission control
    """
    model = Status
    template_name = 'status/status_list.html'
    context_object_name = 'status_list'  # Changed for consistency
    permission_required = 'invoice.view_status'  # Added permission requirement
    paginate_by = 10  # Added pagination control

    def handle_no_permission(self):
        """Custom handling for unauthorized access"""
        return JsonResponse({'error': 'Unauthorized access'}, status=403)


class StatusCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    View for creating new invoice status with AJAX support
    """
    model = Status
    form_class = StatusForm
    template_name = 'status/status_form.html'
    permission_required = 'invoice.add_status'
    
    def form_valid(self, form):
        """Handle valid form submission with user association"""
        form.instance.created_by = self.request.user
        self.object = form.save()
        
        # Return JSON response for AJAX requests
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'id': self.object.id,
                'name': self.object.status_types,
                'redirect_url': reverse_lazy('status_list')
            })
        return super().form_valid(form)

    def form_invalid(self, form):
        """Handle invalid form submission"""
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors.get_json_data()
            }, status=400)
        return super().form_invalid(form)

    def get_success_url(self):
        """Default success URL"""
        return reverse_lazy('status_list')


class StatusUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    View for updating existing invoice status
    """
    model = Status
    form_class = StatusForm
    template_name = 'status/status_form.html'
    permission_required = 'invoice.change_status'
    
    def get_success_url(self):
        """Redirect to list view after update"""
        return reverse_lazy('status_list')


class StatusDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    View for deleting invoice status with confirmation
    """
    model = Status
    template_name = 'status/status_confirm_delete.html'
    permission_required = 'invoice.delete_status'
    success_url = reverse_lazy('status_list')
    
    def delete(self, request, *args, **kwargs):
        """Handle AJAX delete requests"""
        self.object = self.get_object()
        self.object.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'redirect_url': self.get_success_url()})
        return super().delete(request, *args, **kwargs)


class StatusDetailView(PermissionRequiredMixin, DetailView):
    """
    View for displaying invoice status details
    """
    model = Status
    template_name = 'status/status_detail.html'
    context_object_name = 'status'
    permission_required = 'invoice.view_status'

# Shipping Views


class ShippingListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    View for listing all shipping companies with search and pagination
    """
    model = Shipping_com_m
    template_name = 'shipping/shipping_list.html'
    context_object_name = 'shipping_companies'
    permission_required = 'shipping.view_shippingcompany'
    paginate_by = 10

    def get_queryset(self):
        """Filter results based on search query"""
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                shipping_company_name__icontains=search_query
            )
        return queryset.order_by('shipping_company_name')

    def handle_no_permission(self):
        """Custom handling for unauthorized access"""
        messages.error(self.request, 'ليس لديك صلاحية لعرض شركات الشحن')
        return super().handle_no_permission()


class ShippingCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    View for creating new shipping companies with AJAX support
    """
    model = Shipping_com_m
    form_class = ShippingForm
    template_name = 'shipping/shipping_form.html'
    permission_required = 'shipping.add_shippingcompany'
    
    def form_valid(self, form):
        """Handle valid form submission with user association"""
        form.instance.created_by = self.request.user
        self.object = form.save()
        
        # Return JSON response for AJAX requests
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'id': self.object.id,
                'name': self.object.shipping_company_name,
                'redirect_url': self.get_success_url()
            })
        
        messages.success(self.request, 'تم إنشاء شركة الشحن بنجاح')
        return super().form_valid(form)

    def form_invalid(self, form):
        """Handle invalid form submission"""
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors.get_json_data()
            }, status=400)
        
        messages.error(self.request, 'حدث خطأ أثناء إنشاء شركة الشحن')
        return super().form_invalid(form)

    def get_success_url(self):
        """Redirect to detail view after creation"""
        return reverse_lazy('shipping_detail', kwargs={'pk': self.object.id})


class ShippingUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    View for updating existing shipping companies
    """
    model = Shipping_com_m
    form_class = ShippingForm
    template_name = 'shipping/shipping_form.html'
    permission_required = 'shipping.change_shippingcompany'
    
    def form_valid(self, form):
        """Handle successful update"""
        response = super().form_valid(form)
        messages.success(self.request, 'تم تحديث بيانات شركة الشحن بنجاح')
        return response

    def get_success_url(self):
        """Redirect to detail view after update"""
        return reverse_lazy('shipping_detail', kwargs={'pk': self.object.id})


class ShippingDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """
    View for displaying shipping company details
    """
    model = Shipping_com_m
    template_name = 'shipping/shipping_detail.html'
    context_object_name = 'shipping'
    permission_required = 'shipping.view_shippingcompany'


class ShippingDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """
    View for deleting shipping companies with confirmation
    """
    model = Shipping_com_m
    template_name = 'shipping/shipping_confirm_delete.html'
    permission_required = 'shipping.delete_shippingcompany'
    success_url = reverse_lazy('shipping_list')
    
    def delete(self, request, *args, **kwargs):
        """Handle AJAX delete requests"""
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'redirect_url': str(success_url)
            })
        
        messages.success(request, 'تم حذف شركة الشحن بنجاح')
        return super().delete(request, *args, **kwargs)




# PriceType Views
class PriceTypeListView(ListView):
    model = PriceType
    template_name = 'pricetype/pricetype_list.html'
    context_object_name = 'pricetypes'

class PriceTypeCreateView(CreateView):
    model = PriceType
    form_class = PriceTypeForm  # استخدام النموذج (Form)
    template_name = 'pricetype/pricetype_form.html'
    success_url = reverse_lazy('pricetype_list')

class PriceTypeUpdateView(UpdateView):
    model = PriceType
    form_class = PriceTypeForm  # استخدام النموذج (Form)
    template_name = 'pricetype/pricetype_form.html'
    success_url = reverse_lazy('pricetype_list')

class PriceTypeDeleteView(DeleteView):
    model = PriceType
    template_name = 'pricetype/pricetype_confirm_delete.html'
    success_url = reverse_lazy('pricetype_list')

class PriceTypeDetailView(DetailView):
    model = PriceType
    template_name = 'pricetype/priceType_detail.html'
    context_object_name = 'PriceType'


# Currency Views


class CurrencyListView(LoginRequiredMixin, ListView):
    """عرض قائمة العملات مع تحسينات الأمان والأداء"""
    model = Currency
    template_name = 'currency/currency_list.html'
    context_object_name = 'currencies'  # تغيير الاسم ليكون أكثر وضوحاً (جمع)
    paginate_by = 10  # ترقيم الصفحات
    
    # تحسين الأداء باستخدام select_related/prefetch_related إذا كان هناك علاقات
    def get_queryset(self):
        return super().get_queryset().order_by('currency_name')


class CurrencyCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """إنشاء عملة جديدة مع تحسينات الأمان والاستجابة"""
    model = Currency
    form_class = CurrencyForm
    template_name = 'currency/currency_form.html'
    success_message = _('تم إنشاء العملة بنجاح')
    
    def get_success_url(self):
        return reverse_lazy('currency_list')
    
    def form_valid(self, form):
        """معالجة النموذج الصحيح مع دعم AJAX"""
        self.object = form.save()
        
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'id': self.object.id,
                'name': self.object.currency_name,
                'message': str(self.success_message)
            })
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """معالجة النموذج غير الصحيح مع دعم AJAX"""
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors.get_json_data(),
                'message': _('حدث خطأ في الإدخال، يرجى التصحيح والمحاولة مرة أخرى')
            }, status=400)
        return super().form_invalid(form)


class CurrencyUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """تحديث العملة مع تحسينات الأمان"""
    model = Currency
    form_class = CurrencyForm
    template_name = 'currency/currency_form.html'
    success_url = reverse_lazy('currency_list')
    success_message = _('تم تحديث العملة بنجاح')


class CurrencyDeleteView(LoginRequiredMixin, DeleteView):
    """حذف العملة مع تحسينات الأمان"""
    model = Currency
    template_name = 'currency/currency_confirm_delete.html'
    success_url = reverse_lazy('currency_list')
    
    def delete(self, request, *args, **kwargs):
        """معالجة الحذف مع دعم AJAX"""
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': _('تم حذف العملة بنجاح')
            })
        return HttpResponseRedirect(success_url)


class CurrencyDetailView(LoginRequiredMixin, DetailView):
    """عرض تفاصيل العملة"""
    model = Currency
    template_name = 'currency/currency_detail.html'
    context_object_name = 'currency'



# Payment_method Views

class payment_methodListView(ListView):
    model = Payment_method
    template_name = 'payment_method/payment_method_list.html'
    context_object_name = 'payment_method'
    paginate_by = 10

class payment_methodCreateView(CreateView):
    model = Payment_method
    form_class = payment_methodForm
    template_name = 'payment_method/payment_method_form.html'

    def form_valid(self, form):
        self.object = form.save()
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'id': self.object.id,
                'name': self.object.payment_method_name
            })
        return super().form_valid(form)

    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors.as_json()
            }, status=400)
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('payment_method_list')

class payment_methodUpdateView(UpdateView):
    model = Payment_method
    form_class = payment_methodForm
    template_name = 'payment_method/payment_method_form.html'
    success_url = reverse_lazy('payment_method_list')

class payment_methodDeleteView(DeleteView):
    model = Payment_method
    template_name = 'payment_method/payment_method_confirm_delete.html'
    success_url = reverse_lazy('payment_method_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            self.object.delete()
            return JsonResponse({
                'success': True,
                'message': 'تم الحذف بنجاح'
            })
        return super().delete(request, *args, **kwargs)

class payment_methodDetailView(DetailView):
    model = Payment_method
    template_name = 'payment_method/payment_method_detail.html'
    context_object_name = 'payment_method'




class FileUploadSecurity:
    """فئة متخصصة في التحقق الآمن من الملفات المرفوعة"""
    
    ALLOWED_MIME_TYPES = ['image/jpeg', 'image/png', 'image/webp']
    MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB
    MAX_DIMENSION = 5000  # أقصى عرض أو ارتفاع للصورة

    @classmethod
    def validate_file(cls, uploaded_file):
        """التحقق من الملف المرفوع مع تطبيق جميع الإجراءات الأمنية"""
        cls._check_file_size(uploaded_file)
        cls._check_extension(uploaded_file)
        cls._check_mime_type(uploaded_file)
        cls._check_image_content(uploaded_file)
        cls._sanitize_filename(uploaded_file)

    @classmethod
    def _check_file_size(cls, file):
        if file.size > cls.MAX_FILE_SIZE:
            raise ValidationError(f"حجم الملف يتجاوز الحد المسموح ({cls.MAX_FILE_SIZE/1024/1024}MB)")

    @classmethod
    def _check_extension(cls, file):
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
            raise ValidationError("امتداد الملف غير مسموح")

    @classmethod
    def _check_mime_type(cls, file):
        file.seek(0)
        try:
            mime = magic.from_buffer(file.read(1024), mime=True)
            file.seek(0)
            
            if mime not in cls.ALLOWED_MIME_TYPES:
                raise ValidationError(f"نوع الملف غير مدعوم: {mime}")
        except Exception as e:
            file.seek(0)
            raise ValidationError("تعذر تحديد نوع الملف") from e

    @classmethod
    def _check_image_content(cls, file):
        file.seek(0)
        try:
            with Image.open(file) as img:
                if max(img.size) > cls.MAX_DIMENSION:
                    raise ValidationError(f"أبعاد الصورة تتجاوز الحد الأقصى ({cls.MAX_DIMENSION}px)")
                img.verify()
                
                if img.mode not in ['L', 'RGB', 'RGBA']:
                    raise ValidationError("نوع الصورة اللوني غير مدعوم")
                
            file.seek(0)
        except UnidentifiedImageError:
            raise ValidationError("الملف ليس صورة صالحة")
        except Exception as e:
            raise ValidationError(f"خطأ في محتوى الصورة: {str(e)}")

    @classmethod
    def _sanitize_filename(cls, file):
        """إعادة تسمية الملف باسم آمن باستخدام UUID"""
        ext = os.path.splitext(file.name)[1].lower()
        file.name = f"{uuid4().hex}{ext}"

class SaleCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView): # <--- PermissionRequiredMixin موجود هنا
    model = Sale
    form_class = SaleForm
    template_name = 'sales/sale_create.html'
    success_url = reverse_lazy('sale_list')
    #permission_required = ['sales.add_sale'] # <--- صلاحية واضحة هنا
    permission_required = ['invoice.add_sale']
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        """إعداد البيانات الأساسية للقالب"""
        context = super().get_context_data(**kwargs)
        context.update({
            'statuses': Status.objects.all(),
            'payment_methods': Payment_method.objects.all(),
            'currencies': Currency.objects.all(),
            'shipping_companies': Shipping_com_m.objects.all(), # تأكد أن هذا هو الاسم الصحيح لنموذج شركة الشحن
        })
        
        if hasattr(self, 'preserved_form_data'):
            context.update(self.preserved_form_data)
        return context

    def handle_no_permission(self):
        """معالجة حالات عدم وجود الصلاحية"""
        messages.error(self.request, "ليس لديك صلاحية لإضافة فاتورة مبيعات.")
        # إذا كان المستخدم مسجلاً للدخول ولكن ليس لديه الصلاحية، ارفع 403
        if self.request.user.is_authenticated:
            raise PermissionDenied("ليس لديك الصلاحية المطلوبة.")
        # إذا لم يكن مسجلاً للدخول، أعد توجيهه إلى صفحة تسجيل الدخول
        return redirect(self.login_url)

    @transaction.atomic
    def form_valid(self, form):
        """المعالجة الرئيسية لحفظ الفاتورة"""
        try:
            sale = self._create_sale_instance(form)
            sale.save()  # حفظ الفاتورة أولاً
            
            self._process_sale_items(sale)
            self._calculate_final_totals(sale)
            
            logger.info(f"تم إنشاء فاتورة جديدة رقم {sale.id} بواسطة {self.request.user}")
            messages.success(self.request, 'تم حفظ الفاتورة بنجاح')
            return redirect(self.success_url)
            
        except ValidationError as e:
            logger.error(f"خطأ في التحقق من صحة البيانات: {str(e)}")
            messages.error(self.request, str(e))
            return self.form_invalid(form)
        except Exception as e:
            logger.error(f"خطأ غير متوقع أثناء حفظ الفاتورة: {str(e)}", exc_info=True)
            messages.error(self.request, f'حدث خطأ غير متوقع أثناء الحفظ: {str(e)}')
            return self.form_invalid(form)

    def _create_sale_instance(self, form):
        """إنشاء نسخة أولية من الفاتورة مع البيانات الأساسية"""
        customer = self._validate_and_get_customer()
        
        sale = form.save(commit=False)
        sale.created_by = self.request.user
        sale.sale_customer = customer
        sale.sale_status_id = self.request.POST.get('sale_status')
        sale.sale_payment_method_id = self.request.POST.get('sale_payment_method')
        sale.sale_currency_id = self.request.POST.get('sale_currency')
        sale.subtotal = Decimal('0.00')
        sale.discount_amount = Decimal('0.00')
        sale.addition_amount = Decimal('0.00')
        sale.tax_amount = Decimal('0.00')
        sale.sale_total_amount = Decimal('0.00')
        
        self._process_shipping_info(sale)
        return sale

    def _validate_and_get_customer(self):
        """التحقق من صحة العميل وإرجاعه"""
        customer_id = self.request.POST.get('sale_customer')
        if not customer_id:
            raise ValidationError('يجب اختيار عميل صحيح')
            
        try:
            return User.objects.get(id=int(customer_id))
        except (User.DoesNotExist, ValueError):
            raise ValidationError('العميل المحدد غير موجود')

    def _process_shipping_info(self, sale):
        """معالجة معلومات الشحن إذا وجدت"""
        shipping_company = self.request.POST.get('sale_shipping_company')
        if shipping_company:
            try:
                company = Shipping_com_m.objects.get(id=int(shipping_company)) # تأكد من الاسم الصحيح
                sale.sale_shipping_company = company
                sale.sale_shipping_num = self.request.POST.get('sale_shipping_num', '')
            except Shipping_com_m.DoesNotExist:
                raise ValidationError('شركة الشحن المحددة غير موجودة')
        else:
            sale.sale_shipping_company = None # تأكد من مسح الحقل إذا لم يتم اختياره

    def _process_sale_items(self, sale):
        """معالجة عناصر الفاتورة والباركود"""
        has_items = False
        subtotal = Decimal('0.00')
        
        for i in range(1, self._get_max_items() + 1):
            product_id = self.request.POST.get(f'product_id_{i}')
            if not product_id:
                continue
                
            product, item_total = self._process_single_item(sale, i)
            has_items = True
            subtotal += item_total
        
        if not has_items:
            raise ValidationError('يجب إدخال على الأقل مادة واحدة في الفاتورة')
        
        sale.subtotal = subtotal
        sale.save() # حفظ subtotal بعد إضافة كل البنود

    def _get_max_items(self):
        """الحصول على الحد الأقصى لعدد العناصر"""
        return 41 # عدد افتراضي، يمكنك جعله ديناميكياً

    def _process_single_item(self, sale, item_index):
        """معالجة عنصر واحد من الفاتورة"""
        product = self._get_validated_product(item_index)
        quantity, unit_price = self._get_validated_quantities(item_index)
        
        # الصورة (إذا كانت موجودة في الـ request)
        image_file = self.request.FILES.get(f'sale_item_image_{item_index}')
        if image_file:
            try:
                FileUploadSecurity.validate_file(image_file)
            except ValidationError as e:
                raise ValidationError(f'الصف {item_index}: {str(e)}')
            except Exception as e:
                logger.error(f"فشل تحميل الملف للصنف {item_index}: {str(e)}", exc_info=True)
                raise ValidationError(f'الصف {item_index}: خطأ في معالجة الملف')
        
        row_total = quantity * unit_price
        
        sale_item = self._create_sale_item(sale, product, quantity, unit_price, row_total, item_index, image_file)
        self._process_item_barcodes(item_index, sale_item, quantity)
        
        return product, row_total

    def _get_validated_product(self, item_index):
        """التحقق من صحة المنتج وإرجاعه"""
        product_id = self.request.POST.get(f'product_id_{item_index}')
        try:
            return Product.objects.get(id=int(product_id))
        except (Product.DoesNotExist, ValueError):
            raise ValidationError(f'المنتج في الصف {item_index} غير موجود')

    def _get_validated_quantities(self, item_index):
        """التحقق من صحة الكميات والأسعار"""
        try:
            quantity = Decimal(self.request.POST.get(f'quantity_{item_index}', '1'))
            unit_price = Decimal(self.request.POST.get(f'unit_price_{item_index}', '0'))
            
            if quantity <= Decimal('0'):
                raise ValidationError(f'كمية المادة في الصف {item_index} يجب أن تكون أكبر من الصفر')
            if unit_price < Decimal('0'):
                raise ValidationError(f'سعر المادة في الصف {item_index} يجب أن يكون قيمة موجبة')
                
            return quantity, unit_price
        except Exception as e:
            raise ValidationError(f'قيم غير صالحة في الصف {item_index}: {str(e)}')

    def _create_sale_item(self, sale, product, quantity, unit_price, row_total, item_index, image_file):
        """إنشاء عنصر الفاتورة في قاعدة البيانات"""
        sale_item_data = {
            'sale': sale,
            'item_name': product.product_name, # أو يمكن أن يكون product.name
            'quantity': quantity,
            'unit_price': unit_price,
            'notes': self.request.POST.get(f'notes_{item_index}', ''),
            'sale_total': row_total,
            'sale_item_image': image_file # تمرير الملف مباشرة هنا
        }
        
        # إذا كان حقل 'product' موجوداً في SaleItem، أضفه
        if hasattr(SaleItem, 'product'):
            sale_item_data['product'] = product
        
        return SaleItem.objects.create(**sale_item_data)

    def _process_item_barcodes(self, item_index, sale_item, quantity):
        """معالجة الباركود الخاص بالعنصر إذا وجد"""
        for j in range(1, int(quantity) + 1):
            barcode_value = self.request.POST.get(f'barcode_{item_index}_{j}')
            if barcode_value and barcode_value.strip():
                barcode, created = Barcode.objects.get_or_create(
                    barcode_out=barcode_value.strip()
                )
                SaleItemBarcode.objects.create(
                    sale_item=sale_item,
                    barcode=barcode,
                    is_primary=(j == 1)
                )

    def _calculate_final_totals(self, sale):
        """حساب المجاميع النهائية للفاتورة"""
        try:
            discount = Decimal(self.request.POST.get('sale_global_discount', '0'))
            addition = Decimal(self.request.POST.get('sale_global_addition', '0'))
            tax_rate = Decimal(self.request.POST.get('sale_global_tax', '0'))
            
            total_after_discount = sale.subtotal - discount + addition
            tax_amount = total_after_discount * (tax_rate / Decimal('100'))
            
            sale.discount_amount = discount
            sale.addition_amount = addition
            sale.tax_amount = tax_amount
            sale.sale_total_amount = total_after_discount + tax_amount
            sale.save()
            
        except Exception as e:
            logger.error(f"خطأ في العمليات الحسابية للفاتورة: {str(e)}", exc_info=True)
            raise ValidationError(f'حدث خطأ أثناء العمليات الحسابية: {str(e)}')

    def form_invalid(self, form):
        """معالجة حالة النموذج غير الصالح"""
        self.preserved_form_data = {
            'form_data': self.request.POST.copy(),
            'form_files': {
                k: v.name for k, v in self.request.FILES.items()
            } if hasattr(self.request, 'FILES') else {}
        }
        logger.warning(f"نموذج غير صالح: {form.errors}")
        messages.error(self.request, "الرجاء تصحيح الأخطاء في النموذج: " + str(form.errors))
        return super().form_invalid(form)

@login_required
def autocomplete_customers(request):
    """وظيفة البحث التلقائي للعملاء"""
    if not request.user.has_perm('auth.view_user'):
        return JsonResponse([], safe=False)
    
    term = request.GET.get('term', '').strip()
    if term:
        customers = User.objects.filter(
            Q(username__icontains=term) | 
            Q(first_name__icontains=term) | 
            Q(last_name__icontains=term)
        ).distinct()[:10]
    else:
        customers = User.objects.all()[:10]
    
    data = [{
        "id": customer.id,
        "username": customer.username,
        "first_name": customer.first_name or '',
        "last_name": customer.last_name or '',
        "label": f"{customer.username} - {customer.first_name} {customer.last_name}"
    } for customer in customers] if customers.exists() else [{"label": "لا توجد نتائج", "value": ""}]
    
    return JsonResponse(data, safe=False)


@login_required
def autocomplete_product(request):
    """وظيفة البحث التلقائي للمنتجات"""
    if not request.user.has_perm('invoice.view_product'):
        return JsonResponse([], safe=False)
    
    term = request.GET.get('term', '').strip()
    if term:
        products = Product.objects.filter(
            Q(product_name__icontains=term) |
            Q(barcode__icontains=term)
        ).distinct()[:10]
    else:
        products = Product.objects.all()[:10]
    
    data = []
    for product in products:
        data.append({
            "id": product.id,
            "label": product.product_name,
            "value": product.product_name,
            "price": product.get_price(),
            "image": product.get_image_url() if hasattr(product, 'get_image_url') else ''
        })
    
    if not data:
        data.append({"label": "لا توجد نتائج", "value": "", "id": "", "price": 0})
    
    return JsonResponse(data, safe=False)








from django.views.generic import UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.db.models import Prefetch, Q
from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib.auth import get_user_model # استخدام get_user_model لضمان مرونة أكبر
import logging

# استيراد النماذج والفورمز الخاصة بك (تأكد من مسارات الاستيراد الصحيحة)
from .models import Sale, SaleItemBarcode, Status, Payment_method, Currency, Shipping_com_m
from .forms import SaleForm, SaleItemFormSet # تأكد من استيراد SaleItemFormSet

User = get_user_model() # الحصول على نموذج المستخدم النشط

logger = logging.getLogger(__name__)


# تأكد من استيراد نموذج Sale من المكان الصحيح
from .models import Sale

logger = logging.getLogger(__name__)


from django.views.generic import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.exceptions import PermissionDenied
import logging


from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Prefetch, Sum, Avg, Max, Count
from django.contrib import messages
from django.core.exceptions import PermissionDenied
import logging

# تأكد من استيراد النماذج الخاصة بك من المكان الصحيح
# (افترض أن جميعها في نفس التطبيق 'invoice' كما هو الحال مع Sale)
from .models import Sale, SaleItemBarcode, Status, Payment_method, Currency, Shipping_com_m

logger = logging.getLogger(__name__)





class SaleListView(LoginRequiredMixin, ListView):
    """
    View لعرض قائمة فواتير المبيعات.
    تتطلب تسجيل الدخول وتطبق منطق تصفية الفواتير بدقة بناءً على صلاحيات المستخدم:
    - المستخدمون السوبر يوزر يرون جميع الفواتير.
    - المستخدمون الذين لديهم صلاحية 'invoice.can_view_all_sales' يرون جميع الفواتير.
    - البائعون (الذين لديهم صلاحيات إضافة/تعديل/حذف الفواتير) يرون فقط الفواتير التي أنشأوها.
    - الزبائن يرون فقط الفواتير التي يكونون هم العميل فيها.
    """
    model = Sale
    template_name = 'sales/sale_list.html'
    context_object_name = 'sales'
    paginate_by = 10
    login_url = '/accounts/login/'

    def dispatch(self, request, *args, **kwargs):
        """
        يتحقق من صلاحيات المستخدم قبل عرض الصفحة.
        LoginRequiredMixin يتولى إعادة توجيه المستخدمين غير المسجلين للدخول.
        هنا نتحقق من الصلاحيات الإضافية.
        """
        user = request.user

        # السوبر يوزر يمكنه دائماً رؤية الصفحة.
        if user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        # إذا كان لدى المستخدم صلاحية 'can_view_all_sales'
        # (للمدراء أو أي دور آخر يجب أن يرى كل الفواتير)
        if user.has_perm('invoice.can_view_all_sales'):
            return super().dispatch(request, *args, **kwargs)

        # إذا كان المستخدم لديه أي من صلاحيات إضافة/تعديل/حذف الفواتير (للبائعين)
        # فهذا يعني أنه يجب أن يكون قادرًا على رؤية قائمة الفواتير، وسيتم تصفية ما يراه في get_queryset
        if user.has_perm('invoice.add_sale') or \
           user.has_perm('invoice.change_sale') or \
           user.has_perm('invoice.delete_sale'):
            return super().dispatch(request, *args, **kwargs)

        # إذا كان المستخدم مسجلاً للدخول (مثل الزبون العادي)
        # سيتم تصفية ما يراه في get_queryset ليقتصر على فواتيره الخاصة.
        if user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        
        # إذا وصل الكود إلى هنا، فهذا يعني أن المستخدم غير مسجل للدخول
        # (على الرغم من أن LoginRequiredMixin يجب أن يتعامل مع هذا)
        # أو أنه مسجل للدخول وليس لديه أي صلاحيات رؤية ذات صلة، ولا هو زبون.
        messages.error(request, "ليس لديك الصلاحية لعرض قائمة الفواتير.")
        raise PermissionDenied("ليس لديك الصلاحية لعرض هذه الصفحة.")


    def get_queryset(self):
        """
        يسترجع مجموعة الاستعلامات للفواتير بناءً على صلاحيات المستخدم:
        - سوبر يوزر أو 'can_view_all_sales': جميع الفواتير.
        - بائعون: فقط الفواتير التي أنشأوها (created_by).
        - زبائن: فقط الفواتير التي هم عملاؤها (sale_customer).
        """
        # إنشاء Prefetch object أولاً لتحسين الأداء بجلب البيانات ذات الصلة.
        try:
            barcode_prefetch = Prefetch(
                'items__saleitembarcode_set',
                queryset=SaleItemBarcode.objects.select_related('barcode'),
                to_attr='prefetched_barcodes'
            )
        except Exception as e:
            logger.error(f"Error in barcode prefetch setup: {e}", exc_info=True)
            barcode_prefetch = None

        # البدء بالكويريست الأساسي لجميع الفواتير.
        queryset = Sale.objects.all()
        
        # تطبيق select_related لجلب الكائنات المرتبطة (Foreign Keys) دفعة واحدة.
        queryset = queryset.select_related(
            'sale_customer',
            'sale_status',
            'sale_payment_method',
            'sale_currency',
            'sale_shipping_company',
            'created_by'
        )
        
        # تطبيق prefetch_related لجلب الكائنات المرتبطة (Many-to-Many أو Reverse Foreign Keys) دفعة واحدة.
        prefetch_list = ['items']
        if barcode_prefetch:
            prefetch_list.append(barcode_prefetch)
        
        queryset = queryset.prefetch_related(*prefetch_list)

        # تطبيق تصفية الفواتير بناءً على دور المستخدم وصلاحياته.
        user = self.request.user

        if user.is_superuser:
            # المستخدم السوبر يوزر يرى كل الفواتير.
            pass 
        elif user.has_perm('invoice.can_view_all_sales'):
            # المستخدمون الذين لديهم صلاحية 'can_view_all_sales' يرون كل الفواتير.
            pass
        elif user.has_perm('invoice.add_sale') or \
             user.has_perm('invoice.change_sale') or \
             user.has_perm('invoice.delete_sale'):
            # هذه هي حالة البائعين (مثل Ahmad).
            # بناءً على التوضيح، يجب أن يروا الفواتير التي أنشأوها فقط.
            queryset = queryset.filter(created_by=user)
        else:
            # المستخدمون الآخرون (مثل الزبائن العاديين مثل Ali) يرون فقط الفواتير
            # التي يكونون هم العميل فيها.
            queryset = queryset.filter(sale_customer=user)

        # تطبيق الفلاتر الإضافية (البحث، التاريخ، الحالة، إلخ) والفرز.
        queryset = self._apply_filters(queryset)
        
        return queryset

    def _apply_filters(self, queryset):
        """
        تطبق الفلاتر والفرز المستندة إلى معلمات GET على مجموعة الاستعلامات.
        """
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(uniqueId__icontains=search) |
                Q(sale_customer__username__icontains=search) |
                Q(sale_customer_phone__icontains=search) |
                Q(sale_shipping_num__icontains=search) |
                Q(items__saleitembarcode__barcode__barcode_out__icontains=search)
            ).distinct()
        
        status_filter = self.request.GET.get('status')
        if status_filter:
            queryset = queryset.filter(sale_status_id=status_filter)
        
        date_from = self.request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(sale_date__gte=date_from)
        
        date_to = self.request.GET.get('date_to')
        if date_to:
            queryset = queryset.filter(sale_date__lte=date_to)
        
        payment_method = self.request.GET.get('payment_method')
        if payment_method:
            queryset = queryset.filter(sale_payment_method_id=payment_method)
        
        # الفرز
        sort_column = self.request.GET.get('sort')
        if sort_column:
            sort_direction = self.request.GET.get('dir', 'asc')
            if sort_direction == 'desc':
                sort_column = f'-{sort_column}'
            queryset = queryset.order_by(sort_column)
        else:
            queryset = queryset.order_by('-sale_date') # الفرز الافتراضي
        
        return queryset

    def get_context_data(self, **kwargs):
        """
        إعداد البيانات الأساسية للقالب، بما في ذلك إحصائيات الفواتير.
        """
        context = super().get_context_data(**kwargs)
        
        # نحصل على sales_queryset من get_queryset لضمان تطبيق الفلاتر
        sales_queryset = self.get_queryset()
        try:
            stats = sales_queryset.aggregate(
                total_sales=Sum('sale_total_amount'),
                avg_sale=Avg('sale_total_amount'),
                max_sale=Max('sale_total_amount'),
                count=Count('id')
            )
        except Exception as e:
            logger.error(f"Error calculating stats in SaleListView: {e}", exc_info=True)
            stats = {'total_sales': 0, 'avg_sale': 0, 'max_sale': 0, 'count': 0}

        context.update({
            'page_title': 'قائمة فواتير المبيعات',
            'statuses': Status.objects.all(),
            'payment_methods': Payment_method.objects.all(),
            'currencies': Currency.objects.all(),
            'total_sales': stats['total_sales'] or 0,
            'avg_sale': stats['avg_sale'] or 0,
            'max_sale': stats['max_sale'] or 0,
            'sales_count': stats['count'],
            'current_sort': self.request.GET.get('sort'),
            'current_dir': self.request.GET.get('dir'),
        })
        return context




from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.db.models import Prefetch, Q
from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib.auth import get_user_model
import logging

# استيراد النماذج والفورمز الخاصة بك (تأكد من مسارات الاستيراد الصحيحة)
from .models import Sale, SaleItemBarcode, Status, Payment_method, Currency, Shipping_com_m
from .forms import SaleForm, SaleItemFormSet # تأكد من استيراد SaleItemFormSet

User = get_user_model()

logger = logging.getLogger(__name__)


#=============================
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.forms import inlineformset_factory
from django.urls import reverse
from django.contrib import messages
from django.http import Http404, JsonResponse
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError # استوردها لاستخدامها في التحقق

# تأكد من استيراد النماذج والفورمز الصحيحة
from .models import Sale, SaleItem, Payment_method, Currency, Status, Shipping_com_m, Product
from .forms import SaleForm, SaleItemForm # <--- تأكد من استيراد SaleItemForm هنا
from django.contrib.auth.models import User # أو النموذج المخصص للمستخدم الخاص بك

# تعريف FormSet باستخدام SaleItemForm الذي قدمته
SaleItemFormSet = inlineformset_factory(
    Sale,
    SaleItem,
    form=SaleItemForm, # <--- استخدام SaleItemForm المخصص
    extra=1,
    can_delete=True,
    min_num=1, # تأكد أن هذا يطابق ما تريده، إذا أردت 0 لعدم وجود مواد، غيّره
    validate_min=True,
)

class SaleUpdateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = 'sales/sale_create.html'
    permission_required = ('invoice.change_sale',)

    def get_object(self):
        sale_pk = self.kwargs.get('pk')
        sale = get_object_or_404(Sale, pk=sale_pk)

        if sale.created_by != self.request.user and not self.request.user.has_perm('invoice.can_view_all_sales'):
            messages.error(self.request, _("ليس لديك صلاحية لتعديل هذه الفاتورة."))
            raise Http404(_("الفاتورة غير موجودة أو ليس لديك صلاحية الوصول إليها."))
            
        return sale

    def get_context_data(self, **kwargs):
        context = kwargs

        if 'instance' not in context:
            context['instance'] = self.get_object()

        if 'form' not in context:
            context['form'] = SaleForm(instance=context['instance'])
            
        if 'formset' not in context:
            context['formset'] = SaleItemFormSet(instance=context['instance'], prefix='items')

        context['payment_methods'] = Payment_method.objects.all()
        context['currencies'] = Currency.objects.all()
        context['statuses'] = Status.objects.all()
        context['shipping_companies'] = Shipping_com_m.objects.all()

        context['is_update_view'] = True
        context['sale_instance'] = context['instance']

        # إضافة طباعة لتصحيح الأخطاء عند التحميل الأولي
        print("\n--- GET Request Context Data ---")
        print(f"Sale Instance PK: {context['sale_instance'].pk}")
        print("Formset forms initial data:")
        for form_item in context['formset']:
            print(f"  Prefix: {form_item.prefix}, Instance PK: {form_item.instance.pk if form_item.instance else 'New'}, Item Name: {form_item.instance.item_name if form_item.instance else 'N/A'}")
            print(f"  Initial: {form_item.initial}")
        print("-------------------------------\n")

        return context

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        sale_instance = self.get_object()
        
        form = SaleForm(request.POST, request.FILES, instance=sale_instance)
        formset = SaleItemFormSet(request.POST, request.FILES, instance=sale_instance, prefix='items')

        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    sale_instance = form.save(commit=False)
                    
                    customer_id = request.POST.get('sale_customer')
                    if customer_id:
                        try:
                            sale_instance.sale_customer = User.objects.get(pk=customer_id)
                        except User.DoesNotExist:
                            messages.error(request, _("العميل المحدد غير موجود."))
                            return render(request, self.template_name, self.get_context_data(form=form, formset=formset, instance=sale_instance))
                    else:
                        messages.error(request, _("يجب اختيار عميل."))
                        return render(request, self.template_name, self.get_context_data(form=form, formset=formset, instance=sale_instance))

                    sale_instance.save()
                    
                    # حفظ الـ SaleItems عبر الـ formset
                    # SaleItemFormSet سيعالج الآن منطق التحقق من item_name والباركودات
                    # بناءً على تعريف SaleItemForm
                    
                    # for item_instance in formset.save(commit=False): # هذا كان تكرار لبعض المنطق
                    #     item_instance.sale = sale_instance
                    #     # لا داعي لمعالجة الباركودات أو item_name هنا يدوياً إذا كانت SaleItemForm تقوم بذلك
                    #     # ومع ذلك، إذا كانت هناك حاجة لتحديث SaleItem.product_id (Foreign Key) 
                    #     # بناءً على قيمة تُرسل من الواجهة ولم تكن part of SaleItemForm's fields،
                    #     # فستحتاج إلى معالجتها يدوياً هنا قبل save()
                    #     item_instance.save()
                    
                    # بدلاً من ذلك، دع Formset يقوم بالحفظ.
                    # Formset.save() يعود بقائمة من الكائنات التي تم تعديلها/إنشائها.
                    # الكائنات المحذوفة يتم حذفها تلقائياً إذا تم تحديدها.

                    # في حالتك، بما أنك قمت بوضع 'item_name' كـ HiddenInput في الفورم
                    # وقمت بتعيينه من Autocomplete في الـ JavaScript، فإن هذا الاسم سيصل مباشرةً
                    # إلى حقل 'item_name' في SaleItemForm، والذي بدوره سيحفظ في SaleItem.
                    # هذا يعني أنك لست بحاجة إلى منطق product_id في View على الإطلاق.
                    
                    # حفظ البنود الجديدة والمعدلة
                    formset.save() # هذا سيهتم بـ `sale` ForeignKey أيضاً

                    # معالجة البنود التي تم تعليمها للحذف
                    # هذا الجزء صحيح ويجب أن يكون بعد حفظ البنود الجديدة/المعدلة
                    # هذا سيتم معالجته بواسطة formset.save() تلقائياً أيضاً إذا تم تمكين can_delete
                    # ولكن إذا كنت تريد القيام بذلك يدوياً:
                    # for item_form in formset.deleted_forms:
                    #     item_form.instance.delete()

                    sale_instance.calculate_totals()
                    
                    messages.success(request, _("تم تحديث الفاتورة بنجاح!"))
                    return redirect(reverse('sale_detail', kwargs={'pk': sale_instance.pk}))

            except Exception as e:
                messages.error(request, _(f"حدث خطأ أثناء تحديث الفاتورة: {e}"))
        
        # إذا كان هناك أخطاء في الفورم أو الفورمست، أعد عرض الصفحة مع الأخطاء
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{form.fields[field].label}: {error}")
        for i, formset_form in enumerate(formset):
            if formset_form.errors:
                messages.error(request, _(f"أخطاء في البند رقم {i+1}:"))
                for field, errors in formset_form.errors.items():
                    messages.error(request, f"- {formset_form.fields[field].label}: {error}")
            if formset_form.non_field_errors():
                for error in formset_form.non_field_errors():
                    messages.error(request, error)
        
        # إضافة طباعة لتصحيح الأخطاء عند وجود أخطاء في POST
        print("\n--- POST Request (Errors) Context Data ---")
        print("Form errors:", form.errors)
        print("Formset errors:")
        for form_item in formset:
            print(f"  Prefix: {form_item.prefix}, Errors: {form_item.errors}")
        print("------------------------------------------\n")

        return render(request, self.template_name, self.get_context_data(form=form, formset=formset, instance=sale_instance))

# Autocomplete views remain the same
class AutocompleteCustomers(View):
    def get(self, request, *args, **kwargs):
        term = request.GET.get('term', '')
        customers = User.objects.filter(username__icontains=term).values('id', 'username')
        results = []
        for customer in customers:
            results.append({'id': customer['id'], 'label': customer['username'], 'value': customer['username']})
        return JsonResponse(results, safe=False)


# View لإكمال اسم المنتج تلقائياً
class AutocompleteProduct(View):
    def get(self, request, *args, **kwargs):
        term = request.GET.get('term', '')
        products = Product.objects.filter(product_name__icontains=term).values('id', 'product_name', 'price')
        results = []
        for product in products:
            image_url = '' # يمكنك جلب URL الصورة إذا كانت متاحة في نموذج Product
            results.append({
                'id': product['id'],
                'label': product['product_name'],
                'value': product['product_name'],
                'price': float(product['price']),
                'image': image_url
            })
        return JsonResponse(results, safe=False)






class SaleDetailView(LoginRequiredMixin, DetailView):
    """
    View لعرض تفاصيل فاتورة مبيعات معينة.
    تتطلب تسجيل الدخول وتطبق منطق رؤية الفاتورة بناءً على الدور.
    - السوبر يوزر والمدراء يرون أي فاتورة.
    - البائعون يرون الفواتير التي أنشأوها فقط.
    - الزبائن يرون الفواتير التي هم العميل فيها فقط.
    """
    model = Sale
    template_name = 'sales/sale_detail.html'
    context_object_name = 'sale'
    login_url = '/accounts/login/'

    def dispatch(self, request, *args, **kwargs):
        """
        يتحقق من أن المستخدم لديه إذن كافٍ لعرض تفاصيل الفاتورة.
        """
        user = request.user
        # السماح بالوصول لجميع المستخدمين الذين سيتم تصفية رؤيتهم في get_queryset
        # أو الذين لديهم صلاحية عامة للرؤية.
        if user.is_superuser or \
           user.has_perm('invoice.can_view_all_sales') or \
           user.has_perm('invoice.add_sale') or \
           user.has_perm('invoice.change_sale') or \
           user.has_perm('invoice.delete_sale') or \
           user.is_authenticated: # السماح للمستخدمين المسجلين بالوصول ليتم تصفيتهم لاحقاً
            return super().dispatch(request, *args, **kwargs)
        
        messages.error(request, "ليس لديك الصلاحية لعرض تفاصيل الفاتورة.")
        raise PermissionDenied("ليس لديك الصلاحية لعرض هذه الصفحة.")

    def get_queryset(self):
        """
        يسترجع مجموعة الاستعلامات للفواتير بناءً على صلاحيات المستخدم
        (بائع: يرى ما أنشأه، زبون: يرى ما هو عميله).
        """
        queryset = super().get_queryset()
        
        # تحسينات Preloading للحد من استعلامات قاعدة البيانات
        try:
            barcode_prefetch = Prefetch(
                'items__saleitembarcode_set',
                queryset=SaleItemBarcode.objects.select_related('barcode'),
                to_attr='prefetched_barcodes'
            )
            # استخدام Prefetch objects و select_related لتحسين الأداء
            queryset = queryset.prefetch_related(barcode_prefetch, 'items')
        except Exception as e:
            logger.error(f"Error in barcode prefetch setup in SaleDetailView: {e}", exc_info=True)
            queryset = queryset.prefetch_related('items') # في حالة الخطأ، استمر بدون الباركود

        queryset = queryset.select_related(
            'sale_customer',
            'sale_status',
            'sale_payment_method',
            'sale_currency',
            'sale_shipping_company',
            'created_by'
        )

        user = self.request.user

        if user.is_superuser or user.has_perm('invoice.can_view_all_sales'):
            # السوبر يوزر والمدراء يرون جميع الفواتير.
            pass # لا تصفية إضافية
        elif user.has_perm('invoice.add_sale') or \
             user.has_perm('invoice.change_sale') or \
             user.has_perm('invoice.delete_sale'):
            # البائعون يرون الفواتير التي أنشأوها فقط.
            queryset = queryset.filter(created_by=user)
        elif user.is_authenticated:
            # الزبون العادي يرى فقط الفواتير المرتبطة به كـ sale_customer.
            queryset = queryset.filter(sale_customer=user)
        else:
            # أي مستخدم آخر غير مسموح له بالوصول.
            # (هذه الحالة يجب أن يتم التعامل معها بواسطة LoginRequiredMixin أو PermissionDenied في dispatch).
            return queryset.none() # لا ترجع أي كائنات

        return queryset

    def get_context_data(self, **kwargs):
        """
        يضيف عنوان الصفحة إلى السياق.
        """
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'تفاصيل الفاتورة'
        return context


class SaleDeleteView(LoginRequiredMixin, DeleteView):
    """
    View لحذف فاتورة مبيعات موجودة.
    تتطلب تسجيل الدخول وتطبق منطق صلاحيات الحذف بناءً على الدور:
    - السوبر يوزر والمدراء (حملة صلاحية 'can_view_all_sales') يمكنهم حذف أي فاتورة.
    - البائعون (حملة صلاحية 'delete_sale') يمكنهم حذف الفواتير التي أنشأوها فقط.
    - الآخرون لا يمكنهم الحذف.
    """
    model = Sale
    template_name = 'sales/sale_confirm_delete.html'
    success_url = reverse_lazy('sale_list')
    login_url = '/accounts/login/'
    
    # لا نستخدم permission_required مباشرة هنا لأن get_queryset ستتعامل مع التصفية الدقيقة
    # ولكن يمكن استخدامها للتحقق الأولي من أن المستخدم لديه صلاحية 'delete_sale' على الأقل.
    # ومع ذلك، سنقوم بتطبيق منطق أكثر تفصيلاً في dispatch و get_queryset.

    def dispatch(self, request, *args, **kwargs):
        """
        يتحقق من أن المستخدم لديه إذن كافٍ لمحاولة حذف الفاتورة.
        """
        user = request.user
        
        # السوبر يوزر يمكنه دائماً محاولة الحذف.
        if user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        
        # إذا كان لديه صلاحية رؤية جميع المبيعات (مدير)، يمكنه الحذف.
        if user.has_perm('invoice.can_view_all_sales'):
            return super().dispatch(request, *args, **kwargs)

        # إذا كان لدى المستخدم صلاحية 'invoice.delete_sale' (للبائعين)، يمكنه محاولة الحذف.
        # سيتم تحديد ما يمكنه حذفه بالفعل في get_queryset.
        if user.has_perm('invoice.delete_sale'):
            return super().dispatch(request, *args, **kwargs)
        
        # إذا لم يكن المستخدم سوبر يوزر، أو لديه صلاحية عامة، أو صلاحية الحذف،
        # يمنع من الوصول.
        messages.error(request, "ليس لديك صلاحية لحذف الفواتير.")
        raise PermissionDenied("ليس لديك الصلاحية لحذف هذه الفاتورة.")

    def get_queryset(self):
        """
        يسترجع مجموعة الاستعلامات للفواتير التي يمكن للمستخدم حذفها.
        """
        queryset = super().get_queryset()
        user = self.request.user

        if user.is_superuser:
            # السوبر يوزر يمكنه حذف أي فاتورة.
            return queryset
        elif user.has_perm('invoice.can_view_all_sales'):
            # المدراء يمكنهم حذف أي فاتورة.
            return queryset
        elif user.has_perm('invoice.delete_sale'):
            # البائعون الذين لديهم صلاحية 'delete_sale' يمكنهم حذف
            # الفواتير التي أنشأوها فقط.
            return queryset.filter(created_by=user)
        else:
            # أي مستخدم آخر لا يمكنه حذف أي فواتير.
            return queryset.none()

    def delete(self, request, *args, **kwargs):
        """
        يتجاوز دالة الحذف القياسية لإضافة رسائل تأكيد.
        """
        try:
            self.object = self.get_object() # الحصول على الكائن بناءً على get_queryset
            self.object.delete()
            logger.info(f"تم حذف الفاتورة رقم {self.object.id} بواسطة {request.user}")
            messages.success(request, f'تم حذف الفاتورة رقم {self.object.uniqueId} بنجاح.')
            return redirect(self.success_url)
        except PermissionDenied:
            messages.error(request, "ليس لديك الصلاحية لحذف هذه الفاتورة.")
            raise # إعادة إطلاق الخطأ بعد إضافة الرسالة
        except Exception as e:
            logger.error(f"خطأ غير متوقع أثناء حذف الفاتورة: {e}", exc_info=True)
            messages.error(request, f'حدث خطأ أثناء حذف الفاتورة: {e}')
            return redirect(self.success_url) # أو إعادة التوجيه إلى صفحة الخطأ

















#============================

@csrf_exempt
def search_customers(request):
    if request.method == 'GET':
        q = request.GET.get('q', '')
        
        # البحث في username أو first_name أو last_name
        customers = User.objects.filter(
            Q(username__icontains=q) |
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q)
        )[:10].values('id', 'username', 'first_name', 'last_name')
        
        results = []
        for customer in customers:
            full_name = f"{customer['first_name'] or ''} {customer['last_name'] or ''}".strip()
            display_name = customer['username'] + (f" ({full_name})" if full_name else "")
            
            results.append({
                'id': customer['id'],
                'username': customer['username'],
                'phone': '',  # يمكنك إضافة حقل الهاتف إذا كان موجوداً
                'address': '',  # يمكنك إضافة حقل العنوان إذا كان موجوداً
                'display_name': display_name
            })
        
        return JsonResponse(list(results), safe=False)
    return JsonResponse([], safe=False)





def search_products(request):
    query = request.GET.get('q', '')  # لاحظ: نستخدم 'q' للتماشي مع الجافاسكربت
    if query:
        products = Product.objects.filter(product_name__icontains=query)[:5]
    else:
        products = Product.objects.all()[:5]

    if products.exists():
        results = [{'label': product.product_name, 'value': product.product_name} for product in products]
    else:
        results = [{'label': 'لا توجد نتائج', 'value': ''}]
    
    return JsonResponse(results, safe=False)



