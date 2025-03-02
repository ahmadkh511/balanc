from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View  # أضف هذا الاستيراد



def home(request):
    return render(request, 'accounts/home.html')





def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # تسجيل الدخول تلقائيًا بعد التسجيل
            return redirect('accounts:login')  # إعادة التوجيه إلى صفحة تسجيل الدخول
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})



