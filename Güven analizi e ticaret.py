# -*- coding: utf-8 -*-
gemini_key="APİ ANAHTARINI GİRİN" #Api anahtarını girin

import google.generativeai as genai
#Analiz etmek istediğimiz ürünü yazıyoruz
aratilan_urun="U.s. Polo Assn. Kadın Mavi Elbise Örme 50305753-vr036 Mavi" #Buraya aratmak istediğiniz Ürünün adını girin

genai.configure(api_key=gemini_key)

model=genai.GenerativeModel("gemini-2.5-pro")
chat=model.start_chat()
#Yapay zeka ile ürün özelliklerini analiz edip json formatına getiriyoruz
prompt=f"{aratilan_urun} bu ifadeyi sadece var olan ürün bilgilerini kullanarak (markayı kesinlikle unutma) ve ürün türünde gereksiz kelime kullanma renkler yabancı dilde yazıldıysa yabancı yaz renkleri çok uzatma olamayan özellikleri boş yazarak [Marka][Seri] [Kritik Özellik] [Kapasite][Renk] [Ürün Türü] yapısını bana sadece çıktı dictionary olacak şekilde yazdır."
response=chat.send_message(prompt)

# JSON string
import json
#Çıktıdaki gereksiz ifadeleri ve json yapısısnı bozan şeyleri temizliyoruz
json_str = response.text.replace("```json", "").replace("```", " ")

data = json.loads(json_str)
#Hakkında bilgi olmayan kısımları filtreliyoruz
data = {k: v for k, v in data.items() if v is not None}
print(data)
# JSON string'ini sözlüğe çevir
# Belirtilen sırayla alanları birleştirip ürün arama ve eşleştirme için uygun bir hale getiriyoruz.
arama_sonucu = f"{data['Marka']} {data['Seri']} {data['Kritik Özellik']} {data['Kapasite']} {data['Renk']} {data['Ürün Türü']}"
print(arama_sonucu)

import json
from rapidfuzz import fuzz

def match_json_with_text(json_str, arama_sonucu):
# 1. Parse JSON
    veri = json.loads(json_str)

    # 2. JSON'daki tüm kelimeleri çıkar
    json_kelimeler = []
    for v in veri.values():
        json_kelimeler += v.lower().split()

    # 3. Arama sonucu kelimeleri
    arama_kelimeler = arama_sonucu.lower().split()
    # 4. Her json kelimesi için en yüksek benzerliği bul
    en_yuksek_skorlar = []
    for json_kelime in json_kelimeler:
        skorlar = [fuzz.ratio(json_kelime, arama_kelime) for arama_kelime in arama_kelimeler]
        if skorlar:  # Ensure there are scores before finding the max
            en_yuksek = max(skorlar)
            en_yuksek_skorlar.append(en_yuksek)

    # 5. Ortalama benzerliği hesapla
    if not en_yuksek_skorlar: # Avoid division by zero if no matching words found
        return 0
    ortalama_benzerlik = sum(en_yuksek_skorlar) / len(en_yuksek_skorlar)
    if ortalama_benzerlik :
        return arama_sonucu,round(ortalama_benzerlik, 4)

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import urllib.parse
from rapidfuzz import fuzz
import time
def trendyol_urunleri_cek(urun_adi):
    #Ürün adını alıp encode ediyoruz ve arama linkine yerleştiriyoruz
    urun_adi_encoded = urllib.parse.quote_plus(urun_adi)
    url = f"https://www.trendyol.com/sr?q={urun_adi_encoded}"
    print(url)

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # Akıllı bekleme - ürün kapsayıcılar yüklenene kadar bekle
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.prdct-cntnr-wrppr"))
        )
        time.sleep(1)  # opsiyonel ek bekleme, yavaş internet varsa
    except:
      return None

    urunler = []

    # 1. prdct-cntnr-wrppr kapsayıcıları al
    kapsayicilar = driver.find_elements(By.CSS_SELECTOR, "div.prdct-cntnr-wrppr")

    for kapsayici in kapsayicilar:
        # 2. İçindeki p-card-wrppr ile devam et
        p_cards = kapsayici.find_elements(By.CSS_SELECTOR, "div.p-card-wrppr.with-campaign-view")
        for card in p_cards:
            title = card.get_attribute("title")
            data_id = card.get_attribute("data-id")
            try:
                link_etiket = card.find_element(By.CSS_SELECTOR, "a.p-card-chldrn-cntnr")

                link = link_etiket.get_attribute("href")
            except:
                link = None
            try:
                # Marka bilgisini çekiyoruz
                marka_span = card.find_element(By.CSS_SELECTOR, "span.prdct-desc-cntnr-ttl")
                marka = marka_span.get_attribute("title").strip()
            except NoSuchElementException:
                marka = None
            if title and link:
                urunler.append({"title": title.strip(), "link": link.strip(),"data_id": data_id.strip(),"marka": marka})

    driver.quit()
    return urunler

def get_product_id_trendyol(sonuc,json_str):
    arama_kelimesi = sonuc
    urunler = trendyol_urunleri_cek(arama_kelimesi[:51:])
    #Ürünleri getirme fonksiyonu
    print(f"Aranan ürün: '{arama_kelimesi}'\n")
    max_score=0
    max_urun=None
    max_urun_id=None
    max_urun_link=None
    data = json.loads(json_str)
    if urunler is None:
      print("Ürün bulunamadı")
    else:
      for urun in urunler:
          urun_title = urun['marka']+" "+urun['title']
          urun_title=urun_title.title()
          #Ürün adını fonksiyona verip en uygun eşleşmeyi bulamk istiyoruz
          product=match_json_with_text(json_str,urun_title)[0]
          score=match_json_with_text(json_str,urun_title)[1]
          if product:
            try:
              if data['Renk'] in urun_title:
                #renk konusunda yanlış ürün getirebilir diye renk koşulu konuldu
                if max_score<score:
                  max_score=score
                  max_urun=product
                  max_urun_link=urun['link']
                  max_urun_id=urun['data_id']
            except:
               if max_score<score:
                  max_score=score
                  max_urun=product
                  max_urun_link=urun['link']
                  max_urun_id=urun['data_id']

          else:
            print("Ürün bulunamadı")
    if max_score>80:
      #Maksimum skoru ve yukarıdaki koşulu sağlayan  ürünü döndürüyoruz
      return max_urun,max_urun_id,max_urun_link
    else:
      print("Ürün bulunamadı")
      return None,None,None

def n11_urunleri_cek(urun_adi):
    urun_adi_encoded = urllib.parse.quote_plus(urun_adi)
    #Ürün adını encode edip linke ekliyoruz
    url = f"https://www.n11.com/arama?q={urun_adi_encoded}"
    print(url)

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(3)  # Sayfanın yüklenmesi için bekle

    urunler = []
    # a.plink selector'ü ile ürün linkleri ve isimleri alınır
    links = driver.find_elements("css selector", "a.plink")

    for a_tag in links:
        href = a_tag.get_attribute("href")
        title = a_tag.get_attribute("title")
        data_id = a_tag.get_attribute("data-id")
        if href and title:
            urunler.append({"title": title, "link": href,"data_id":data_id})

    driver.quit()
    return urunler

def get_product_id_n11(sonuc,json_str):
    arama_kelimesi = sonuc
    urunler = n11_urunleri_cek(arama_kelimesi[:51:])
    print(f"Aranan ürün: '{arama_kelimesi}'\n")
    max_score=0
    max_urun=None
    max_urun_id=None
    max_urun_link=None
    data = json.loads(json_str)
    if urunler is None:
      print("Ürün bulunamadı")
    else:
      for urun in urunler:
          urun_title = urun['title'].title()
          match_result = match_json_with_text(json_str,urun_title)
          if match_result: # Eşleşme sonucu varlığı kontrolü
               product, score = match_result
               if product:
                  try:
                    if data['Renk'] in urun_title:
                      #Renk varlığı koşulu
                      if max_score<score:
                        max_score=score
                        max_urun=product
                        max_urun_link=urun['link']
                        max_urun_id=urun['data_id']
                  except:
                    if max_score<score:
                        max_score=score
                        max_urun=product
                        max_urun_link=urun['link']
                        max_urun_id=urun['data_id']
               else:
                  print("Ürün bulunamadı")

    if max_score > 65:
        #Eşleşen ürün bu koşulu sağlarsa döndür (Bu eşikler sitelerin ürün isimlendirme kıstaslarıyla oluşturuldu)
        return max_urun,max_urun_id,max_urun_link
    else:
        print("Ürün bulunamadı")
        return None,None,None

from bs4 import BeautifulSoup
import json
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

def get_hepsiburada_prolink_to_id(urun_link):
    url = urun_link
    #Ürünün stok kodunu almak için ürün linkini kullanıp parse işlemi yapıyoruz
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(4)  # Sayfa yüklenmesi için bekle

    page_value = None

    try:
        divs = driver.find_elements("xpath", "//div[@data-hbus]")
        for div in divs:
            data_hbus_str = div.get_attribute("data-hbus")
            if data_hbus_str:
                try:
                    data_hbus = json.loads(data_hbus_str)
                    # Sadece dict ise işlem yap
                    if isinstance(data_hbus, dict):
                        page_value = data_hbus.get("data", {}).get("page_value")
                        if page_value:
                            break
                    else:
                        # data_hbus bool veya başka tip ise atla
                        continue
                except json.JSONDecodeError:
                    continue
    except NoSuchElementException:
        print("data-hbus attribute'u olan div bulunamadı.")
    finally:
        driver.quit()

    return page_value



def hepsiburada_urunleri_cek(urun_adi):
    urun_adi_encoded = urllib.parse.quote(urun_adi)
    url = f"https://www.hepsiburada.com/ara?q={urun_adi_encoded}"
    print(url)

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(4)  # Yüklenme için bekleme (gerekirse artırılabilir)

    urunler = []
    try:
        # UL içindeki tüm LI ürünlerini al
        lis = driver.find_elements("css selector", 'ul[class^="productListContent-"] > li[class^="productListContent-"]')
    except NoSuchElementException:
        lis = []

    for li in lis:
        try:
            article = li.find_element("css selector", 'article[class^="productCard-module_article"]')
            a_tag = article.find_element("css selector", 'a[class^="productCardLink-module_productCardLink"]')
            title = a_tag.get_attribute("title")
            href = a_tag.get_attribute("href")
            if title and href:
                if href.startswith("/"):
                    href = "https://www.hepsiburada.com" + href
                urunler.append({"title": title.strip(), "link": href})
        except NoSuchElementException:
            continue

    driver.quit()
    return urunler

def get_product_id_hepsiburada(sonuc,json_str):
    arama_kelimesi = sonuc
    urunler = hepsiburada_urunleri_cek(arama_kelimesi)

    print(f"Aranan ürün: '{arama_kelimesi}'\n")
    max_score=0
    max_urun=None
    max_urun_link=None
    if urunler is None:
      print("Ürün bulunamadı")
    else:
      for urun in urunler:
          urun_title = urun['title'].title() # Store the original title for printing
          product=match_json_with_text(json_str,urun_title)[0]
          score=match_json_with_text(json_str,urun_title)[1]

          data = json.loads(json_str)


          if product:
            try:
              if data['Renk'] in urun_title:
                if max_score<score:
                  max_score=score
                  max_urun=product
                  max_urun_link=urun['link']
                  max_urun_id=urun['data_id']
            except:
               if max_score<score:
                  max_score=score
                  max_urun=product
                  max_urun_link=urun['link']
                  max_urun_id=urun['data_id']

          else:
            print("Ürün bulunamadı")

      if max_score > 65:
        return max_urun,get_hepsiburada_prolink_to_id(max_urun_link),max_urun_link
      else:
        print("Ürün bulunamadı")
        return None,None,None

import httpx
import pandas as pd
import time
import httpx
import pandas as pd
import time
def get_hepsiburada_comments(sku):
  #Sku kodu bize product_id fonksiyonlarından gelicek
  #Hepsiburada sitesindeki ilgili ürünlerin yorumlarını alıyoruz sku ile
  if sku is not None:
      #Sku değerinin varlığına göre yorumları df e ekliycez
      df = pd.DataFrame(columns=["date", "comment", "rate"])
      url = f"https://user-content-gw-hermes.hepsiburada.com/queryapi/v2/ApprovedUserContents?sku={sku}&includeSiblingVariantContents=true&from={{}}&size=100"
      #Api linkine sku kodunu yerleştiriyoruz
      headers = {
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/115.0.0.0 Safari/537.36",
          "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
                    "application/signed-exchange;v=b3;q=0.9",
          "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
          "Accept-Encoding": "gzip, deflate, br",
          "Connection": "keep-alive",
          "Referer": "https://www.google.com/",
          "Origin": "https://www.hepsiburada.com",
          "Sec-Fetch-Site": "same-origin",
          "Sec-Fetch-Mode": "navigate",
          "Sec-Fetch-User": "?1",
          "Sec-Fetch-Dest": "document",
          "Upgrade-Insecure-Requests": "1",
          # "Cookie": "cookie_adi=cookie_degeri; diger_cookie=deger",  # Eğer varsa ekle
      }

      response = httpx.get(url.format(0), headers=headers)

      if response.status_code == 200:
          data = response.json()

          # Toplam yorum sayısını al ve sayfa sayısını bul
          total_count = data.get("totalItemCount", 0)
          print(f"Toplam Yorum Sayısı: {total_count}")
          for i in range(0,total_count,100):

              response = httpx.get(url.format(i), headers=headers)
              if response.status_code == 200:
                  data = response.json()
                  # Yorum listesini al
                  yorumlar = data["data"]["approvedUserContent"]["approvedUserContentList"]

                  for yorum in yorumlar:
                      tarih = yorum.get("createdAt", "Yok").split("T")[0]  # Saat kısmı atıldı
                      puan = yorum.get("star", "Yok")
                      content = yorum.get("review", {}).get("content", "Yorum yok")

                      print(f"Tarih: {tarih}| Yorum :{content} | Puan :{puan}")
                      df.loc[len(df)] = [tarih, content, puan]
                      df=df.dropna(subset=['comment'])
                  time.sleep(0.5)
              else:
                  print(f"Failed to retrieve data. Status code: {response.status_code}")
                  break # Hata alırsak koddan çık
      else:
          print(f"Failed to retrieve initial data. Status code: {response.status_code}")
      return df

from itertools import product
import cloudscraper
import pandas as pd
import time
from datetime import datetime


def get_n11_comments(product_id):
    df = pd.DataFrame(columns=["date", "comment", "rate"])
    if product_id is not None:
        # Ürün ID'yi buraya yaz varsa dfe ekleme işlemini başlat

        url_template=f"https://m.n11.com/getProductReviews/{product_id}?currentPage={{}}&sortOrder=RECENT&tag=tümü"
        #Ürün kodunu apiye yerleştirip yorumları çek
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Referer': 'https://www.n11.com',
        }

        scraper = cloudscraper.create_scraper(browser={'custom': headers['User-Agent']})


        # İlk sayfadan toplam yorumu bul ve sayfa sayısını hesapla
        response = scraper.get(url_template.format(1), headers=headers)

        if response.status_code == 200:
            data = response.json()

            total_comment = int(data['pagination']['totalCount'])
            if total_comment%8==0:
                total_pages = total_comment // 8
            else:
                total_pages = total_comment // 8 + 1
            print(f"Toplam sayfa sayısı: {total_pages}")
        else:
            print("Veri alınamadı. Durum kodu:", response.status_code)
            total_pages = 0
        s=0
        for page in range(1, total_pages + 1):
            response = scraper.get(url_template.format(page), headers=headers)

            if response.status_code == 200:
                data = response.json()
                comments = data.get('productFeedBackReviewList', [])

                for comment in comments:
                    rate = comment.get('scoreAsStar')
                    text = comment.get("contents")
                    date_iso = comment.get('createdDate')

                    date_iso = datetime.strptime(date_iso, "%d/%m/%Y").date()
                    print(f"Tarih: {date_iso} | Yorum: {text} | Puan: {rate}")
                    df.loc[len(df)] = [date_iso, text, rate]



            else:
                print(f"Veri alınamadı. Durum kodu: {response.status_code} - Sayfa: {page}")
            time.sleep(1)  # 1 saniye bekle ki sunucu aşırı istekten hata vermesin
    else:
      pass
    return df

import requests
#Trendyol için yorumları çekme
import pandas as pd
def get_trendyol_comments(product_id):
    df = pd.DataFrame(columns=["date", "comment", "rate"])
    if product_id is not None:

        url = f"https://apigw.trendyol.com/discovery-mweb-socialgw-service/api/product-review/reviews/{product_id}?page={{}}&size=50&storefrontId=1&orderByDirection=DESC&orderByField=Score&channelId=1"

        response = requests.get(url.format(0))
        #Sayfa sayısını alıyoruz döngüde yardımcı olucak
        if response.status_code == 200:
            data = response.json()
            comments = data["reviews"]["content"]
            result = data.get("reviews", {})
            total_pages = result.get("totalPages")
            total_elements = result.get("totalElements")
            current_page = result.get("page")
            page_size = result.get("size")

        else:
            print("Veri alınamadı. Durum kodu:", response.status_code)
        for j in range(total_pages):

          response = requests.get(url.format(j))

          if response.status_code == 200:
              data = response.json()
              comments = data["reviews"]["content"]
              result = data.get("reviews", {})

              total_pages = result.get("totalPages")
              total_elements = result.get("totalElements")
              current_page = result.get("page")
              page_size = result.get("size")

              for i, comment in enumerate(comments, start=1):

                  rate = comment.get("rate")
                  text = comment.get("comment")
                  date_iso = comment.get("commentDateISOType")
                  print(f"Tarih: {date_iso}| Yorum: {text} | Puan: {rate} ")

                  df.loc[len(df)] = [date_iso, text, rate]
              time.sleep(1)
          else:
              print("Veri alınamadı. Durum kodu:", response.status_code)
    else:
      pass
    return df

#Product idleri alıyoruz
urun_trendyol,pro_id_trendyol,trendyol_link=get_product_id_trendyol(arama_sonucu,json_str)
urun_hepsiburada,pro_id_hepsiburada,hepsiburada_link=get_product_id_hepsiburada(arama_sonucu,json_str)
urun_n11,pro_id_n11,n11_link=get_product_id_n11(arama_sonucu,json_str)

#Yorumları alıyoruz product_id kullanıp ve dfe atıyoruz
df_hepsiburada=get_hepsiburada_comments(pro_id_hepsiburada)
print("-----------------------------")
df_trendyol=get_trendyol_comments(pro_id_trendyol)
print("-----------------------------")
df_n11=get_n11_comments(pro_id_n11)

import pandas as pd
#dfleri birleştirip sadece puan verilmiş yorumları kaldırıyoruz
df_all=pd.concat([df_hepsiburada,df_trendyol,df_n11]).dropna(subset=['comment'])

import google.generativeai as genai
model=genai.GenerativeModel("gemini-2.5-pro")
# Negatif kriter indexleri (0 tabanlı)
negative_indexes = [4]  # Çelişki

# Kriter ağırlıkları (toplam 100)
weights=[30, 20, 20, 15, 10, 5]

def calculate_realism_score(scores):
    total_weight = sum(weights)
    weighted_score = 0

    for i, score in enumerate(scores):
        if i in negative_indexes:
            # Negatif kriter: yüksekse kötü, ters çevir
            realism_component = 5 - score  # score 0-5 arasında olmalı
        else:
            # Pozitif kriter: yüksekse iyi
            realism_component = score
        weighted_score += realism_component * weights[i]

    # Çünkü score 0-5 aralığında, maksimum weighted_score = total_weight * 5
    realism_percentage = (weighted_score / (5*total_weight)) * 100
    return realism_percentage


def create_gemini_prompt_for_detailed_fake_probability_v2(comments):
    comments_str = "\n".join(f"- {c}" for c in comments)
    #Yorumları prompta ver ve aşağıdaki kıstaslara göre puanlanmış güvenilirlik analizi
    prompt = f""":Aşağıda müşteri yorumları yer almaktadır. Her yorum için aşağıdaki 6 özelliğin her birinin ne kadar bulunduğunu 0 ile 5 arasında, kademeli ve yumuşak şekilde puanla

    - 0 = Özellik hiç yok
    - 5 = Özellik çok belirgin

    - Lütfen aşırı uç puanlar çelişki hariç (0 veya 5) vermekten kaçın.
    - Çelişki veya mantıksal sorun için düşük puan çelişkisiz, yüksek puan çok çelişkili demektir.

    Özellikler:
    1) Kişisel Deneyim Belirtisi
    2) Yorum içeriğinin anlamlılığı
    3) Somut Detay Seviyesi
    4) Duygusal Doğallık Seviyesi
    5) Çelişki veya Mantıksal Sorun
    6) Dilsel Özgünlük

    Her yorum için 6 puanı sırayla ve sadece rakamlarla, virgül ile ayırarak yaz.

    Yorumlar:
    {comments_str}

    Örnek çıktı:
    1,4,0,5,1,4
    3,3,1,4,5,0
    ...

    Sadece sayılarla cevap ver. Açıklama ya da yorum ekleme.
    """

    return prompt

def analyze_detailed_fake_probabilities_gemini_v2(comments):
    chat = model.start_chat()
    prompt = create_gemini_prompt_for_detailed_fake_probability_v2(comments)
    response = chat.send_message(prompt)
    metin = response.text.strip()

    lines = metin.split('\n')
    results = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            puanlar = [int(x.strip()) for x in line.split(',')]
            if len(puanlar) == 6:
                results.append(puanlar)
        except:
            continue
    return results

# Örnek kullanım
comments = list(df_all['comment'])
realism_scores = []
# realism score listesi

import time
for j in range(0,len(df_all),30):
      comments = list(df_all['comment'])[j:j+30:]

      detailed_scores = analyze_detailed_fake_probabilities_gemini_v2(comments)



      for i, scores in enumerate(detailed_scores):
          realism = calculate_realism_score(scores)
          realism_scores.append(realism)

          print(
                      f"Yorum {i+1}: "
                      f"Kişisel Deneyim: {scores[0]}, Yorumun Anlamlılığı: {scores[1]}, Somut Detay: {scores[2]}, "
                      f"Duygusal Doğallık: {scores[3]}, Çelişki: {scores[4]}, Dilsel Özgünlük: {scores[5]} | "
                      f"Gerçeklik Skoru: %{realism:.2f}"
          )
          time.sleep(5)

#Realism skorlarını dfe ekle
df_all= df_all.iloc[:len(realism_scores)].copy()
df_all['realism_score'] = realism_scores
df_all = df_all.reset_index(drop=True)

n = len(df_all)
total_etki = 0
"""Doğruluk Destekli Memnuniyet Skoru (DDMS)
— Memnuniyet puanını yorumların doğruluk skoruyla destekler.
Olumlu yorumlar 3 yıldız ve üzeri
Yalan  yorumlar doğruluk oranı %50 nin altında olanlar
Yorum olumlu ise +1
Yorum olumsuz ise -1
Yorum doğru ise  +1
Yorum yalan ise -1
Bu değerler çarpılarak memnuniyet puanı hesaplanır.
Bu sistemde olumlu ve doğru yorumlar +1
olumlu ve yalan yorumlar -1
olumsuz ve doğru yorumlar -1
olumsuz ve yalan yorumlar +1  şeklinde değerlendirilir ve adil bir ürün puanlama yapılmaya çalışılır"""

for i in range(n):
    t = 1 if df_all.loc[i, "rate"] >= 3 else -1
    r = 1 if df_all.loc[i, "realism_score"] >= 50 else -1
    total_etki += t * r

memnuniyet = ((total_etki + n) / (2 * n)) * 5
print(f"5 üzerinden genel memnuniyet skoru: {memnuniyet:.2f}")

import google.generativeai as genai
import re
model = genai.GenerativeModel("gemini-2.5-pro")

def create_gemini_prompt_for_detailed_comment_analysis(comments):
    comments_str = "\n".join(f"- {c}" for c in comments)

    prompt = f""":Aşağıda müşteri yorumları yer almaktadır.

    Yorumlar:
    {comments_str}

    Bu yorumları analiz edip ilgili ürünün kısaca iyi özelliklerini ve kötü özelliklerini özetlemeni istiyorum
    """

    return prompt


# Örnek kullanım
comments = list(df_all['comment'])
chat = model.start_chat()
prompt = create_gemini_prompt_for_detailed_comment_analysis(comments)
response = chat.send_message(prompt)

if response.text:
    metin = response.text
    print(metin)
else:
    print("API response did not contain text.")
    print(f"Finish reason: {response.candidates[0].finish_reason}")
    print(f"Safety ratings: {response.candidates[0].safety_ratings}")

rapor = f"""

{arama_sonucu}
---------------------------------------------------------------------------------------------

Toplam Yorum Sayısı: {len(df_all)}
Doğruluk Destekli Memnuniyet Puanı:{memnuniyet:.2f}/5

Yapay zeka ile yapılan ürün eşleştirmesinin  linkleri:
Trendyol:{str(trendyol_link).replace("None","")}
Hepsiburada:{str(hepsiburada_link).replace("None","")}
N11:{str(n11_link).replace("None","")}

----------------------------------------------------------------------------------------------

{metin}

-----------------------------------------------------------------------------------------------

"""

with open(f"{data['Marka']} {data['Ürün Türü']} urun analizi.txt", "w", encoding="utf-8") as f:
    f.write(rapor)

with open(f"{data['Marka']} {data['Ürün Türü']} urun analizi.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()
    for line in lines:
        print(line.strip())


import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import os

# Varsayılan dosya uzantısı
DOSYA_KLASORU = "urun analizleri"  # Şu anki klasör
UZANTI = ".txt"

# Ana pencere
root = tk.Tk()
root.title("Ürün Analiz Görüntüleyici")
root.geometry("900x600")
root.configure(bg="white")

# Sol: Dosya listesi
frame_left = tk.Frame(root, bg="white", padx=10, pady=10)
frame_left.pack(side=tk.LEFT, fill=tk.Y)

label_list = tk.Label(frame_left, text="🗂 Analiz Dosyaları", font=("Helvetica", 14, "bold"), bg="white")
label_list.pack(pady=(0, 10))

listbox = tk.Listbox(frame_left, width=30, font=("Helvetica", 12))
listbox.pack(fill=tk.Y)

# Sağ: Başlık ve içerik
frame_right = tk.Frame(root, bg="white", padx=10, pady=10)
frame_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Başlık alanı (yeşil çerçeve)
frame_title = tk.Frame(frame_right, bg="white", highlightbackground="green", highlightthickness=3, padx=10, pady=10)
frame_title.pack(fill=tk.X, pady=(0, 10))

label_title = tk.Label(frame_title, text="Ürün Başlığı", font=("Helvetica", 18, "bold"), fg="#1b5e20", bg="white")
label_title.pack()

# İçerik alanı (mor çerçeve)
frame_text = tk.Frame(frame_right, bg="white", highlightbackground="#7b1fa2", highlightthickness=3)
frame_text.pack(fill=tk.BOTH, expand=True)

text_area = ScrolledText(frame_text, wrap=tk.WORD, font=("Helvetica", 12), bg="#f5f5f5")
text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
text_area.config(state=tk.DISABLED)

# Listeyi .txt dosyalarıyla doldur
def txt_dosyalari_yukle():
    txt_dosyalar = [f for f in os.listdir(DOSYA_KLASORU) if f.endswith(UZANTI)]
    for dosya in txt_dosyalar:
        listbox.insert(tk.END, dosya)

# Seçilen dosyayı göster
def goster(event):
    secili_index = listbox.curselection()
    if not secili_index:
        return
    dosya_adi = listbox.get(secili_index[0])
    dosya_yolu = os.path.join(DOSYA_KLASORU, dosya_adi)
    
    with open(dosya_yolu, "r", encoding="utf-8") as f:
        icerik = f.read()
    
    # Başlık alma (ilk satır)
    satirlar = icerik.strip().split("\n")
    baslik = satirlar[0] if satirlar else "Başlık Bulunamadı"
    
    label_title.config(text=baslik)
    text_area.config(state=tk.NORMAL)
    text_area.delete(1.0, tk.END)
    text_area.insert(tk.END, icerik)
    text_area.config(state=tk.DISABLED)

# Liste seçimi olayı
listbox.bind("<<ListboxSelect>>", goster)

# Başlatırken dosyaları yükle
txt_dosyalari_yukle()

# Başlat
root.mainloop()
