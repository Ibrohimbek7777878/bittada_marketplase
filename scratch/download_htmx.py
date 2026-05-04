import urllib.request
url = "https://unpkg.com/htmx.org@1.9.10/dist/htmx.min.js"
urllib.request.urlretrieve(url, "backend/static/js/htmx.min.js")
print("Downloaded HTMX")
