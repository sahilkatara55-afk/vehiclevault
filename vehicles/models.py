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
    
    BODY_CHOICES = [
        ('suv', 'SUV'),
        ('sedan', 'Sedan'),
        ('hatchback', 'Hatchback'),
        ('muv', 'MUV'),
        ('coupe', 'Coupe'),
        ('convertible', 'Convertible'),
        ('wagon', 'Wagon'),
        ('van', 'Van'),
        ('jeep', 'Jeep'),
    ]

    # Basic Info
    image        = models.ImageField(upload_to='cars/', blank=True, null=True)
    make         = models.CharField(max_length=100)
    model        = models.CharField(max_length=100)
    year         = models.PositiveIntegerField(default=2024)
    min_price    = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Minimum price in INR")
    max_price    = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Maximum price in INR")
    mileage      = models.CharField(max_length=30, blank=True)
    engine       = models.CharField(max_length=20, choices=ENGINE_CHOICES, default='petrol')
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES, default='manual')
    description  = models.TextField(blank=True, null=True)
    safety_rating = models.CharField(max_length=1, choices=SAFETY_CHOICES, default='4')
    
    # Technical Specifications
    engine_displacement = models.PositiveIntegerField(null=True, blank=True, help_text="Engine displacement in cc")
    max_power           = models.CharField(max_length=100, null=True, blank=True, help_text="e.g., 113.18 bhp @ 4000 rpm")
    max_torque          = models.CharField(max_length=100, null=True, blank=True, help_text="e.g., 250 Nm @ 1500-2750 rpm")
    fuel_tank_capacity  = models.PositiveIntegerField(null=True, blank=True, help_text="Fuel tank capacity in Liters")
    seating_capacity    = models.PositiveIntegerField(null=True, blank=True, help_text="Number of seats")
    boot_space          = models.PositiveIntegerField(null=True, blank=True, help_text="Boot space in Liters")
    body_type           = models.CharField(max_length=20, choices=BODY_CHOICES, null=True, blank=True)
    
    # Features (Booleans)
    has_sunroof         = models.BooleanField(default=False)
    has_airbags         = models.BooleanField(default=True)
    has_abs             = models.BooleanField(default=True)

    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    @property
    def formatted_min_price(self):
        val = float(self.min_price)
        if val >= 10000000:
            cr = val / 10000000
            return f"{cr:.2f} Crore".replace(".00", "")
        elif val >= 100000:
            lakh = val / 100000
            return f"{lakh:.2f} Lakh".replace(".00", "")
        return f"{val:,.0f}"

    @property
    def formatted_max_price(self):
        val = float(self.max_price)
        if val >= 10000000:
            cr = val / 10000000
            return f"{cr:.2f} Crore".replace(".00", "")
        elif val >= 100000:
            lakh = val / 100000
            return f"{lakh:.2f} Lakh".replace(".00", "")
        return f"{val:,.0f}"

    @property
    def formatted_price_range(self):
        min_p = self.formatted_min_price
        max_p = self.formatted_max_price
        if self.min_price == self.max_price or not self.max_price:
            return f"₹{min_p}"
        
        # Avoid redundancy like ₹11.55 Lakh - ₹15 Lakh -> ₹11.55 - 15 Lakh
        # For simplicity, returning both full strings is safest
        return f"₹{min_p} - ₹{max_p}"

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


# ── Brand ──────────────────────────────────────────────────────
class Brand(models.Model):
    name       = models.CharField(max_length=100, unique=True)
    logo       = models.ImageField(upload_to='brand_logos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

# ── Car Review ─────────────────────────────────────────────────
class CarReview(models.Model):
    car        = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='reviews')
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_left')
    rating     = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment    = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.car.make} {self.car.model} ({self.rating}/5)"
