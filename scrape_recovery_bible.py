import requests
from bs4 import BeautifulSoup
import json
import re


parseBible_results = "parseBible_results.json"

# 目標網址（馬太福音 第 1 章）
#bible_url = "http://recoveryversion.com.tw/Style0A/026/read_List.php?f_BookNo=40&f_ChapterNo=1"
# 目標經文頁面（請換成實際網址）
base_url = "http://recoveryversion.com.tw/Style0A/026/"  # 這是聖經網站的根網址
bible_url = base_url + "read_List.php?f_BookNo=40&f_ChapterNo=1"  # 這是經文頁面

# 1. 發送請求獲取經文頁面 HTML
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(bible_url, headers=headers)
response.encoding = "utf-8"
soup = BeautifulSoup(response.text, "html.parser")

# 2. 擷取所有經文（處理整章）
bible_data = []
verses = soup.find_all("td", colspan="6")  # 找出所有經文內容
verse_numbers = soup.find_all("td", width="50")  # 找出所有經文號碼

# 只保留符合「章:節」格式的 <td>
verse_tds = []
for td in verses:
    # 跳過標題（標題通常包含 <b> 或 <font>）
    if td.find("b") or td.find("font"):
        continue
    verse_tds.append(td)

for num, verse_td in enumerate(verse_tds):

    verse_number = verse_numbers[num].get_text(strip=True)  # 取得經文號碼 (ex: "1:21", "1:25")

    if verse_td:
        # 提取所有註解
        notes = {}
        for note in verse_td.find_all("a", class_="notes"):
            note_id = note["href"]  # 取得註解的 JavaScript 連結
            note_number = note.get_text(strip=True)  # 註解序號 (如 1, 2)
            notes[note_number] = note_id  # 存入字典 {註解編號: 連結}

            # 提取註解的實際網址
            note_url = base_url + note_id.split("'")[1]  # 轉換成完整 URL
            note_content = "（註解載入失敗）"

            try:
                # 3. 發送請求抓取註解內容
                note_response = requests.get(note_url, headers=headers)
                note_response.encoding = "utf-8"
                note_soup = BeautifulSoup(note_response.text, "html.parser")
                
                # 4. 找到註解的正文（請根據實際 HTML 調整選擇器）
                note_tds = note_soup.find_all("td") 
                for note_td in note_tds:
                    note_content = note_td.find("p")  # 找到 <p> 標籤
                    if note_content:
                        note_content = note_content.get_text(strip=True) # 提取純文字
                print(f" {verse_number} 註解 {note_number} 載入")
            except Exception as e:
                print(f"❌ 註解 {note_number} 無法載入: {e}")

            # 儲存註解
            notes[note_number] = {"content": note_content}

            note.extract()  # 移除註解標籤，避免影響經文內容

        verse_text = verse_td.get_text(" ", strip=True)  # 取得純文字經文
    
        # 儲存經文和註解
        bible_data.append({"verse": verse_number, "text": verse_text, "notes": notes})

# 3. 輸出結果
print("\n=== 📖 整章經文與註解 ===\n")
for entry in bible_data:
    print(f"{entry['verse']}: {entry['text']}")
    for note_num, note_link in entry["notes"].items():
        print(f"  🔹 註解 {note_num}: {note_link}")

with open(parseBible_results, "w", encoding="utf-8") as file:
    json.dump(bible_data, file, indent=4, ensure_ascii=False)