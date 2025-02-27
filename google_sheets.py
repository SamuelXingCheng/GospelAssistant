import gspread
from google.oauth2.service_account import Credentials
from db import get_care_list  # 取得關懷名單的函式
import logging

# 設定 Logging
logging.basicConfig(level=logging.INFO)

# 設定 Google Sheets API 憑證與權限範圍
SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_FILE = "gospelassistant-452215-3aa41b17c041.json"  # Google Sheets API 憑證檔案

# 授權並連接 Google Sheets
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

# 指定 Google Sheets ID
SPREADSHEET_ID = "1u_3vop6W3AAqZV9QadkeDteXuco7QJnuG_NkbgK8bjQ"  # 替換成你的試算表 ID
spreadsheet = client.open_by_key(SPREADSHEET_ID)

def update_google_sheet(sheet_name="自動更新表"):
    from  line_bot import get_line_user_name
    """同步 Firestore / Supabase 的關懷名單到 Google Sheets"""
    sheet = spreadsheet.worksheet(sheet_name)  # 選擇指定的分頁
    care_list = get_care_list()  # 取得資料庫中的所有關懷名單
    
    # 清空分頁內容
    sheet.clear()
    logging.info(f"📌 收到 Update sheet 請求: {care_list}")
    # 插入標題列
    sheet.append_row(["日期", "姓名", "校園", "系級", "情況", "接觸人"])
    
    # 插入名單資料
    for care in care_list:
        user_name = get_line_user_name(care.get("user_id"))  # 取得 LINE 使用者名稱
        sheet.append_row([
            care.get("date", "無日期"),
            care.get("name", "未知"),
            "逢甲",
            care.get("系級", ""),
            care.get("situation", "無內容"),
            user_name
            
        ])

    print("✅ 牧養名單已同步到 Google Sheets！")

# 測試時可執行此程式來同步 Google Sheets
if __name__ == "__main__":
    update_google_sheet(debug=True)
