import firebase_admin
from firebase_admin import credentials, firestore
from config import FIREBASE_CREDENTIALS_PATH  # 匯入 Firebase 金鑰路徑
import os


# 初始化 Firebase

cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)

firebase_admin.initialize_app(cred)
db = firestore.client()

def save_user_name(user_id, user_name):
    """將使用者名稱存入 Firestore"""
    db.collection("users").document(user_id).set({
        "name": user_name,
        "created_at": firestore.SERVER_TIMESTAMP
    }, merge=True)

def get_user_name(user_id):
    """從 Firestore 取得使用者名稱"""
    doc = db.collection("users").document(user_id).get()
    return doc.to_dict().get("name") if doc.exists else None

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
        "time": time,
        "user_id": user_id
    })
    # 更新 Firestore
    doc_ref.set({"care_items": existing_data})

def get_care_list():
    from  line_bot import get_line_user_name
    """取得所有關懷名單"""
    docs = db.collection("care_list").stream()
    care_list = []
    for doc in docs:
        data = doc.to_dict()
        care_items = data.get("care_items", [])  # 取得 care_items 陣列

        for item in care_items:
            print("📌 [DEBUG] 查看db.py item:", item)  # 檢查格式
            user_id = item["user_id"]
            #user_id = ""
            print("📌 [DEBUG] 查看db.py user_id:", user_id)  # 檢查格式
            user_name = get_line_user_name(user_id)  # 取得 LINE 使用者名稱
            print("📌 [DEBUG] 查看db.py user_name:", user_name)  # 檢查格式
            item["user_name"] = user_name  # 加入 LINE 名稱
            care_list.append(item)
    return care_list

def get_user_care_list(user_id):
    """取得特定使用者的關懷名單"""
    doc_ref = db.collection("care_list").document(user_id)  # 查詢指定 user_id 的文件
    doc = doc_ref.get()

    if doc.exists:
        data = doc.to_dict()
        return data.get("care_items", [])  # 只回傳該 user_id 的 care_items
    else:
        return []  # 若該使用者沒有資料則回傳空陣列

def delete_care_item(user_id, name):
    """從 Firestore 刪除關懷名單中的特定人"""
    try:
        doc_ref = db.collection("care_list").document(user_id)
        doc = doc_ref.get()

        if doc.exists:
            data = doc.to_dict().get("care_items", [])
            new_data = [entry for entry in data if entry["name"] != name]

            if len(new_data) == len(data):  # 如果名單長度沒變，代表沒找到
                return False

            doc_ref.update({"care_items": new_data})  # 更新 Firestore
            return True
        return False
    except Exception as e:
        print(f"❌ [ERROR] 刪除失敗: {e}")
        return False

def save_conversation(user_id, messages):
    """儲存使用者對話紀錄"""
    db.collection("conversations").document(user_id).set({"messages": messages})

def get_conversation(user_id):
    """取得使用者對話紀錄"""
    doc = db.collection("conversations").document(user_id).get()
    return doc.to_dict().get("messages", []) if doc.exists else []

def is_name_exists(name):
    """檢查關懷名單中是否已有相同人名"""
    docs = db.collection("care_list").stream()
    for doc in docs:
        care_items = doc.to_dict().get("care_items", [])
        for item in care_items:
            if item.get("name") == name:
                return True  # 人名已存在
    return False  # 人名不存在