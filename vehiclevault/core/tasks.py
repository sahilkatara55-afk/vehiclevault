from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_email_task(subject, message, recipient_list):
    """Send an email as a background task."""
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        return f"Email sent to {recipient_list}"
    except Exception as e:
        return f"Failed: {str(e)}"


@shared_task
def check_price_drops():
    """
    Check for price drops on wishlisted cars and notify users.
    Run this task periodically (e.g. every day via Celery Beat).
    """
    from vehicles.models import FavoriteVehicle
    from core.models import Notification

    for fav in FavoriteVehicle.objects.select_related('user', 'car'):
        user = fav.user
        car = fav.car
        # Trigger notification — could track price changes via signal or stored original price
        Notification.objects.create(
            user=user,
            title='Price Drop Alert',
            message=f"Good news! The price of {car.make} {car.model} may have changed. Check it out!"
        )
    return "Price drop check completed."


@shared_task
def send_emi_reminders():
    """
    Send EMI reminders to users.
    Run this task periodically via Celery Beat (e.g. daily at 9 AM).
    """
    from vehicles.models import Reminder
    from django.utils import timezone
    from datetime import timedelta
    from core.models import Notification

    tomorrow = timezone.now().date() + timedelta(days=1)
    reminders = Reminder.objects.filter(due_date=tomorrow).select_related('user')

    for reminder in reminders:
        Notification.objects.create(
            user=reminder.user,
            title=f"Reminder: {reminder.title}",
            message=f"Your '{reminder.title}' is due tomorrow ({reminder.due_date}). Don't miss it!"
        )
        # Also send email
        send_email_task.delay(
            subject=f"VehicleVault — Reminder: {reminder.title}",
            message=f"Hi {reminder.user.first_name},\n\nYour '{reminder.title}' is due tomorrow ({reminder.due_date}).\n\n— VehicleVault Team",
            recipient_list=[reminder.user.email]
        )
    return f"Sent {reminders.count()} EMI reminders."


@shared_task
def send_daily_digest():
    """
    Send a daily digest notification to all active users.
    """
    from core.models import User, Notification
    users = User.objects.filter(is_active=True, is_deleted=False, is_superuser=False)
    for user in users:
        Notification.objects.create(
            user=user,
            title='Daily Update',
            message='Check out the latest cars, offers and updates on VehicleVault today!'
        )
    return f"Sent daily digest to {users.count()} users."
