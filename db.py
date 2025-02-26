import firebase_admin
from firebase_admin import credentials, firestore
from config import FIREBASE_CREDENTIALS_PATH  # 匯入 Firebase 金鑰路徑

# 初始化 Firebase
cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
firebase_admin.initialize_app(cred)
db = firestore.client()

def add_care_item(user_id, name, content):
    """將關懷名單存入 Firestore"""
    doc_ref = db.collection("care_list").document(user_id)
    doc_ref.set({"name": name, "content": content})

def get_care_list():
    """取得所有關懷名單"""
    docs = db.collection("care_list").stream()
    return [{"name": doc.to_dict()["name"], "content": doc.to_dict()["content"]} for doc in docs]
