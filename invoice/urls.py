from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    HomeView, InvoiceListView, InvoiceCreateView, InvoiceUpdateView, InvoiceDeleteView, InvoiceDetailView,
    InvoiceItemCreateView, InvoiceItemUpdateView, InvoiceItemDeleteView,
    PriceTypeListView, PriceTypeCreateView, PriceTypeUpdateView, PriceTypeDeleteView,PriceTypeDetailView,
    ProductListView, ProductCreateView, ProductUpdateView, ProductDeleteView, ProductDetailView,
    autocomplete_customers, autocomplete_products , ShippingListView , ShippingCreateView , ShippingUpdateView ,
    ShippingDeleteView , ShippingDetailView , CurrencyListView , CurrencyCreateView , CurrencyUpdateView ,
    CurrencyDeleteView , CurrencyDetailView , StatusListView , StatusCreateView , StatusUpdateView , StatusDeleteView , StatusDetailView ,
    PurchaseListView , PurchaseCreateView , PurchaseUpdateView , PurchaseDeleteView , PurchaseDetailView ,
    export_purchase_pdf , send_purchase_email  , 
    autocomplete_suppliers , autocomplete_items , autocomplete_barcodes , 
    export_invoice_pdf, export_invoice_excel, send_invoice_email ,  barcodeListView , barcodeCreateView ,
    barcodeUpdateView , barcodeDeleteView , barcodeDetailView ,
    payment_methodListView , payment_methodCreateView , payment_methodUpdateView , payment_methodDeleteView , payment_methodDetailView

)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),

    # Invoice URLs
    path('invoices/', InvoiceListView.as_view(), name='invoice_list'),
    path('invoices/create/', InvoiceCreateView.as_view(), name='invoice_create'),
    path('invoices/<int:pk>/', InvoiceDetailView.as_view(), name='invoice_detail'),
    path('invoices/<int:pk>/update/', InvoiceUpdateView.as_view(), name='invoice_update'),
    path('invoices/<int:pk>/delete/', InvoiceDeleteView.as_view(), name='invoice_delete'),

    # InvoiceItem URLs
    path('invoiceitems/create/', InvoiceItemCreateView.as_view(), name='invoiceitem_create'),
    path('invoiceitems/<int:pk>/update/', InvoiceItemUpdateView.as_view(), name='invoiceitem_update'),
    path('invoiceitems/<int:pk>/delete/', InvoiceItemDeleteView.as_view(), name='invoiceitem_delete'),


    # Purchase 
    path('purchase/', PurchaseListView.as_view(), name='purchase_list'),
    path('purchase/create/', PurchaseCreateView.as_view(), name='purchase_create'),
    path('purchase/<int:pk>/update/', PurchaseUpdateView.as_view(), name='purchase_update'),
    path('purchase/<int:pk>/delete/', PurchaseDeleteView.as_view(), name='purchase_delete'),
    path('purchase/<int:pk>/', PurchaseDetailView.as_view(), name='purchase_detail'),


    # purchaseitems URLs
    path('purchaseitems/create/', PurchaseCreateView.as_view(), name='purchaseitems_create'),
    path('purchaseitems/<int:pk>/update/', PurchaseUpdateView.as_view(), name='purchaseitems_update'),
    path('purchaseitems/<int:pk>/delete/', PurchaseDeleteView.as_view(), name='purchaseitems_delete'),
    path('purchaseitems/<int:pk>/', PurchaseDetailView.as_view(), name='purchaseitems_detail'),


    # Barcode URLs

    path('barcode/', barcodeListView.as_view(), name='barcode_list'),
    path('barcode/create/', barcodeCreateView.as_view(), name='barcode_create'),
    path('barcode/<int:pk>/', barcodeDetailView.as_view(), name='barcode_detail'),
    path('barcode/<int:pk>/update/', barcodeUpdateView.as_view(), name='barcode_update'),
    path('barcode/<int:pk>/delete/', barcodeDeleteView.as_view(), name='barcode_delete'),



    # Product URLs
    path('products/', ProductListView.as_view(), name='product_list'),
    path('products/create/', ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('products/<int:pk>/update/', ProductUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),


    # Shipping URLs
    path('shipping/', ShippingListView.as_view(), name='shipping_list'),
    path('shipping/create/', ShippingCreateView.as_view(), name='shipping_create'),
    path('shipping/<int:pk>/update/', ShippingUpdateView.as_view(), name='shipping_update'),
    path('shipping/<int:pk>/delete/', ShippingDeleteView.as_view(), name='shipping_delete'),
    path('shipping/<int:pk>/', ShippingDetailView.as_view(), name='shipping_detail'),


    # Status URLs
    path('status/', StatusListView.as_view(), name='status_list'),
    path('status/create/', StatusCreateView.as_view(), name='status_create'),
    
    path('status/<int:pk>/update/', StatusUpdateView.as_view(), name='status_update'),
    path('status/<int:pk>/delete/', StatusDeleteView.as_view(), name='status_delete'),
    path('status/<int:pk>/', StatusDetailView.as_view(), name='status_detail'),



    # PriceType URLs
    path('pricetypes/', PriceTypeListView.as_view(), name='pricetype_list'),
    path('pricetypes/create/', PriceTypeCreateView.as_view(), name='pricetype_create'),
    path('pricetypes/<int:pk>/update/', PriceTypeUpdateView.as_view(), name='pricetype_update'),
    path('pricetypes/<int:pk>/delete/', PriceTypeDeleteView.as_view(), name='pricetype_delete'),
    path('pricetypes/<int:pk>/', PriceTypeDetailView.as_view(), name='pricetype_detail'),


    # Currency URLs
    path('currency/', CurrencyListView.as_view(), name='currency_list'),
    path('currency/create/', CurrencyCreateView.as_view(), name='currency_create'),
    
    path('currency/<int:pk>/update/', CurrencyUpdateView.as_view(), name='currency_update'),
    path('currency/<int:pk>/delete/', CurrencyDeleteView.as_view(), name='currency_delete'),
    path('currency/<int:pk>/', CurrencyDetailView.as_view(), name='currency_detail'),



    # Payment_method URLs
    path('payment_method/', payment_methodListView.as_view(), name='payment_method_list'),
    path('payment_method/create/', payment_methodCreateView.as_view(), name='payment_method_create'),
    path('payment_method/<int:pk>/update/', payment_methodUpdateView.as_view(), name='payment_method_update'),
    path('payment_method/<int:pk>/delete/', payment_methodDeleteView.as_view(), name='payment_method_delete'),
    path('payment_method/<int:pk>/', payment_methodDetailView.as_view(), name='payment_method_detail'),





    # Autocomplete URLs
    path('autocomplete-customers/', autocomplete_customers, name='autocomplete_customers'),
    path('autocomplete-products/', autocomplete_products, name='autocomplete_products'),

     # Autocomplete URLs  Purchase

    path('invoice/<int:pk>/pdf/', export_invoice_pdf, name='export_invoice_pdf'),
    path('invoice/<int:pk>/excel/', export_invoice_excel, name='export_invoice_excel'),
    path('invoice/<int:pk>/email/', send_invoice_email, name='send_invoice_email'),


    path('purchase/<int:pk>/export-pdf/', export_purchase_pdf, name='export_purchase_pdf'),
    path('purchase/<int:pk>/send-email/', send_purchase_email, name='send_purchase_email'),
    #path('purchase/<int:pk>/export-excel/', export_purchase_excel, name='export_purchase_exce'),

    
    path('autocomplete-suppliers/', autocomplete_suppliers, name='autocomplete_suppliers'),
    path('autocomplete-items/', autocomplete_items, name='autocomplete_items'),
    path('autocomplete/barcodes/', autocomplete_barcodes, name='autocomplete_barcodes'),




    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]