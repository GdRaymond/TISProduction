from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from authentication.forms import SignupForm
from django.contrib.auth import login

# Create your views here.
def signup(request):
    if request.method=="POST":
        form=SignupForm(request.POST)
        if form.is_valid():
            username=form.cleaned_data.get('username')
            password=form.cleaned_data.get('password')
            email=form.cleaned_data.get('email')
            User.objects.create_user(username=username,password=password,email=email)
            user=authenticate(username=username,password=password)
            login(request,user=user)
            return redirect('/')
        else:
            return render(request,'authentication\signup.html',{'form':form})
    else:
        return render(request,'authentication\signup.html',{'form':SignupForm()})

