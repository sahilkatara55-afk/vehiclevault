import os
import django
import sys
import urllib.request
import time
from django.core.files.base import ContentFile

sys.path.append(os.path.abspath('d:/project/VehicleVault/vehiclevault'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vehiclevault.settings')
django.setup()

from vehicles.models import Car
from seed_50_cars import CARS, fetch_wikipedia_image

car_map = {m: (mk, wiki) for mk, m, _, _, _, _, wiki, _, _, _ in CARS}

cars = Car.objects.filter(image='')
print(f"Attempting to fetch images for {cars.count()} cars...")

for car in cars:
    if car.model in car_map:
        wiki = car_map[car.model][1]
        print(f"Fetching {car.make} {car.model} via {wiki}")
        img_url = fetch_wikipedia_image(wiki)
        if img_url:
            try:
                req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                img_data = urllib.request.urlopen(req).read()
                file_name = f"{car.make.lower()}_{car.model.lower().replace(' ', '_')}.jpg"
                car.image.save(file_name, ContentFile(img_data), save=True)
                print("  -> Success!")
            except Exception as e:
                print(f"  -> Error saving: {e}")
        else:
            print("  -> No image found")
        time.sleep(2.5)  # Avoid 429
