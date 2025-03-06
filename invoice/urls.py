from django.urls import path
from .views import (
    HomeView, InvoiceListView, InvoiceCreateView, InvoiceUpdateView, InvoiceDeleteView, InvoiceDetailView,
    InvoiceItemCreateView, InvoiceItemUpdateView, InvoiceItemDeleteView,
    PriceTypeListView, PriceTypeCreateView, PriceTypeUpdateView, PriceTypeDeleteView,PriceTypeDetailView,
    ProductListView, ProductCreateView, ProductUpdateView, ProductDeleteView, ProductDetailView,
    autocomplete_customers, autocomplete_products , ShippingListView , ShippingCreateView , ShippingUpdateView ,
    ShippingDeleteView , ShippingDetailView , CurrencyListView , CurrencyCreateView , CurrencyUpdateView ,
    CurrencyDeleteView , CurrencyDetailView
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


    # Autocomplete URLs
    path('autocomplete-customers/', autocomplete_customers, name='autocomplete_customers'),
    path('autocomplete-products/', autocomplete_products, name='autocomplete_products'),
]