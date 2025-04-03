import requests

CLIENT_ID = "3644311625640045"
CLIENT_SECRET = "XHklsGB1MIAAayT4TfxsxZuyn5E7qRJX"

url = "https://api.mercadolibre.com/oauth/token"
payload = {
    "grant_type": "client_credentials",
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
}

response = requests.post(url, data=payload)
access_token = response.json().get("access_token")

print("Access Token:", access_token)


##python get_token.py


  ##APP_USR-3644311625640045-030619-804d761ca58f35a6f83eb56377865cd6-162093607