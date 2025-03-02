import requests
from bs4 import BeautifulSoup
import json
import re
import time
import os

# 設定儲存 JSON 的資料夾
JSON_FOLDER = "bible_json"

# 如果資料夾不存在，則自動建立
os.makedirs(JSON_FOLDER, exist_ok=True)

# 聖經網站的根網址
BASE_URL = "http://recoveryversion.com.tw/Style0A/026/"

# 聖經 66 卷書及其章數（中譯名可改）
BIBLE_BOOKS = {
    1: 50,  # 創世記
    2: 40,  # 出埃及記
    3: 27,  # 利未記
    4: 36,  # 民數記
    5: 34,  # 申命記
    6: 24,  # 約書亞記
    7: 21,  # 士師記
    8: 4,   # 路得記
    9: 31,  # 撒母耳記上
    10: 24, # 撒母耳記下
    11: 22, # 列王紀上
    12: 25, # 列王紀下
    13: 29, # 歷代志上
    14: 36, # 歷代志下
    15: 10, # 以斯拉記
    16: 13, # 尼希米記
    17: 10, # 以斯帖記
    18: 42, # 約伯記
    19: 150,# 詩篇
    20: 31, # 箴言
    21: 12, # 傳道書
    22: 8,  # 雅歌
    23: 66, # 以賽亞書
    24: 52, # 耶利米書
    25: 5,  # 耶利米哀歌
    26: 48, # 以西結書
    27: 12, # 但以理書
    28: 14, # 何西阿書
    29: 3,  # 約珥書
    30: 9,  # 阿摩司書
    31: 1,  # 俄巴底亞書
    32: 4,  # 約拿書
    33: 7,  # 彌迦書
    34: 3,  # 那鴻書
    35: 3,  # 哈巴谷書
    36: 3,  # 西番雅書
    37: 2, # 哈該書
    38: 14,  # 撒迦利亞書
    39: 4,  # 瑪拉基書
    40: 28, # 馬太福音
    41: 16, # 馬可福音
    42: 24, # 路加福音
    43: 21, # 約翰福音
    44: 28, # 使徒行傳
    45: 16, # 羅馬書
    46: 16, # 哥林多前書
    47: 13, # 哥林多後書
    48: 6,  # 加拉太書
    49: 6,  # 以弗所書
    50: 4,  # 腓立比書
    51: 4,  # 歌羅西書
    52: 5,  # 帖撒羅尼迦前書
    53: 3,  # 帖撒羅尼迦後書
    54: 6,  # 提摩太前書
    55: 4,  # 提摩太後書
    56: 3,  # 提多書
    57: 1,  # 腓利門書
    58: 13, # 希伯來書
    59: 5,  # 雅各書
    60: 5,  # 彼得前書
    61: 3,  # 彼得後書
    62: 5,  # 約翰一書
    63: 1,  # 約翰二書
    64: 1,  # 約翰三書
    65: 1,  # 猶大書
    66: 22  # 啟示錄
}


# 四福音書
GOSPELS = {
    40: 28,  # 馬太福音
    41: 16,  # 馬可福音
    42: 24,  # 路加福音
    43: 21   # 約翰福音
}

def get_bible_chapter(book_no: int, chapter_no: int):
    """ 抓取指定的聖經書卷與章節 """
    
    # 生成 URL
    bible_url = f"{BASE_URL}read_List.php?f_BookNo={book_no}&f_ChapterNo={chapter_no}"
    
    # 送出請求
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(bible_url, headers=headers)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")

    # 儲存經文資料
    bible_data = []
    verses = soup.find_all("td", colspan="6")  # 經文內容
    verse_numbers = soup.find_all("td", width="50")  # 經文號碼

    # 過濾掉標題（通常有 <b> 或 <font>）
    verse_tds = [td for td in verses if not (td.find("b") or td.find("font"))]

    for num, verse_td in enumerate(verse_tds):
        verse_number = verse_numbers[num].get_text(strip=True)  # 取得經文號碼 (ex: "1:21")

        # 處理註解
        notes = {}
        for note in verse_td.find_all("a", class_="notes"):
            note_id = note["href"]
            note_number = note.get_text(strip=True)

            # 取得註解網址
            note_url = BASE_URL + note_id.split("'")[1]
            note_content = "（註解載入失敗）"

            try:
                note_response = requests.get(note_url, headers=headers)
                note_response.encoding = "utf-8"
                note_soup = BeautifulSoup(note_response.text, "html.parser")

                # 找到註解內容
                note_tds = note_soup.find_all("td")
                for note_td in note_tds:
                    note_p = note_td.find("p")
                    if note_p:
                        note_content = note_p.get_text(strip=True)
                print(f" {verse_number} 註解 {note_number} 載入")
            except Exception as e:
                print(f"❌ 註解 {note_number} 無法載入: {e}")

            notes[note_number] = {"content": note_content}
            note.extract()  # 移除註解標籤

        verse_text = verse_td.get_text(" ", strip=True)  # 取得純文字經文

        bible_data.append({"verse": verse_number, "text": verse_text, "notes": notes})

    # 儲存 JSON
    json_filename = f"{JSON_FOLDER}/Bible_{book_no}_{chapter_no}.json"
    with open(json_filename, "w", encoding="utf-8") as file:
        json.dump(bible_data, file, indent=4, ensure_ascii=False)

    print(f"\n📂 已儲存: {json_filename}")
    return bible_data

def scrape_full_bible():
    """ 自動爬取 66 卷書的所有章節 """
    for book_no, total_chapters in BIBLE_BOOKS.items():
        for chapter_no in range(1, total_chapters + 1):
            print(f"\n📖 爬取 聖經 {book_no} 卷 第 {chapter_no} 章...")
            get_bible_chapter(book_no, chapter_no)
            time.sleep(1)  # 避免過度請求，被伺服器封鎖

def scrape_gospels():
    """ 只爬取四福音書（馬太福音、馬可福音、路加福音、約翰福音） """
    for book_no, total_chapters in GOSPELS.items():
        for chapter_no in range(1, total_chapters + 1):
            print(f"\n📖 爬取 福音書 {book_no} 卷 第 {chapter_no} 章...")
            get_bible_chapter(book_no, chapter_no)
            time.sleep(1)  # 避免過度請求，被伺服器封鎖

def scrape_specific_chapter():
    """ 讓使用者輸入書卷號碼與章數，自訂爬取單一章節 """
    try:
        book_no = int(input("\n請輸入書卷號碼（1-66）："))
        if book_no not in BIBLE_BOOKS:
            print("❌ 無效的書卷號碼！請重新輸入。")
            return
        
        chapter_no = int(input(f"請輸入章數（1-{BIBLE_BOOKS[book_no]}）："))
        if chapter_no < 1 or chapter_no > BIBLE_BOOKS[book_no]:
            print("❌ 無效的章數！請重新輸入。")
            return

        print(f"\n📖 正在爬取 聖經 第 {book_no} 卷 第 {chapter_no} 章...")
        get_bible_chapter(book_no, chapter_no)

    except ValueError:
        print("❌ 輸入格式錯誤！請輸入數字。")

# 測試
if __name__ == "__main__":
    print("\n📖 聖經爬取工具 📖")
    print("1. 爬取完整聖經")
    print("2. 爬取四福音書")
    print("3. 爬取特定書卷與章節")

    mode = input("\n請選擇模式（1/2/3）：")

    if mode == "1":
        scrape_full_bible()
    elif mode == "2":
        scrape_gospels()
    elif mode == "3":
        scrape_specific_chapter()
    else:
        print("❌ 無效輸入，請輸入 1、2 或 3")