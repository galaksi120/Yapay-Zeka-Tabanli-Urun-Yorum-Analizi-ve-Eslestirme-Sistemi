# Yapay-Zeka-Tabanli-Urun-Yorum-Analizi-ve-Eslestirme-Sistemi
🛍️ Yapay Zekâ Destekli Çoklu Platform Ürün Analiz ve Yorum Değerlendirme Sistemi

Bu proje; Trendyol, N11 ve Hepsiburada e-ticaret sitelerinde bir ürünün bulunmasını, yorumlarının toplanmasını ve yapay zekâ ile analiz edilmesini sağlayan bir sistemdir.

Sistem şu adımları gerçekleştirir:

Ürün Arama:

Girilen ürün adı, Trendyol, N11 ve Hepsiburada’da aranır.

Yapay zekâ (LLM) kullanılarak ürünün önemli özellikleri çıkarılır (ör. marka, model, kapasite, renk vb.).

Bu bilgiler eşleştirilerek aynı ürün farklı sitelerde bulunur.

Yorum Toplama:

Her siteden ilgili ürünün müşteri yorumları toplanır.

Sahte Yorum Analizi:

Yorumlar LLM ile analiz edilerek gerçek mi sahte mi olduğu belirlenir.

Güvenilirlik oranı %50’nin üzerinde olan yorumlar gerçek kabul edilir.

Yorum Özeti ve Puanlama:

Gerçek yorumlar üzerinden ürünün olumlu ve olumsuz yönleri özetlenir.

Her yorum hem olumlu/olumsuz hem de güvenilir/güvenilmez olarak etiketlenir.

Buna göre ürün için adil bir memnuniyet skoru üretilir.

⚙️ Kullanılan Teknolojiler

Kelime Eşleme:

Gemini API

RapidFuzz

Web Scraping:

Cloudscraper

Selenium

httpx

Requests

Yapay Zekâ Analizi:

LLM (Gemini) tabanlı modeller ile sahte yorum tespiti

Yorumların özetlenmesi ve sınıflandırılması
