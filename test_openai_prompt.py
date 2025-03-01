import json
import os
import openai
from datetime import datetime
from config import OPENAI_API_KEY  # 匯入環境變數

# 設定 OpenAI API Key
openai.api_key = OPENAI_API_KEY
client = openai.OpenAI()  # 創建 OpenAI 客戶端

# 讀取 JSON 檔案
with open("prompts.json", "r", encoding="utf-8") as file:
    prompts = json.load(file)

# 設定輸出結果的 JSON 檔案
results_file = "results.json"

# 如果檔案存在，就先讀取舊資料，避免覆蓋
if os.path.exists(results_file):
    with open(results_file, "r", encoding="utf-8") as file:
        try:
            existing_results = json.load(file)
        except json.JSONDecodeError:
            existing_results = []  # 如果檔案格式錯誤，重新初始化為空陣列
else:
    existing_results = []

# 記錄新的測試結果
new_results = []

# 產生時間戳記
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 測試不同角色的 Prompt
for i, prompt_set in enumerate(prompts):
    system_prompt = prompt_set["system"]
    
    print(f"🛠 測試組合 {i+1} - System 設定: {system_prompt}\n")
    
    for j, user_prompt in enumerate(prompt_set["user"]):
        formatted_prompt = user_prompt.format(name="弟兄 A")  # 你可以更換不同的名字
        print(f"🔹 測試 Prompt {j+1}: {formatted_prompt}\n")

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": system_prompt},
                    {"role": "user", "content": formatted_prompt}]
        )

        # 將測試結果存入字典
        result_entry = {
            "timestamp": timestamp,
            "system": system_prompt,
            "user_prompt": formatted_prompt,
            "response": response.choices[0].message.content  # 這裡可以填入 AI 回應
        }
        new_results.append(result_entry)
        print(f"🔹 測試 Prompt:\n{formatted_prompt}\n")
        print(f"🔹 回應:\n{response.choices[0].message.content}\n{'='*50}\n")

# 合併舊結果 + 新結果
all_results = existing_results + new_results

# 將結果存回 results.json
with open(results_file, "w", encoding="utf-8") as file:
    json.dump(all_results, file, indent=4, ensure_ascii=False)

print(f"✅ 已將 {len(new_results)} 筆測試結果存入 {results_file}")
