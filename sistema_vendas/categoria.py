import requests

url = "https://api.mercadolibre.com/sites/MLB/categories"
response = requests.get(url)
categories = response.json()

for category in categories:
    print(f"ID: {category['id']}, Name: {category['name']}")