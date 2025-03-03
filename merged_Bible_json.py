import json
import os

# 設定 JSON 檔案的目錄（假設所有 Bible_xx.json 檔案都在同一個資料夾）
directory = "bible_json"  # ← 替換為你的 JSON 檔案所在資料夾

# 存放合併後的資料
merged_data = {}

# 讀取並合併 Bible_1.json 到 Bible_66.json
for i in range(1, 67):  # Bible_1.json 到 Bible_66.json
    file_name = f"Bible_{i}.json"
    file_path = os.path.join(directory, file_name)

    # 確保檔案存在
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            merged_data[f"Bible_{i}"] = data  # 以 Bible_1, Bible_2 作為 key 存入

# 將合併後的數據存成新的 JSON 檔案
output_file = os.path.join(directory, "Merged_Bible.json")
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(merged_data, f, ensure_ascii=False, indent=4)

print(f"✅ 合併完成！已儲存為 {output_file}")
