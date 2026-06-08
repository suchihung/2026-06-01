#python中不能混用空格鍵和Tab鍵
import streamlit as st
import json
from groq import Groq

# 頁面設定
st.set_page_config(page_title="附中 AI 導覽員")
st.title("陽明交大附中 - 阿北導覽")

# 讀取背景知識
try:
    with open('tour.json', 'r', encoding='utf-8') as f:
        context_data = json.load(f)
        context_text = json.dumps(context_data, ensure_ascii=False)
except FileNotFoundError:
    st.error("找不到 tour.json 檔案")
    st.stop()
except Exception as e:
    st.error(f"讀取 JSON 發生錯誤：{e}")
    st.stop()

# 系統人設指令
system_instruction = (
    f"你是陽明交大附中導覽員「阿北」。\n"
    f"請優先參考以下內容回答。\n\n"
    f"內容：\n{context_text}"
)

# 初始化 API 與對話
if "groq_client" not in st.session_state:
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except KeyError:
        st.error("未找到 GROQ_API_KEY")
        st.stop()

    # 建立 Groq 客戶端
    client = Groq(api_key=api_key)
    st.session_state.groq_client = client

    st.session_state.messages = [
        {"role": "assistant", "content": "你好，我是導覽員阿北，請隨時發問。"}
    ]

# 顯示歷史紀錄
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 處理使用者輸入
if prompt := st.chat_input("想問什麼事"):
    st.chat_message("user").write(prompt)

    # 將使用者訊息加入歷史紀錄清單中
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("處理中"):
        try:
            # 將系統人設與歷史紀錄合併，準備傳給 Groq
            api_messages = [{"role": "system", "content": system_instruction}] + st.session_state.messages

            # 呼叫 Groq API
            response = st.session_state.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=api_messages,
                temperature=0.7
            )

            # 取得模型回應文字
            response_text = response.choices[0].message.content

            st.chat_message("assistant").write(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})

        except Exception as e:
            st.error(f"對話發生異常：{e}")
