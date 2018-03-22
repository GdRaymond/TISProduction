from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from TISProduction import settings
import os.path
import hashlib
import urllib

# Create your models here.
class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    location=models.CharField(max_length=50,null=True,blank=True)
    url=models.CharField(max_length=50,null=True,blank=True)
    job_title=models.CharField(max_length=50,null=True,blank=True)

    class Meta:
        db_table="auth_profile"

    def __str__(self):
        print(self.user.username)

    def get_screen_name(self):
        try:
            if self.user.get_full_name():
                return self.user.get_full_name()
            else:
                return self.user.username
        except Exception:
            return self.user.username

    def get_picture(self):
        no_picture='http://trybootcamp.vitorfs.com/static/img/user.png'
        try:
            file_name=settings.MEDIA_ROOT+'/profile_picture/'+self.user.username+'.jpg'
            picture_url=settings.MEDIA_URL+'profile_picture/'+self.user.username+'.jpg'
            if os.path.isfile(file_name):
                return picture_url
            else:
                gravata_url='http://www.gravata.com/avarta/{0}?{1}'.format(
                    hashlib.md5(self.user.email.lower()).hexdigest(),urllib.parse.urlencode({'d': no_picture, 's': '256'})
                )
                return gravata_url
        except Exception:
            return no_picture

    def get_url(self):
        url=self.url
        if 'http://' not in url and 'https://' not in self.url and len(self.url)>0:
            url="http://"+str(self.url)
        return url


def create_user_profile(sender,instance,created,**kwargs):
    if created:
        Profile.objects.create(user=instance)
        print("created")

def save_user_profile(sender,instance,**kwargs):
    instance.profile.save()
    print("saved")

post_save.connect(create_user_profile,sender=User)
post_save.connect(save_user_profile,sender=User)