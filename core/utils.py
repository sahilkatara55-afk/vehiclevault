from django.core.mail import send_mail
from django.conf import settings
from .models import Notification, NotificationPreference

TRANSLATIONS = {
    'gu': {
        'Account created successfully': 'તમારું એકાઉન્ટ સફળતાપૂર્વક બનાવવામાં આવ્યું છે',
        'Welcome to VehicleVault! Your account is ready.': 'VehicleVault માં આપનું સ્વાગત છે! તમારું એકાઉન્ટ તૈયાર છે.',
        'New login detected': 'નવું લોગિન શોધાયું',
        'A login was detected on your account. If this was not you, please change your password immediately.': 'તમારા એકાઉન્ટ પર એક લોગિન જોવા મળ્યું હતું. જો આ તમે ન હોવ, તો કૃપા કરીને તમારો પાસવર્ડ તરત જ બદલો.',
        'Password reset request received': 'પાસવર્ડ રીસેટ કરવાની વિનંતી મળી છે',
        'We received a request to reset your password. If this was not you, please contact support.': 'અમને તમારા પાસવર્ડને રીસેટ કરવાની વિનંતી મળી છે. જો આ તમે ન હોવ, તો કૃપા કરીને સપોર્ટનો સંપર્ક કરો.',
        'Password updated successfully': 'પાસવર્ડ સફળતાપૂર્વક અપડેટ થયો',
        'Your password has been reset successfully. You can now log in with your new password.': 'તમારો પાસવર્ડ સફળતાપૂર્વક રીસેટ કરવામાં આવ્યો છે. હવે તમે તમારા નવા પાસવર્ડ સાથે લોગિન કરી શકો છો.',
        'Enquiry Submitted': 'પૂછપરછ સબમિટ કરી',
        'Your enquiry has been submitted': 'તમારી પૂછપરછ સબમિટ કરવામાં આવી છે',
        'New User Registered': 'નવો વપરાશકર્તા નોંધાયેલ',
        'New Car Enquiry': 'નવી કાર પૂછપરછ',
    }
}

def send_action_notification(user, title, message, send_email=False):
    """
    Creates a Notification object and optionally sends an email if the user prefers it.
    Supports English (default) and Gujarati.
    """
    if not user.is_active or user.is_deleted:
        return
    
    # Check preferences
    try:
        prefs = user.notification_preference
    except NotificationPreference.DoesNotExist:
        prefs = NotificationPreference.objects.create(user=user)

    # Translate if language is Gujarati
    display_title = title
    display_message = message
    if prefs.language == 'gu':
        display_title = TRANSLATIONS['gu'].get(title, title)
        display_message = TRANSLATIONS['gu'].get(message, message)

    if prefs.in_app_notifications:
        Notification.objects.create(
            user=user,
            title=display_title,
            message=display_message
        )
    
    if send_email and prefs.email_notifications:
        try:
            send_mail(
                subject=f"VehicleVault — {display_title}",
                message=display_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Failed to send email: {e}")

def get_client_ip(request):
    """Extracts the client's IP address from the request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

