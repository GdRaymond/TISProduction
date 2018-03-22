from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from TISProduction.settings import ALLOWED_SIGNUP_DOMAIN

def ForbbidenUsernameValidator(value):
    fobbiden_usernames=['admin', 'settings', 'news', 'about', 'help',
                           'signin', 'signup', 'signout', 'terms', 'privacy',
                           'cookie', 'new', 'login', 'logout', 'administrator',
                           'join', 'account', 'username', 'root', 'blog',
                           'user', 'users', 'billing', 'subscribe', 'reviews',
                           'review', 'blog', 'blogs', 'edit', 'mail', 'email',
                           'home', 'job', 'jobs', 'contribute', 'newsletter',
                           'shop', 'profile', 'register', 'auth',
                           'authentication', 'campaign', 'config', 'delete',
                           'remove', 'forum', 'forums', 'download',
                           'downloads', 'contact', 'blogs', 'feed', 'feeds',
                           'faq', 'intranet', 'log', 'registration', 'search',
                           'explore', 'rss', 'support', 'status', 'static',
                           'media', 'setting', 'css', 'js', 'follow',
                           'activity', 'questions', 'articles', 'network', ]
    if value.lower() in fobbiden_usernames:
        raise ValidationError('This is reserve key word , do not use for username')

def InvalidUsernameValidator(value):
    if '+' in value or '-' in value or '@' in value:
        raise ValidationError('This is an invalid username')

def UniqueUsernameValidator(value):
    if User.objects.filter(username__iexact=value).exists():
        raise ValidationError('User with this username already exist')

def UniqueEmailValidator(value):
    if User.objects.filter(email__iexact=value).exists():
        raise ValidationError('User with this email already exist')

def SignupDomainValidator(value):
    if '*' not in ALLOWED_SIGNUP_DOMAIN:
        error_message='The sign up domain allowed is {0}'.format('.'.join(ALLOWED_SIGNUP_DOMAIN))
        try:
            if value[value.index('@')+1:] not in ALLOWED_SIGNUP_DOMAIN:
                raise ValidationError(error_message)
        except Exception as err:
            raise ValidationError(error_message)


class SignupForm(forms.Form):
    username=forms.CharField(
        widget=forms.TextInput(attrs={"class":"form-control"}),
        max_length=50,
        required=True,
        help_text="Usernames main contain <strong>alphanumic</strong> , <strong>_</strong> and <strong>.</strong> characters",
    )
    password=forms.CharField(
        widget=forms.PasswordInput(attrs={"class":"form-control"}),
    )
    confirm_password=forms.CharField(
        widget=forms.PasswordInput(attrs={"class":"form-control"}),
    )
    email=forms.CharField(
        widget=forms.EmailInput(attrs={"class":"form-control"}),
        max_length=35,
        required=True
    )
    class Meta:
        model="User"
        exclude=['last_login','date_joined']
        fields=['username','password','confirm_password','email']

    def __init__(self,*args,**kwargs):
        super(SignupForm,self).__init__(*args,**kwargs)
        self.fields['username'].validators.append(ForbbidenUsernameValidator)
        self.fields['username'].validators.append(InvalidUsernameValidator)
        self.fields['username'].validators.append(UniqueUsernameValidator)
        self.fields['email'].validators.append(SignupDomainValidator)
        self.fields['email'].validators.append(UniqueEmailValidator)

    def clean(self):
        form_data=self.cleaned_data
        password=form_data.get('password')
        confirm_password=form_data.get('confirm_password')
        if password and password!=confirm_password:
            self._errors['password']=self.error_class(['password don\'t match'])
        return form_data