import urllib.request
import os

url = "https://placehold.co/600x400?text=Bittada+Mebel"
dst = "/home/ibrohim/Desktop/client_baza/bittada_marketplase/backend/static/images/placeholder.png"

os.makedirs(os.path.dirname(dst), exist_ok=True)
try:
    urllib.request.urlretrieve(url, dst)
    print(f"Downloaded placeholder to {dst}")
except Exception as e:
    print(f"Error: {e}")
