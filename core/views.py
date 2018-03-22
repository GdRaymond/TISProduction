from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from core.forms import ProfileForm
from django.contrib import messages
from django.conf import settings as django_settings
from PIL import Image
import os

# Create your views here.
def home(request):
    if request.user.is_authenticated:
        return render(request,"authentication/welcome.html",{"user":request.user})
    else:
        return render(request,"core/cover.html",{"next":"/"})

@login_required
def profile(request,username):
    page_user=get_object_or_404(User,username=username)
    return render(request,'core/profile.html',{'page_user':page_user})

@login_required
def settings(request):
    print('start in settings')
    user=request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            user.first_name=form.cleaned_data.get('first_name')
            user.last_name=form.cleaned_data.get('last_name')
            user.email=form.cleaned_data.get('email')
            user.profile.job_title=form.cleaned_data.get('job_title')
            user.profile.url=form.cleaned_data.get('url')
            user.profile.location=form.cleaned_data.get('location')
            user.save()
            messages.add_message(request,messages.SUCCESS,'You have successfully edited the user')
    else:
        form=ProfileForm(instance=user,initial={'job_title':user.profile.job_title,'email':user.email,
                                                'url':user.profile.url,'location':user.profile.location})
    return render(request,'core/settings.html',{'form':form})

@login_required
def picture(request):
    uploaded_picture=False
    try:
        if request.GET.get('uploaded_picture')=='uploaded':
            uploaded_picture=True
    except Exception:
        pass
    return render(request,'core/picture.html',{'uploaded_picture':uploaded_picture})

@login_required
def upload_picture(request):
    profile_pictures=django_settings.MEDIA_ROOT+'/profile_pictures/'
    if not os.path.exists(profile_pictures):
        os.makedirs(profile_pictures)
    filename=profile_pictures+request.user.username+'_tmp.jpg'
    f=request.FILES['picture']
    with open(filename,'wb') as destination:
        for chunk in f.chunks:
            destination.write(chunk)
    im=Image.open(filename)
    width,height=im.size
    if width>350:
        new_width=350
        new_height=(350/width)*height
        new_size=new_width,new_height
        im.thumbnail(new_size,Image.ANTIALIAS)
        im.save(filename)
    return redirect('/settings/picture/?uploaded_picture=uploaded')

@login_required
def save_picture(request):
    x=int(request.POST.get('x'))
    y=int(request.POST.get('y'))
    w=int(request.POST.get('w'))
    h=int(request.POST.get('h'))
    profile_pictures=django_settings.MEDIA_ROOT+'/profile_pictures/'
    tmp_filename=profile_pictures+request.user.username+'_tmp.jpg'
    filename=profile_pictures+request.user.username+'.jpg'
    im_tmp=Image.open(tmp_filename)
    croped_im=im_tmp.crop(x+w,y+h)
    croped_im.thumbnail((200,200),Image.ANTIALIAS)
    croped_im.save(filename)
    return redirect('/settings/picture/')