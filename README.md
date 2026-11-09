# LLM API Lab

Küçük, anahtarsız bir demo: yerel bir mock API ile REST, JSON, Pydantic
structured output ve SSE streaming kavramlarını denemek.

## Kurulum ve çalıştırma

Python 3.11+ gerekir.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
uvicorn app:app --reload
```

Servis `http://127.0.0.1:8000` adresinde çalışır. `http://127.0.0.1:8000/docs`
adresinden endpoint'leri tarayıcıda deneyebilirsin. Başka bir terminalde:

```bash
python client.py
```

## Öğrenme deneyi

1. `POST /chat` adresine `{"prompt": "Merhaba"}` JSON gövdesi gönder.
2. Yanıttaki `answer` ve `confidence` alanlarını incele. Bunlar Pydantic
   `ChatResponse` şemasına uymalı.
3. Boş veya 500 karakterden uzun prompt gönder; API `422` ile reddeder.
4. `POST /chat/stream` çağrısında SSE `data:` olaylarını izle. Yanıt JSON
   chunk'ları halinde gelir ve `[DONE]` olayıyla biter.
5. Kodu değiştirip testleri çalıştır: `pytest -q`.

## Dosyalar

- `app.py`: FastAPI mock servisi ve Pydantic veri modelleri.
- `client.py`: HTTPX ile REST isteği ve SSE stream okuyucusu.
- `tests/test_app.py`: başarılı yanıt, doğrulama ve streaming testleri.

Bu servis gerçek bir dil modeli çağırmaz; amaç API ve test akışını dış
servis, API anahtarı veya ücret olmadan öğrenmektir.

## Mini evaluation: cevap kalitesini ölç

API bazı sorulara sabit cevap verir; diğer girdilerde eski `Mock yanıt: ...`
davranışı korunur. Streaming de aynı cevapları kullanır. `confidence=0.99`
yalnızca örnek bir sabittir; ölçülmüş güven veya doğruluk değildir.

Servisi açık bırak. Mac'te mevcut `.venv-1` ortamını kullanıyorsan yeni bir
terminalde proje klasöründen:

```bash
source .venv-1/bin/activate
python -m pip install -e ".[dev]"
python -m evaluate
```

Yeni kurulumda sanal ortamının adı `.venv` ise aktivasyon yolunu buna göre
değiştir. Komut `datasets/questions.json` içindeki 10 soruyu gerçek HTTP
istekleriyle `/chat` endpoint'ine gönderir. Beklenen çıktının özeti:

```text
Toplam senaryo: 10
Başarılı: 8
Başarısız: 2
Doğruluk: %80
```

Son iki soru mock cevap listesinde özellikle yoktur. Bu yüzden başarısız
örneklerin beklenen ve gerçek cevapları da gösterilir. Ayrıntılar
`evaluation-report.json` dosyasına yazılır; bu üretilen rapor Git'e eklenmez.

Karşılaştırma **birebir metin eşleşmesidir**: harf büyüklüğü, boşluk veya
eş anlamlı cevap farklılığı da başarısız sayılır. Bu, demo dataset'indeki
başarı oranıdır; genel LLM kalitesi veya judge değerlendirmesi değildir.
API bağlantı/HTTP/şema hataları ise normal cevap uyuşmazlığı sayılmaz;
komut hatayla durur ve yeni başarı raporu üretmez.

Varsayılan kalite eşiği `%100` olduğu için ilk çalıştırma `FAIL` ve çıkış
kodu `1` üretir. Bu, kurulum hatası değildir. `%80` eşiğini denemek için:

```bash
python -m evaluate --min-accuracy 0.8
```

Tam eşikte sonuç `PASS` ve çıkış kodu `0` olur. Alternatif dataset, servis
ve rapor yolları `--dataset`, `--base-url`, `--report` ile belirtilebilir.

### Alıştırma

1. `app.py` içindeki `MOCK_ANSWERS` listesine Almanya sorusunun cevabını ekle.
2. Reload açık değilse servisi yeniden başlat.
3. Evaluation komutunu tekrar çalıştır; `%90` bekle.
4. Çıkarma sorusunu da ekle; `%100` ve `PASS` bekle.

Beklenen cevabı gerçek çıktıya uydurarak dataset'i değiştirmek yerine,
sistemin davranışını düzelt. Öncesi/sonrası raporlarını ayrı kaydetmek için
`--report before.json` ve `--report after.json` kullanabilirsin.

```bash
python -m pytest -v
```

Otomatik testler başlangıç demosundaki `%80` davranışını da sabitler.
Alıştırmada mock'u düzelttiğinde bu testin beklenen sonuçlarını da bilinçli
olarak güncellemelisin. Testler `TestClient` kullandığı için çalışan sunucu
gerektirmez; evaluation komutu ise çalışan API gerektirir.
