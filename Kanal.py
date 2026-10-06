import urllib.request
import json
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

M3U_URL = "https://iptv-org.github.io/iptv/countries/tr.m3u"

WANTED_CHANNELS = [
    "TRT 1", "TRT Haber", "TRT Çocuk", "TRT Belgesel", "TRT Spor",
    "Kanal D", "ATV", "TV8", "NOW", "Kanal 7", "Habertürk",
    "NTV", "CNN Türk", "A Spor", "Show TV", "Star TV", "Beyaz TV"
]

def fetch_and_parse():
    req = urllib.request.Request(M3U_URL, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        response = urllib.request.urlopen(req, context=ctx)
        lines = response.read().decode('utf-8').split('\n')
    except Exception:
        return []

    channel_dict = {ch: {"name": ch, "logo": "", "urls": []} for ch in WANTED_CHANNELS}

    # KANAL 7 VIP LİNKLERİ (Uygulama önce bunları dener)
    channel_dict["Kanal 7"]["urls"].append("https://kanal7.blutv.com/blutv_kanal7_live/live.m3u8")
    channel_dict["Kanal 7"]["urls"].append("https://kanal7dvr.blutv.com/blutv_kanal7_dvr2/live_720p2000000kbps/index.m3u8")
    channel_dict["Kanal 7"]["urls"].append("https://kanal7-live.daioncdn.net/kanal7/kanal7.m3u8")

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
                    if line.strip() not in channel_dict[wanted]["urls"]:
                        channel_dict[wanted]["urls"].append(line.strip())
                    
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

if __name__ == "__main__":
    main()
