import os
import json
import faiss
import numpy as np
from openai import OpenAI
from config import OPENAI_API_KEY  # 匯入環境變數

# 載入 OpenAI API
client = OpenAI(api_key=OPENAI_API_KEY)

# 設定 JSON 資料夾與 FAISS 索引檔案
JSON_FOLDER = "bible_json"
FAISS_INDEX_FILE = "bible_faiss.index"
TEXTS_FILE = "bible_texts.json"  # 存儲文本資料

# 設定向量維度（text-embedding-ada-002 的維度為 1536）
dimension = 1536
index = faiss.IndexFlatL2(dimension)

# 存儲經文向量與對應文本
texts = []

# 取得文字向量
def get_embedding(text):
    response = client.embeddings.create(input=text, model="text-embedding-ada-002")
    return np.array(response.data[0].embedding, dtype=np.float32)

def build_faiss_index():
    """建立 FAISS 索引"""
    global texts
    embeddings = []

    # 遍歷 `bible_json/` 目錄，讀取所有 JSON 檔案
    for filename in os.listdir(JSON_FOLDER):
        if filename.endswith(".json"):
            file_path = os.path.join(JSON_FOLDER, filename)
        
            # 讀取 JSON 檔案
            with open(file_path, "r", encoding="utf-8") as f:
                bible_data = json.load(f)

            # 轉換經文為向量
            for verse in bible_data:
                book_chapter = filename.replace(".json", "")  # 取得書卷與章節名稱
                verse_text = f"{book_chapter} {verse['verse']} {verse['text']}"

                # 合併註解內容
                notes_text = "".join([note['content'] for note in verse.get('notes', {}).values()])
                full_text = verse_text + " " + notes_text

                vector = get_embedding(full_text)
                index.add(np.array([vector]))
                embeddings.append(vector)
                texts.append(full_text)

    # 儲存 FAISS 索引
    faiss.write_index(index, FAISS_INDEX_FILE)
    
    # 儲存文本資料
    with open(TEXTS_FILE, "w", encoding="utf-8") as f:
        json.dump(texts, f, ensure_ascii=False, indent=4)

    print(f"✅ FAISS 索引已建立並儲存為 `{FAISS_INDEX_FILE}`")

def load_faiss_index():
    """載入 FAISS 索引"""
    global texts
    if os.path.exists(FAISS_INDEX_FILE) and os.path.exists(TEXTS_FILE):
        faiss.read_index(FAISS_INDEX_FILE)
        with open(TEXTS_FILE, "r", encoding="utf-8") as f:
            texts = json.load(f)
        print("✅ 已載入 FAISS 索引與經文文本資料")
    else:
        print("⚠️ 未找到 FAISS 索引，將重新建立...")
        build_faiss_index()

# 先嘗試載入索引，若不存在則建立
load_faiss_index()

# 查詢函式
def search_bible(query, top_k=3):
    """搜尋最相關的經文"""
    query_vector = get_embedding(query).reshape(1, -1)
    distances, indices = index.search(query_vector, top_k)

    # 取得最相關的經文
    retrieved_texts = [texts[i] for i in indices[0]]

    # 組合經文作為上下文
    context = "\n".join(retrieved_texts)
        
    # 傳入 OpenAI API 進行回答
    prompt = f"根據以下聖經經文回答問題：\n{context}\n\n問題：{query}\n回答："

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "你是一個聖經解經助手，請根據恢復本的風格回答問題。"},
                  {"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content.strip()

# 測試查詢
query = "我出身不好，怎麼辦？"
print(search_bible(query))
