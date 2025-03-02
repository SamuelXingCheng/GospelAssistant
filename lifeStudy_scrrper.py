import requests
from bs4 import BeautifulSoup
import json
import os
import time

# 設定儲存 JSON 的資料夾
JSON_FOLDER = "lsm_lifestudy_json"
os.makedirs(JSON_FOLDER, exist_ok=True)

def get_lifestudy_content(url):
    """ 爬取指定的生命讀經章節 """
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 找到主文內容所在的區域
    content_div = soup.find("div", class_="ls-text")
    
    if not content_div:
        print(f"❌ 無法找到主文內容: {url}")
        return None
    
    # 擷取主文內容
    paragraphs = content_div.find_all("p")
    content_text = "\n".join([p.get_text(strip=True) for p in paragraphs])
    
    # 組合 JSON
    data = {
        "content": content_text
    }
    
    # 儲存 JSON
    filename = url.split("/")[-1].replace(".html", "") + ".json"
    json_path = os.path.join(JSON_FOLDER, filename)
    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    
    print(f"📂 已儲存: {json_path}")
    return data

def scrape_lifestudy():
    """ 讓使用者輸入網址來爬取生命讀經內容 """
    while True:
        url = input("\n請輸入生命讀經網址 (或輸入 'exit' 離開)：").strip()
        if url.lower() == "exit":
            break
        if not url.startswith("https://www.lsmchinese.org/lifestudy/"):
            print("❌ 請輸入有效的生命讀經網址！")
            continue
        get_lifestudy_content(url)
        time.sleep(1)  # 避免過度請求

if __name__ == "__main__":
    print("\n📖 生命讀經爬取工具 📖")
    scrape_lifestudy()
