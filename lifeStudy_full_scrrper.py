import requests
from bs4 import BeautifulSoup
import json
import time
import re
import os


# 根據選擇的版本決定 BASE_URL
BASE_URL = "https://www.lsmchinese.org/lifestudy/"
INDEX_PAGE = BASE_URL + "index.html"  # 生命讀經索引頁

def sanitize_filename(name):
    """移除不合法的檔名字元"""
    return re.sub(r'[\/:*?"<>|]', '_', name)

def is_old_testament(book_name):
    old_testament_books = {
        "創世記", "出埃及記", "利未記", "民數記", "申命記", "約書亞記", "士師記", "路得記", 
        "撒母耳記", "列王紀", "歷代志", 
        "以斯拉記", "尼希米記", "以斯帖記", "約伯記", "詩篇", "箴言", "傳道書", "雅歌", 
        "以賽亞書", "耶利米書", "耶利米哀歌", "以西結書", "但以理書", "何西阿書", 
        "約珥書", "阿摩司書", "俄巴底亞書", "約拿書", "彌迦書", "那鴻書", "哈巴谷書", 
        "西番雅書", "哈該書", "撒迦利亞書", "瑪拉基書"
    }
    return book_name in old_testament_books

def get_book_links():
    """擷取所有書卷的名稱與對應索引頁連結"""
    response = requests.get(INDEX_PAGE)
    soup = BeautifulSoup(response.text, 'html.parser')
    books = {}
    for td in soup.select('table.ls-index td a'):
        name = td.text.strip()
        link = BASE_URL + td['href'].strip()
        books[name] = link  # 書卷名稱: 索引頁網址
    return books

def get_chapter_links(book_name, book_url):
    """擷取單本書的所有章節連結"""
    response = requests.get(book_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    chapters = {}
    for a in soup.select('div.ls-text p a'):  # 章節索引內的連結
        title = a.text.strip()
        if is_old_testament(book_name):
            link = BASE_URL + "ot/" + a['href'].strip()
        else:
            link = BASE_URL + a['href'].strip()
        chapters[title] = link  # 章節標題: 章節網址
    return chapters

def scrape_chapter_content(chapter_url):
    """擷取單篇章節的內容"""
    response = requests.get(chapter_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    content_div = soup.find('div', class_='ls-text')
    
    if not content_div:
        print(f"❌ 無法找到主文內容", chapter_url)
        return None

    return content_div.get_text("\n", strip=True) if content_div else "內容抓取失敗"

def main():
    book_links = get_book_links()  # 取得所有書卷
    all_books_content = {}

    for book_name, book_url in book_links.items():
        # **先檢查 JSON 檔案是否已存在**
        safe_book_name = sanitize_filename(book_name)  # 確保檔名合法
        json_filename = f"{safe_book_name}.json"

        if os.path.exists(json_filename):
            print(f"⏭️  跳過《{book_name}》，檔案已存在 ({json_filename})")
            continue  # **跳過已存在的書卷**


        print(f"📖 抓取《{book_name}》索引...")
        chapter_links = get_chapter_links(book_name, book_url)  # 取得書卷內所有章節
        book_content = {}

        for chapter_name, chapter_url in chapter_links.items():
            print(f"📄 抓取《{book_name}》{chapter_name}...")
            book_content[chapter_name] = scrape_chapter_content(chapter_url)
            time.sleep(1)  # 避免過快請求被封鎖

        all_books_content[book_name] = book_content  # 存入該書卷的內容

        with open(f"{sanitize_filename(book_name)}.json", "w", encoding="utf-8") as f:
            json.dump(book_content, f, ensure_ascii=False, indent=4)
        
        print(f"✅ 已儲存 {book_name}")

    # 儲存為 JSON 檔
    with open("生命讀經完整.json", "w", encoding="utf-8") as f:
        json.dump(all_books_content, f, ensure_ascii=False, indent=4)

    print("✅ 所有書卷與章節抓取完成！")

if __name__ == "__main__":
    main()
