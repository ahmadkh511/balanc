from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *

from django.contrib.auth.views import LogoutView
from django.views.generic import CreateView
from .forms import CustomUserCreationForm

from .views import home, register

app_name = 'accounts'

urlpatterns = [
    path('', home, name='home'),

    # مسارات الحسابات
    path('accounts/login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(template_name='accounts/logout.html'), name='logout'),

    path('accounts/register/', CreateView.as_view(
        template_name='accounts/register.html',
        form_class=CustomUserCreationForm,
        success_url='accounts:login/'  # توجيه المستخدم إلى صفحة تسجيل الدخول بعد التسجيل
    ), name='register'),




    
    # هو اسم القالب الذي يعرض النموذج الذي ندخل به الايمل المراد استعدادة كلمة المرور الخاص به
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),

    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),


    #هذا القالب يعرض نموذجًا لإدخال كلمة المرور الجديدة وتأكيدها   <uidb64>: هو معرف المستخدم المشفر باستخدام Base64.   <token>: هو رمز الأمان الذي يتم إنشاؤه لضمان صحة الطلب.
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),


    # password_reset_complete.html إذا كانت البيانات صحيحة، يتم تحديث كلمة المرور وتوجيه المستخدم إلى صفحة .
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),



    
    
    
    


]


