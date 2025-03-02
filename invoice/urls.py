from django.urls import path

from .views import (
    HomeView ,
    InvoiceListView, InvoiceCreateView, InvoiceUpdateView, InvoiceDeleteView, InvoiceDetailView,
    InvoiceItemCreateView, InvoiceItemUpdateView, InvoiceItemDeleteView,
    PriceTypeListView, PriceTypeCreateView, PriceTypeUpdateView, PriceTypeDeleteView ,
    ProductListView, ProductCreateView, ProductUpdateView, ProductDeleteView, ProductDetailView ,
    autocomplete_customers
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

    # PriceType URLs
    path('pricetypes/', PriceTypeListView.as_view(), name='pricetype_list'),
    path('pricetypes/create/', PriceTypeCreateView.as_view(), name='pricetype_create'),
    path('pricetypes/<int:pk>/update/', PriceTypeUpdateView.as_view(), name='pricetype_update'),
    path('pricetypes/<int:pk>/delete/', PriceTypeDeleteView.as_view(), name='pricetype_delete'),



    path('create/', InvoiceCreateView.as_view(), name='invoice_create'),
    path('autocomplete-customers/', autocomplete_customers, name='autocomplete_customers'),
]





