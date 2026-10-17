import urllib.request
import json
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Artık iki farklı havuzumuz var, bot her ikisini de tarayacak!
M3U_SOURCES = [
    "https://iptv-org.github.io/iptv/countries/tr.m3u",
    "http://tinyurl.com/TV2M3"  # Görseldeki yeni kaynak eklendi
]

WANTED_CHANNELS = [
    "TRT 1", "TRT Haber", "TRT Çocuk", "TRT Belgesel", "TRT Spor",
    "Kanal D", "ATV", "TV8", "NOW", "Kanal 7", "Habertürk",
    "NTV", "CNN Türk", "A Spor", "Show TV", "Star TV", "Beyaz TV"
]

def fetch_and_parse():
    channel_dict = {ch: {"name": ch, "logo": "", "urls": []} for ch in WANTED_CHANNELS}

    # KANAL 7 VIP LİNKLERİ (Öncelikli olarak en başta)
    channel_dict["Kanal 7"]["urls"].append("https://kanal7.blutv.com/blutv_kanal7_live/live.m3u8")
    channel_dict["Kanal 7"]["urls"].append("https://kanal7dvr.blutv.com/blutv_kanal7_dvr2/live_720p2000000kbps/index.m3u8")
    channel_dict["Kanal 7"]["urls"].append("https://kanal7-live.daioncdn.net/kanal7/kanal7.m3u8")

    # Bot her iki kaynağı sırayla gezecek
    for source_url in M3U_SOURCES:
        print(f"Taraniyor: {source_url}")
        try:
            req = urllib.request.Request(source_url, headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(req, context=ctx)
            lines = response.read().decode('utf-8').split('\n')
            
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
                            # Link daha önce listeye eklenmemişse ekle (kopya link olmasın)
                            if line.strip() not in channel_dict[wanted]["urls"]:
                                channel_dict[wanted]["urls"].append(line.strip())
                            
                            # Eğer kanalın logosu hala boşsa, bulduğu logoyu ekle
                            if not channel_dict[wanted]["logo"] and current_logo:
                                channel_dict[wanted]["logo"] = current_logo
                            break
                    current_name = ""
                    current_logo = ""
        except Exception as e:
            print(f"Hata olustu ({source_url}): {e}")

    return list(channel_dict.values())

def main():
    channels = fetch_and_parse()
    with open("channels.json", "w", encoding="utf-8") as f:
        json.dump(channels, f, ensure_ascii=False, indent=4)
    print("İşlem tamam! Çift havuzdan kanallar toplandı.")

if __name__ == "__main__":
    main()
