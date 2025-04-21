from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View    # أضف هذا الاستيراد
from django.views.generic import TemplateView 

from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy


def home(request):
    return render(request, 'home.html')


class TermsView(TemplateView):
    template_name = 'accounts/terms.html'


class CustomLogoutView(LogoutView):
    # تحديد الـ URL الذي سيتم إعادة التوجيه إليه بعد تسجيل الخروج
    next_page = reverse_lazy('home')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # تسجيل الدخول تلقائيًا بعد التسجيل
            return redirect('login')  # إعادة التوجيه إلى صفحة تسجيل الدخول
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


