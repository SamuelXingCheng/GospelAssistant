import json
import faiss
import numpy as np
from openai import OpenAI
from config import OPENAI_API_KEY  # 匯入環境變數

# 載入 OpenAI API
client = OpenAI(api_key=OPENAI_API_KEY)

# 讀取《恢復本聖經》的 JSON 檔案
with open("parseBible_results.json", "r", encoding="utf-8") as f:
    bible_data = json.load(f)

# 取得文字向量
def get_embedding(text):
    response = client.embeddings.create(input=text, model="text-embedding-ada-002")
    return np.array(response.data[0].embedding, dtype=np.float32)

# 設定向量維度（text-embedding-ada-002 的維度為 1536）
dimension = 1536
index = faiss.IndexFlatL2(dimension)

# 存儲經文向量與對應文本
embeddings = []
texts = []

for verse in bible_data:
    verse_text = f"馬太福音 {verse['verse']} {verse['text']}"
    
    # 合併註解內容
    notes_text = "".join([note['content'] for note in verse.get('notes', {}).values()])
    full_text = verse_text + " " + notes_text
    
    vector = get_embedding(full_text)
    index.add(np.array([vector]))
    embeddings.append(vector)
    texts.append(full_text)

# 儲存 FAISS 索引
faiss.write_index(index, "bible_faiss.index")

# 查詢函式
def search_bible(query, top_k=3):
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
