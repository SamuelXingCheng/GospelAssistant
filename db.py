import firebase_admin
from firebase_admin import credentials, firestore
from config import FIREBASE_CREDENTIALS_PATH  # 匯入 Firebase 金鑰路徑

# 初始化 Firebase
cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
firebase_admin.initialize_app(cred)
db = firestore.client()

def add_care_item(user_id, name, situation, date, time):
    """將關懷名單存入 Firestore"""
    doc_ref = db.collection("care_list").document(user_id)
    doc_ref.set({"name": name, "content": situation, "date": date, "time": time})

def get_care_list():
    """取得所有關懷名單"""
    docs = db.collection("care_list").stream()
    return [{"name": doc.to_dict()["name"], "content": doc.to_dict()["content"]} for doc in docs]

def save_conversation(user_id, messages):
    """儲存使用者對話紀錄"""
    db.collection("conversations").document(user_id).set({"messages": messages})

def get_conversation(user_id):
    """取得使用者對話紀錄"""
    doc = db.collection("conversations").document(user_id).get()
    return doc.to_dict().get("messages", []) if doc.exists else []