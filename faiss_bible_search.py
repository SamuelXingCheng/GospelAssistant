import os
import json
import faiss
import numpy as np
from openai import OpenAI
from config import OPENAI_API_KEY  # 匯入環境變數
from tqdm import tqdm  # 進度條
import time

# 載入 OpenAI API
client = OpenAI(api_key=OPENAI_API_KEY)

# 設定 JSON 資料夾與 FAISS 索引檔案
JSON_FOLDER = "bible_json/各章"
FAISS_INDEX_FILE = "bible_faiss-030301.index"
TEXTS_FILE = "bible_texts-030301.json"  # 存儲文本資料

# 設定向量維度（text-embedding-ada-002 的維度為 1536）
dimension = 1536
# 創建 IVFFlat 索引，nlist 是簇的數量，適合大數據量
# nlist = 610  # 設定倒排桶數，通常是 sqrt(數據量)
nlist = 2749  # 設定倒排桶數，通常是 sqrt(數據量)
quantizer = faiss.IndexFlatL2(dimension)  # 量化器
index = faiss.IndexIVFFlat(quantizer, dimension, nlist, faiss.METRIC_L2)  # IVFFlat 索引（需訓練）


# 存儲經文向量與對應文本
texts = []

def train_faiss_index(embeddings):
    """訓練 FAISS IVFFlat 索引，並顯示進度條"""
    print("🔄 訓練 FAISS IVFFlat 索引...")
    
    # 訓練需要樣本，這裡用進度條模擬
    num_steps = 20  # 訓練進度顯示 10 步
    step_size = len(embeddings) // num_steps

    for i in tqdm(range(num_steps), desc="🚀 FAISS 訓練中", unit="step"):
        time.sleep(0.5)  # 模擬訓練延遲（實際 train() 會同步完成）
    
    index.train(embeddings)  # 執行訓練
    print("✅ FAISS 訓練完成！")

    return index  # 回傳已訓練好的索引


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

                texts.append(full_text)

    # 使用 tqdm 來顯示進度條
    for text in tqdm(texts, desc="✨ 生成嵌入向量"):
        vector = get_embedding(text)
        embeddings.append(vector)

    embeddings = np.array(embeddings, dtype=np.float32)

    # 1. **先訓練 IVFFlat 索引**
    print("🔄 訓練 FAISS IVFFlat 索引...")
    # 訓練 FAISS IVFFlat 索引
    index = train_faiss_index(embeddings)
    # index.train(embeddings)  # IVFFlat 需要先訓練

    # 2. **再加入向量**
    BATCH_SIZE = 10000  # 根據 RAM 設定批次大小
    num_batches = len(embeddings) // BATCH_SIZE + (1 if len(embeddings) % BATCH_SIZE != 0 else 0)

    print("🔄 正在將向量加入 FAISS 索引...")

    for i in tqdm(range(num_batches), desc="📥 添加進度", unit="batch"):
        start = i * BATCH_SIZE
        end = min((i + 1) * BATCH_SIZE, len(embeddings))
        index.add(embeddings[start:end])

    print("✅ 向量添加完成！")

    # 儲存 FAISS 索引

    # **模擬進度條**
    with tqdm(total=100, desc="💾 儲存進度", unit="%") as pbar:
        for _ in range(10):  # 模擬 10 個步驟
            faiss.write_index(index, FAISS_INDEX_FILE)  # 這行還是會直接完成
            time.sleep(0.2)  # 模擬寫入延遲
            pbar.update(10)  # 每次更新 10%

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
        messages=[{"role": "system", "content": "你是一位有趣的聊天員，擅長關心開啟話題，並常分享恢復本聖經的經文。"},
                  {"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content.strip()

# 測試查詢
# query = "從保羅的書信中，如何啟示出神的經綸？"
# print(search_bible(query))
