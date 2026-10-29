from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CreateUserForm


def registerPage(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'帳號「{username}」已建立，請進行登入！')
            return redirect('login')
    else:
        form = CreateUserForm()

    context = {
        'form': form,
    }
    return render(request, 'user/register.html', context)


def loginPage(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.warning(request, '您的帳號或是密碼不正確！')

    return render(request, 'user/login.html')


def logoutUser(request):
    logout(request)
    messages.info(request, '您已安全登出系統。')
    return redirect('login')
