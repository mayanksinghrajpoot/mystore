from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm
from django.contrib import messages

import random
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from .models import UserProfile

def register_view(request):
    if request.method == 'POST':
        # Check for existing inactive user to bind to form
        email = request.POST.get('email')
        instance = None
        if email:
            try:
                existing_user = User.objects.filter(email=email).first()
                if existing_user and not existing_user.is_active:
                    instance = existing_user
            except Exception:
                pass

        form = UserRegisterForm(request.POST, instance=instance)
        
        if form.is_valid():
            email = form.cleaned_data.get('email')
            username = form.cleaned_data.get('username')
            
            # If it's a new user (no instance), check availability manually just in case
            # (though form.is_valid handles most unique checks, checking logic consistency)
            if not instance:
                if User.objects.filter(email=email).exists():
                     messages.error(request, "Email already registered.")
                     return render(request, 'user/register.html', {'form': form})
                # Also check username for new users
                if User.objects.filter(username=username).exists():
                     messages.error(request, "Username already taken.")
                     return render(request, 'user/register.html', {'form': form})

            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_active = False # Inactive until verified
            user.save()
            
            # Create/Get profile
            profile, created = UserProfile.objects.get_or_create(user=user)

            # Create OTP
            otp = str(random.randint(100000, 999999))
            profile.otp = otp
            profile.otp_created_at = timezone.now()
            profile.save()
            
            # Send Email
            subject = 'Verify your email'
            message = f'Thanks for registering on Style Store.\n Please use the below otp to verify yourself .\n Your OTP is {otp}.'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [email]
            
            try:
                send_mail(subject, message, from_email, recipient_list)
                request.session['verification_user_id'] = user.id
                messages.success(request, 'OTP sent to your email. Please verify.')
                return redirect('verify_otp')
            except Exception as e:
                # If email fails, we don't delete the user if it was a re-registration,
                # but maybe we should to keep state clean? 
                # Actually, better to just show error.
                messages.error(request, f'Error sending email: {e}')
                return render(request, 'user/register.html', {'form': form})
                
    else:
        form = UserRegisterForm()
    return render(request, 'user/register.html', {'form': form})

def verify_otp(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        user_id = request.session.get('verification_user_id')
        
        if not user_id:
            messages.error(request, 'Session expired. Please register again.')
            return redirect('register')
            
        try:
            user = User.objects.get(id=user_id)
            profile = user.profile
            
            # Check expiry
            if profile.otp_created_at < timezone.now() - timedelta(hours=1):
                messages.error(request, 'OTP expired. Please register again.')
                user.delete() # Cleanup
                return redirect('register')
                
            if profile.otp == otp:
                user.is_active = True
                user.save()
                
                # Clear OTP
                profile.otp = None
                profile.save()
                
                # Login
                login(request, user)
                del request.session['verification_user_id']
                messages.success(request, 'Email verified! Registration successful.')
                return redirect('home') # Redirect to home as dashboard URL is not defined
            else:
                messages.error(request, 'Invalid OTP.')
        except User.DoesNotExist:
             messages.error(request, 'User not found.')
             return redirect('register')
             
    return render(request, 'user/verify_otp.html')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                return redirect('home')
            else:
                messages.error(request,"Invalid username or password.")
        else:
            messages.error(request,"Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'user/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('home')

def profile_view(request):
    from .models import UserProfile
    from django.contrib.auth.decorators import login_required
    
    if not request.user.is_authenticated:
        return redirect('login')

    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        profile.phone = request.POST.get('phone', '')
        profile.address = request.POST.get('address', '')
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        profile.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('profile')
    return render(request, 'user/profile.html', {'profile': profile})

