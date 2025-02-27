import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_FILE = "gospelassistant-452215-3aa41b17c041.json"

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

# 測試是否能開啟 Google Sheet
SPREADSHEET_ID = "1u_3vop6W3AAqZV9QadkeDteXuco7QJnuG_NkbgK8bjQ"
spreadsheet = client.open_by_key(SPREADSHEET_ID)
print("✅ 成功連線到 Google Sheets！")
