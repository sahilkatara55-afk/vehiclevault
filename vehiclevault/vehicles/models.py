from django.db import models
from django.conf import settings


class Car(models.Model):
    ENGINE_CHOICES = [
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
        ('cng', 'CNG'),
    ]

    TRANSMISSION_CHOICES = [
        ('manual', 'Manual'),
        ('automatic', 'Automatic'),
    ]

    SAFETY_CHOICES = [
        ('1', '1 Star'),
        ('2', '2 Stars'),
        ('3', '3 Stars'),
        ('4', '4 Stars'),
        ('5', '5 Stars'),
    ]

    image        = models.ImageField(upload_to='cars/', blank=True, null=True)
    make         = models.CharField(max_length=100)
    model        = models.CharField(max_length=100)
    year         = models.PositiveIntegerField(default=2024)
    price        = models.DecimalField(max_digits=12, decimal_places=2)
    mileage      = models.CharField(max_length=30, blank=True)
    engine       = models.CharField(max_length=20, choices=ENGINE_CHOICES, default='petrol')
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES, default='manual')
    description  = models.TextField(blank=True, null=True)
    safety_rating = models.CharField(max_length=1, choices=SAFETY_CHOICES, default='4')
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.make} {self.model} ({self.year})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Car'
        verbose_name_plural = 'Cars'


# ── Favorite Vehicles ──────────────────────────────────────────
class FavoriteVehicle(models.Model):
    user     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    car      = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='favorited_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'car')
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.email} liked {self.car}"


# ── Compare History ────────────────────────────────────────────
class CompareHistory(models.Model):
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='compare_history')
    cars        = models.ManyToManyField(Car, related_name='compared_in')
    compared_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-compared_at']

    def __str__(self):
        return f"{self.user.email} compared on {self.compared_at.strftime('%d-%m-%Y')}"


# ── Recently Viewed ────────────────────────────────────────────
class RecentlyViewed(models.Model):
    user      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recently_viewed')
    car       = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='viewed_by')
    viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'car')
        ordering = ['-viewed_at']

    def __str__(self):
        return f"{self.user.email} viewed {self.car}"


# ── User Document ──────────────────────────────────────────────
class UserDocument(models.Model):
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='documents')
    title       = models.CharField(max_length=200)
    file        = models.FileField(upload_to='user_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.user.email} — {self.title}"


# ── Reminder ──────────────────────────────────────────────────
class Reminder(models.Model):
    REMINDER_TYPES = [
        ('insurance', 'Insurance Renewal'),
        ('service',   'Service Reminder'),
        ('rc',        'RC Expiry'),
        ('puc',       'PUC Expiry'),
        ('other',     'Other'),
    ]

    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reminders')
    title      = models.CharField(max_length=200)
    type       = models.CharField(max_length=20, choices=REMINDER_TYPES, default='other')
    due_date   = models.DateField()
    notes      = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['due_date']

    def __str__(self):
        return f"{self.user.email} — {self.title} ({self.due_date})"


# ── Accessory ──────────────────────────────────────────────────
class Accessory(models.Model):
    name           = models.CharField(max_length=200)
    compatible_car = models.CharField(max_length=200, blank=True)
    price          = models.DecimalField(max_digits=10, decimal_places=2)
    image          = models.ImageField(upload_to='accessories/', blank=True, null=True)
    description    = models.TextField(blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


# ── Admin Notification ─────────────────────────────────────────
class AdminNotification(models.Model):
    title       = models.CharField(max_length=300)
    message     = models.TextField()
    sent_to_all = models.BooleanField(default=True)
    recipients  = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='notifications_received')
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
