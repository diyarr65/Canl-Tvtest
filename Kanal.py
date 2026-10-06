import urllib.request
import json
import ssl
import re

# SSL Hatalarını Yoksay
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

M3U_URL = "https://iptv-org.github.io/iptv/countries/tr.m3u"

# Uygulamada her zaman kalacak sabit kanallar
WANTED_CHANNELS = [
    "TRT 1", "TRT Haber", "TRT Çocuk", "TRT Belgesel", "TRT Spor",
    "Kanal D", "ATV", "TV8", "NOW", "Kanal 7", "Habertürk",
    "NTV", "CNN Türk", "A Spor", "Show TV", "Star TV", "Beyaz TV"
]

def fetch_and_parse():
    print("M3U listesi indiriliyor...")
    req = urllib.request.Request(M3U_URL, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        response = urllib.request.urlopen(req, context=ctx)
        lines = response.read().decode('utf-8').split('\n')
    except Exception as e:
        print(f"Bağlantı hatası: {e}")
        return []

    # Kanalları silinmemek üzere sabit bir sözlükte (dictionary) oluştur
    channel_dict = {ch: {"name": ch, "logo": "", "urls": []} for ch in WANTED_CHANNELS}

    current_name = ""
    current_logo = ""

    for line in lines:
        if line.startswith('#EXTINF'):
            current_name = line.split(',')[-1].strip()
            logo_match = re.search(r'tvg-logo="(.*?)"', line)
            current_logo = logo_match.group(1) if logo_match else ""
            
        elif line.startswith('http') and current_name:
            for wanted in WANTED_CHANNELS:
                if wanted.lower() in current_name.lower():
                    # Linki alternatifler arasına ekle (Aynı link 2 kere eklenmez)
                    if line.strip() not in channel_dict[wanted]["urls"]:
                        channel_dict[wanted]["urls"].append(line.strip())
                    
                    # Eğer kanalın logosu boşsa ekle
                    if not channel_dict[wanted]["logo"] and current_logo:
                        channel_dict[wanted]["logo"] = current_logo
                    break
            current_name = ""
            current_logo = ""

    return list(channel_dict.values())

def main():
    channels = fetch_and_parse()
    with open("channels.json", "w", encoding="utf-8") as f:
        json.dump(channels, f, ensure_ascii=False, indent=4)
    print("Kanallar güncellendi! Hiçbir kanal silinmedi, alternatif linkler eklendi.")

if __name__ == "__main__":
    main()