import random
from datetime import timedelta
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from .models import PendingUser

from django.contrib.auth import get_user_model

User = get_user_model()

def generate_and_send_otp(user):
    otp = str(random.randint(100000, 999999))
    cache_key = f'otp_{user.id}'
    cache.set(cache_key, otp, timeout=300)

    if settings.SEND_OTP_EMAIL:
        send_mail(
            'Your OTP Code',
            f'Your verification code is: {otp}',
            'PertCareApp',
            [user.email],
            fail_silently=False,
        )
        #send_otp_email(user.email, otp)
    return otp

def handle_otp_verification(user_id, submitted_otp, request_status):
    cache_key = f'otp_{user_id}'
    cached_otp = cache.get(cache_key)

    if not cached_otp:
        return False, "OTP expired or doesn't exist", None

    if cached_otp != submitted_otp:
        return False, "Invalid OTP", None

    cache.delete(cache_key)
    print(request_status)
    if request_status == 'sign_up':
        pending_user = PendingUser.objects.get(id = user_id)
        user = User.objects.create(username=pending_user.username, email=pending_user.email,first_name = pending_user.first_name, last_name = pending_user.last_name,country = pending_user.country)
        user.set_password(pending_user.password)
        user.save()
        pending_user.delete()
    else:
        user = User.objects.get(id = user_id)

    return True, "OTP verified successfully", user

from rest_framework.response import Response

def send_otp_response(user, message="OTP sent to your email"):
    otp_sent = generate_and_send_otp(user)
    return Response({
        "message": message,
        "otp": otp_sent,
        "user_id": user.id
    })
