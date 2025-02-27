import firebase_admin
from firebase_admin import credentials, firestore
from config import FIREBASE_CREDENTIALS_PATH  # 匯入 Firebase 金鑰路徑
import os

# 初始化 Firebase
# 如果是在本地環境（非 Render），則載入 憑證檔案
if not os.getenv("RENDER"):
    cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
else:
    cred = credentials.Certificate("/etc/secrets/gospelassistant-firebase-adminsdk-fbsvc-69aeff154b.json")

firebase_admin.initialize_app(cred)
db = firestore.client()

def add_care_item(user_id, name, situation, date, time):
    """將關懷名單存入 Firestore"""
    doc_ref = db.collection("care_list").document(user_id)
    #doc_ref.set({"name": name, "content": situation, "date": date, "time": time})
    # 嘗試取得現有資料
    doc = doc_ref.get()
    if doc.exists:
        existing_data = doc.to_dict().get("care_items", [])
    else:
        existing_data = []

    # 新增新資料
    existing_data.append({
        "name": name,
        "situation": situation,
        "date": date,
        "time": time
    })
    # 更新 Firestore
    doc_ref.set({"care_items": existing_data})

def get_care_list():
    """取得所有關懷名單"""
    docs = db.collection("care_list").stream()
    care_list = []
    for doc in docs:
        data = doc.to_dict()
        care_items = data.get("care_items", [])  # 取得 care_items 陣列
        care_list.extend(care_items)  # 合併所有 care_items 到 care_list
    return care_list


def save_conversation(user_id, messages):
    """儲存使用者對話紀錄"""
    db.collection("conversations").document(user_id).set({"messages": messages})

def get_conversation(user_id):
    """取得使用者對話紀錄"""
    doc = db.collection("conversations").document(user_id).get()
    return doc.to_dict().get("messages", []) if doc.exists else []