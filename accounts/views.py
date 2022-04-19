from email import message
import email
from django.shortcuts import redirect, render
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string  
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage  

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name'],
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split('@')[0]

            user = Account.object.create_user(email=email, username=username, first_name=first_name, last_name=last_name, password=password)
            user.phone_number = password
            user.save()
            # to get the domain of the current site  
            current_site = get_current_site(request)  
            mail_subject = 'Activation link has been sent to your email id'  
            message = render_to_string('accounts/acc_active_email.html', {  
                'user': user,  
                'domain': current_site.domain,  
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),  
                'token':default_token_generator.make_token(user),  
            })  
            to_email = email
            send_email = EmailMessage(  
                mail_subject, message, to=[to_email]  
            )  
            send_email.send()  
            # messages.success(request, 'Registration successful')

            return redirect('/accounts/login/?command=verification&email='+email)
    else:
        form = RegistrationForm()

    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)

def activate(request, uidb64, token):

    try:  
        uid = force_text(urlsafe_base64_decode(uidb64))  
        user = Account.object.get(pk=uid)  
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):  
        user = None  
    if user is not None and default_token_generator.check_token(user, token):  
        user.is_active = True  
        user.save()
        messages.success(request, 'Thank you for your email confirmation. Now you can login your account.')
        return redirect('login')
    else:  
        messages.error(request, 'Invalid  activation link')
        return redirect('register')  


def login(request):
    if request.method == 'POST':
        email = request.POST['email']#dùng kiểu này tránh lỗi hơn
        password = request.POST['password']
        
        user = auth.authenticate(request, email=email, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'invalid login')
            return redirect('login')
    return render(request, 'accounts/login.html')

@login_required(redirect_field_name='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out')
    return redirect('login')

@login_required(redirect_field_name='login')
def dashboard(request):
    return render(request, 'accounts/dashboard.html')

def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        #__exact so sánh sensitive
        if Account.object.filter(email=email).exists():#dùng object thay vì objects vì trong model có lệnh object = MyAccountManage()
            user = Account.object.get(email__exact=email)

            current_site = get_current_site(request)  
            mail_subject = 'Reset Your Password'  
            message = render_to_string('accounts/reset_password_email.html', {  
                'user': user,  
                'domain': current_site.domain,  
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),  
                'token':default_token_generator.make_token(user),  
            })  
            to_email = email
            send_email = EmailMessage(  
                mail_subject, message, to=[to_email]  
            )  
            send_email.send()  
            # messages.success(request, 'Registration successful')

            return redirect('/accounts/forgotPassword/?command=resetpassword&email='+email) 
        else:
           messages.error(request, 'Account does not exist') 
           return redirect('forgotPassword')
    return render(request, 'accounts/forgotPassword.html')

def resetpassword_validate(request, uidb64, token):
    try:  
        uid = force_text(urlsafe_base64_decode(uidb64))  
        user = Account.object.get(pk=uid)  
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):  
        user = None  
    if user is not None and default_token_generator.check_token(user, token):  
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')
    else:  
        messages.error(request, 'THis link has been expired')
        return redirect('login')  
    

def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']       
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.object.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'You have change your password success')
            return redirect('login')
        else:
            messages.error('Password do not match')
            return redirect('resetPassword')
    else:
        return render(request,'accounts/resetPassword.html')