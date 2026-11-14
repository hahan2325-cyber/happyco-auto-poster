import requests
from bs4 import BeautifulSoup

url = "https://happyco.asia/blog/gia-cong-van-cong-nghiep/gia-cong-van-mdf-chong-am-phu-melamine-cnc-nesting-happyco.html"
r = requests.get(url, timeout=10)
print("Status code:", r.status_code)
if r.status_code == 200:
    soup = BeautifulSoup(r.text, "html.parser")
    print("Page Title:", soup.title.string if soup.title else "No title")
    imgs = soup.find_all("img")
    print("Total images on page:", len(imgs))
    for img in imgs:
        src = img.get("src", "")
        if "19180" in src:
            print("  CDN Img:", src)
else:
    # Check blog index
    r2 = requests.get("https://happyco.asia/blog/gia-cong-van-cong-nghiep.html")
    print("Category status:", r2.status_code)
    soup2 = BeautifulSoup(r2.text, "html.parser")
    print("Category Title:", soup2.title.string if soup2.title else "No title")
    links = [a.get("href") for a in soup2.find_all("a") if a.get("href") and "gia-cong-van-mdf" in a.get("href")]
    print("Found links:", links)
