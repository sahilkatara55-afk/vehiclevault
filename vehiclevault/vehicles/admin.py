from django.contrib import admin
from .models import Car, Brand, CarImage, CarReview, FavoriteVehicle, CompareHistory, RecentlyViewed

class CarImageInline(admin.TabularInline):
    model = CarImage
    extra = 3

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('make', 'model', 'year', 'engine', 'min_price')
    list_filter = ('make', 'engine', 'body_type', 'transmission')
    search_fields = ('make', 'model')
    inlines = [CarImageInline]

admin.site.register(Brand)
admin.site.register(CarReview)
admin.site.register(FavoriteVehicle)
admin.site.register(CompareHistory)
admin.site.register(RecentlyViewed)
