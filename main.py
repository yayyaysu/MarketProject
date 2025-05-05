from fastapi import FastAPI
from pydantic import BaseModel
import openai
from readBubble import BubbleAPI
import os

# 初始化 FastAPI 應用
app = FastAPI()

# 設定 OpenAI API 金鑰
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("未設置 OPENAI_API_KEY 環境變數")
client = openai.OpenAI(api_key=api_key)

# 初始化 Bubble API 客戶端
api_token = os.getenv("BUBBLE_API_TOKEN")
if not api_token:
    raise ValueError("未設置 BUBBLE_API_TOKEN 環境變數")
bubble = BubbleAPI(api_token)

# 定義請求模型
class Question(BaseModel):
    user_question: str

@app.post("/ask")
def ask_ai(question: Question):
    user_question = question.user_question

    # 從 Bubble 讀取 Market 資料
    market_data = bubble.get_data("market", limit=10)

    if not market_data or "response" not in market_data or not market_data["response"]["results"]:
        return {"error": "無法從 Bubble 讀取市集資料"}

    # 過濾出 name 為 "小人類市集" 的資料
    filtered_markets = [m for m in market_data["response"]["results"] if m.get("name") == "小人類市集"]

    if not filtered_markets:
        return {"error": "找不到小人類市集資料"}

    first_market = filtered_markets[0]

    market_info = {
        "name": first_market.get("name", "未提供"),
        "location": first_market.get("location", "未提供"),
        "time": first_market.get("time", "未提供"),
        "organizer": first_market.get("organizer", "未提供"),
        "description": first_market.get("description", "未提供")
    }

    # 合成 prompt
    prompt = f"""你是一位友善的活動客服，根據市集資訊回答使用者問題。
使用者問題：
{user_question}

市集資訊如下：
名稱：{market_info['name']}
地點：{market_info['location']}
時間：{market_info['time']}
主辦方：{market_info['organizer']}
詳細規則：{market_info['description']}

回答規則：
1. 僅依據上述提供的市集資訊回答，不要編造任何未提及的細節
2. 如果問題涉及到的內容在上述資訊中沒有提到，請明確告知「很抱歉，目前沒有相關資訊」
3. 不要假設任何未明確提及的資訊
4. 回答要簡潔、準確，並引用來源資訊
5. 不確定的部分，請建議使用者直接聯繫主辦方
"""

    # 呼叫 OpenAI API
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "你是一位活動問答專員。你只能根據提供的資訊回答問題，若資料中沒有相關資訊，請明確表示不知道，而不是猜測或編造答案。"},
            {"role": "user", "content": prompt}
        ]
    )

    reply = response.choices[0].message.content
    return {
        "question": user_question,
        "reply": reply
    }
