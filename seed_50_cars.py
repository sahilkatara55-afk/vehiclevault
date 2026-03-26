import os
import django
import sys
import urllib.request
import json
import random
from django.core.files.base import ContentFile

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vehiclevault.settings")
django.setup()

from vehicles.models import Car, Brand

CARS = [
    ("Tata", "Harrier", "suv", "diesel", 1549000, 2644000, "Tata_Harrier", 1956, "167 bhp", "350 Nm"),
    ("Tata", "Safari", "suv", "diesel", 1619000, 2734000, "Tata_Safari", 1956, "167 bhp", "350 Nm"),
    ("Tata", "Altroz", "hatchback", "petrol", 665000, 1079000, "Tata_Altroz", 1199, "86 bhp", "113 Nm"),
    ("Tata", "Tigor", "sedan", "petrol", 630000, 895000, "Tata_Tigor", 1199, "84 bhp", "113 Nm"),
    ("Mahindra", "XUV700", "suv", "diesel", 1399000, 2699000, "Mahindra_XUV700", 2184, "182 bhp", "450 Nm"),
    ("Mahindra", "Scorpio-N", "suv", "diesel", 1360000, 2454000, "Mahindra_Scorpio-N", 2184, "172 bhp", "400 Nm"),
    ("Mahindra", "Bolero", "suv", "diesel", 979000, 1089000, "Mahindra_Bolero", 1493, "74 bhp", "210 Nm"),
    ("Mahindra", "XUV300", "suv", "petrol", 799000, 1475000, "Mahindra_XUV300", 1197, "108 bhp", "200 Nm"),
    ("Maruti Suzuki", "Fronx", "suv", "petrol", 751000, 1304000, "Maruti_Suzuki_Fronx", 1197, "88 bhp", "113 Nm"),
    ("Maruti Suzuki", "Grand Vitara", "suv", "hybrid", 1080000, 1999000, "Suzuki_Grand_Vitara", 1490, "91 bhp", "122 Nm"),
    ("Maruti Suzuki", "Brezza", "suv", "petrol", 834000, 1414000, "Suzuki_Brezza", 1462, "101 bhp", "136 Nm"),
    ("Maruti Suzuki", "Dzire", "sedan", "petrol", 656000, 939000, "Suzuki_Dzire", 1197, "88 bhp", "113 Nm"),
    ("Maruti Suzuki", "Ertiga", "muv", "petrol", 869000, 1303000, "Suzuki_Ertiga", 1462, "101 bhp", "136 Nm"),
    ("Maruti Suzuki", "Celerio", "hatchback", "petrol", 536000, 710000, "Suzuki_Celerio", 998, "65 bhp", "89 Nm"),
    ("Maruti Suzuki", "Ignis", "hatchback", "petrol", 584000, 810000, "Suzuki_Ignis", 1197, "81 bhp", "113 Nm"),
    ("Maruti Suzuki", "XL6", "muv", "petrol", 1161000, 1461000, "Suzuki_XL6", 1462, "101 bhp", "136 Nm"),
    ("Hyundai", "Venue", "suv", "petrol", 794000, 1348000, "Hyundai_Venue", 1197, "81 bhp", "113 Nm"),
    ("Hyundai", "Aura", "sedan", "petrol", 649000, 905000, "Hyundai_Aura", 1197, "81 bhp", "113 Nm"),
    ("Hyundai", "Alcazar", "suv", "diesel", 1677000, 2128000, "Hyundai_Alcazar", 1493, "113 bhp", "250 Nm"),
    ("Hyundai", "Ioniq 5", "suv", "electric", 4595000, 4595000, "Hyundai_Ioniq_5", 0, "214 bhp", "350 Nm"),
    ("Hyundai", "Exter", "suv", "petrol", 613000, 1028000, "Hyundai_Exter", 1197, "81 bhp", "113 Nm"),
    ("Hyundai", "Grand i10 Nios", "hatchback", "petrol", 592000, 856000, "Hyundai_Grand_i10", 1197, "81 bhp", "113 Nm"),
    ("Hyundai", "Tucson", "suv", "diesel", 2901000, 3594000, "Hyundai_Tucson", 1998, "183 bhp", "416 Nm"),
    ("Kia", "Sonet", "suv", "petrol", 799000, 1569000, "Kia_Sonet", 1197, "81 bhp", "115 Nm"),
    ("Kia", "Carens", "muv", "diesel", 1045000, 1945000, "Kia_Carens", 1493, "114 bhp", "250 Nm"),
    ("Kia", "EV6", "suv", "electric", 6095000, 6595000, "Kia_EV6", 0, "320 bhp", "605 Nm"),
    ("Toyota", "Fortuner", "suv", "diesel", 3343000, 5144000, "Toyota_Fortuner", 2755, "201 bhp", "500 Nm"),
    ("Toyota", "Hyryder", "suv", "hybrid", 1114000, 2019000, "Toyota_Urban_Cruiser_Hyryder", 1490, "91 bhp", "122 Nm"),
    ("Toyota", "Glanza", "hatchback", "petrol", 686000, 1000000, "Toyota_Glanza", 1197, "88 bhp", "113 Nm"),
    ("Toyota", "Camry", "sedan", "hybrid", 4617000, 4617000, "Toyota_Camry", 2487, "175 bhp", "221 Nm"),
    ("Toyota", "Hilux", "suv", "diesel", 3040000, 3790000, "Toyota_Hilux", 2755, "201 bhp", "500 Nm"),
    ("Honda", "Amaze", "sedan", "petrol", 716000, 992000, "Honda_Amaze", 1199, "88 bhp", "110 Nm"),
    ("Honda", "Elevate", "suv", "petrol", 1158000, 1620000, "Honda_Elevate", 1498, "119 bhp", "145 Nm"),
    ("Volkswagen", "Taigun", "suv", "petrol", 1170000, 1999000, "Volkswagen_Taigun", 999, "114 bhp", "178 Nm"),
    ("Volkswagen", "Tiguan", "suv", "petrol", 3517000, 3517000, "Volkswagen_Tiguan", 1984, "187 bhp", "320 Nm"),
    ("Skoda", "Slavia", "sedan", "petrol", 1089000, 1912000, "Škoda_Slavia", 999, "114 bhp", "178 Nm"),
    ("Skoda", "Kushaq", "suv", "petrol", 1089000, 1999000, "Škoda_Kushaq", 999, "114 bhp", "178 Nm"),
    ("Skoda", "Kodiaq", "suv", "petrol", 3850000, 3999000, "Škoda_Kodiaq", 1984, "187 bhp", "320 Nm"),
    ("Renault", "Kiger", "suv", "petrol", 600000, 1123000, "Renault_Kiger", 999, "71 bhp", "96 Nm"),
    ("Renault", "Triber", "muv", "petrol", 600000, 897000, "Renault_Triber", 999, "71 bhp", "96 Nm"),
    ("Renault", "Kwid", "hatchback", "petrol", 470000, 645000, "Renault_Kwid", 999, "67 bhp", "91 Nm"),
    ("Nissan", "Magnite", "suv", "petrol", 600000, 1102000, "Nissan_Magnite", 999, "71 bhp", "96 Nm"),
    ("MG", "Astor", "suv", "petrol", 998000, 1790000, "MG_Astor", 1498, "108 bhp", "144 Nm"),
    ("MG", "ZS EV", "suv", "electric", 1898000, 2520000, "MG_ZS_EV", 0, "174 bhp", "280 Nm"),
    ("MG", "Gloster", "suv", "diesel", 3880000, 4387000, "MG_Gloster", 1996, "212 bhp", "478 Nm"),
    ("MG", "Comet EV", "hatchback", "electric", 699000, 914000, "Wuling_Air_EV", 0, "41 bhp", "110 Nm"),
    ("Jeep", "Compass", "suv", "diesel", 2049000, 3207000, "Jeep_Compass", 1956, "167 bhp", "350 Nm"),
    ("Jeep", "Meridian", "suv", "diesel", 3340000, 3861000, "Jeep_Commander_(2021)", 1956, "167 bhp", "350 Nm"),
    ("Jeep", "Wrangler", "suv", "petrol", 6265000, 6665000, "Jeep_Wrangler", 1995, "268 bhp", "400 Nm"),
    ("Toyota", "Vellfire", "muv", "hybrid", 11990000, 12990000, "Toyota_Alphard", 2487, "190 bhp", "240 Nm"),
]

def fetch_wikipedia_image(title):
    try:
        url = f"https://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&pithumbsize=800&titles={title}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        data = json.loads(response.read())
        pages = data.get('query', {}).get('pages', {})
        for page_id, page_info in pages.items():
            if 'thumbnail' in page_info:
                return page_info['thumbnail']['source']
    except Exception as e:
        print(f"Error fetching image for {title}: {e}")
    return None

def run():
    added = 0
    for make, model, body, engine, p_min, p_max, wiki1, disp, pow, tor in CARS:
        # Check if already exists
        if Car.objects.filter(make__iexact=make, model__iexact=model).exists():
            print(f"Skipping {make} {model}, already exists.")
            continue
            
        print(f"Adding {make} {model}...")
        
        # Make sure Brand exists
        Brand.objects.get_or_create(name=make)

        img_url = fetch_wikipedia_image(wiki1)
        
        car = Car(
            make=make,
            model=model,
            year=2024,
            min_price=p_min,
            max_price=p_max,
            mileage=f"{random.randint(12, 25)} kmpl",
            engine=engine,
            transmission="automatic" if p_max > 1500000 else "manual",
            safety_rating=str(random.randint(3, 5)),
            body_type=body,
            engine_displacement=disp,
            max_power=pow,
            max_torque=tor,
            seating_capacity=7 if body in ['muv'] or model in ['Safari', 'XUV700', 'Scorpio-N', 'Alcazar', 'Fortuner'] else 5,
            fuel_tank_capacity=45 if engine != 'electric' else 0,
            boot_space=random.randint(250, 500),
            has_sunroof=p_max > 1200000,
            has_airbags=True,
            has_abs=True,
        )
        
        if img_url:
            try:
                print(f"  Downloading image from {img_url}")
                req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
                img_response = urllib.request.urlopen(req)
                img_data = img_response.read()
                file_name = f"{make.lower()}_{model.lower().replace(' ', '_')}.jpg"
                car.image.save(file_name, ContentFile(img_data), save=False)
            except Exception as e:
                print(f"  Failed to save image: {e}")
        else:
            print("  No image found on Wikipedia.")
            
        car.save()
        added += 1

    print(f"Successfully added {added} new cars.")

if __name__ == '__main__':
    run()
