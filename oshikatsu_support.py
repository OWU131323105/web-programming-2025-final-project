import streamlit as st
from PIL import Image
import google.generativeai as genai
import pandas as pd
from datetime import datetime, date
import plotly.express as px
import streamlit_calendar as st_calendar


# かわいいCSSを追加
st.markdown('''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kosugi+Maru&display=swap');
    html, body, [class^="css"] {
        font-family: 'Kosugi Maru', 'Rounded Mplus 1c', 'Meiryo', sans-serif;
        background: linear-gradient(135deg, #ffe6f2 0%, #fff0f5 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #ffe6f2 0%, #fff0f5 100%);
    }
    h1, h2, h3, h4 {
        color: #e75480;
        font-family: 'Kosugi Maru', 'Rounded Mplus 1c', 'Meiryo', sans-serif;
        border-radius: 12px;
        padding: 4px 12px;
        background: #fff0f5;
        display: inline-block;
    }
    .stButton>button {
        background-color: #ffb6c1;
        color: #fff;
        border-radius: 20px;
        border: none;
        padding: 8px 24px;
        font-size: 18px;
        font-family: 'Kosugi Maru', 'Rounded Mplus 1c', 'Meiryo', sans-serif;
        transition: 0.2s;
    }
    .stButton>button:hover {
        background-color: #e75480;
        color: #fff;
    }
    .small-delete-btn {
        background-color: #ffb6c1;
        color: #fff;
        border: none;
        border-radius: 50px;
        padding: 2px 10px;
        font-size: 12px;
        cursor: pointer;
        margin-left: 4px;
        transition: 0.2s;
    }
    .small-delete-btn:hover {
        background-color: #e75480;
        color: #fff;
    }
    .stTextInput>div>input, .stTextArea textarea {
        border-radius: 12px;
        border: 2px solid #ffb6c1;
        background: #fff0f5;
    }
    .stDataFrameContainer {
        border-radius: 12px;
        border: 2px solid #ffb6c1;
        background: #fff0f5;
    }
    .stSidebar {
        background: linear-gradient(135deg, #ffe6f2 0%, #fff0f5 100%);
    }
    </style>
''', unsafe_allow_html=True)

st.title('推し活サポートアプリ')

# サイドバーで機能選択
menu = st.sidebar.selectbox(
    '機能を選択してください',
    ('プロフィール管理', 'カレンダーと日記', 'グッズコレクション', '支出管理', 'チャットボット')
)

# 共通のセッションステート初期化
if "profiles" not in st.session_state:
    st.session_state.profiles = []
if "calendar_events" not in st.session_state:
    st.session_state.calendar_events = {}
if "collections" not in st.session_state:
    st.session_state.collections = []
if "diary_entries" not in st.session_state:
    st.session_state.diary_entries = {}
if "expenses" not in st.session_state:
    st.session_state.expenses = []
if "messages" not in st.session_state:
    st.session_state.messages = []
if "favorite_videos" not in st.session_state:
    st.session_state.favorite_videos = []

# プロフィール管理
if menu == 'プロフィール管理':
    st.header("💖 推し管理・プロフィール")
    oshiname = st.text_input("推しの名前")
    birthday = st.date_input("誕生日", min_value=date(1900, 1, 1), max_value=date.today())
    
    st.subheader("🌸 SNSリンク")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        x_link = st.text_input("Xリンク", placeholder="https://twitter.com/...")
    with col2:
        instagram_link = st.text_input("Instagramリンク", placeholder="https://instagram.com/...")
    with col3:
        youtube_link = st.text_input("YouTubeリンク", placeholder="https://youtube.com/...")
    with col4:
        other_link = st.text_input("その他リンク", placeholder="https://...")
    
    oshipoints = st.text_area("推しポイント")
    
    st.subheader("🎶 好きな曲・動画リスト")
    video_link = st.text_input("YouTubeリンクを入力してください", placeholder="https://youtube.com/...")
    if st.button("リンクを追加"):
        st.session_state.favorite_videos.append(video_link)
        st.success("リンクを追加しました！")
    if st.session_state.favorite_videos:
        st.subheader("✨ 追加されたリンク")
        for link in st.session_state.favorite_videos:
            st.write(link)
            # 動画IDを抽出するロジックを改善
            if "v=" in link:
                video_id = link.split("v=")[-1].split("&")[0]  # "v="以降を取得し、"&"で切り取る
            elif "youtu.be/" in link:
                video_id = link.split("youtu.be/")[-1].split("?")[0]  # "youtu.be/"以降を取得し、"?"で切り取る
            else:
                st.error("無効なYouTubeリンクです。")
                continue
            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/0.jpg"
            st.image(thumbnail_url, caption="サムネイル", use_container_width=True)
    
    appearances = st.text_area("🌟 出演情報リンク集")
    if st.button("プロフィールを保存💾"):
        st.session_state.profiles.append({
            "name": oshiname,
            "birthday": birthday,
            "sns_links": {
                "x": x_link,
                "instagram": instagram_link,
                "youtube": youtube_link,
                "other": other_link
            },
            "oshipoints": oshipoints,
            "favorite_videos": st.session_state.favorite_videos,
            "appearances": appearances
        })
        st.success("プロフィールを保存しました！")
    if st.session_state.profiles:
        st.subheader("👑 推しプロフィール一覧")
        for profile in st.session_state.profiles:
            st.write("名前:", profile["name"])
            st.write("誕生日:", profile["birthday"])
            st.write("SNSリンク:")
            st.write("- X:", profile["sns_links"]["x"])
            st.write("- Instagram:", profile["sns_links"]["instagram"])
            st.write("- YouTube:", profile["sns_links"]["youtube"])
            st.write("- その他:", profile["sns_links"]["other"])
            st.write("推しポイント:", profile["oshipoints"])
            st.write("好きな曲・動画リスト:")
            for link in profile["favorite_videos"]:
                st.write(link)
                if "v=" in link:
                    video_id = link.split("v=")[-1].split("&")[0]
                elif "youtu.be/" in link:
                    video_id = link.split("youtu.be/")[-1].split("?")[0]
                else:
                    st.error("無効なYouTubeリンクです。")
                    continue
                thumbnail_url = f"https://img.youtube.com/vi/{video_id}/0.jpg"
                st.image(thumbnail_url, caption="サムネイル", use_container_width=True)
            st.write("出演情報リンク集:", profile["appearances"])

# カレンダーと日記の統合ページ
elif menu == 'カレンダーと日記':
    st.header("📅 推し活カレンダーと日記")
    
    # カレンダー表示
    st.subheader("🗓️ カレンダー")
    events = []
    for event_date_str, event_list in st.session_state.calendar_events.items():
        for idx, event in enumerate(event_list):
            events.append({"date": str(event_date_str), "title": event["title"], "color": "#ffb6c1"})
    selected_date_dict = st_calendar.calendar(events=events)
    selected_date = str(selected_date_dict.get("selected_date", ""))  # 正しいキーを使用して日付を取得
    
    # イベント入力
    st.subheader("🎀 イベント入力")
    event_date = st.date_input("イベントの日付を選択してください", value=date.today())  # 自由に日付を選択可能
    event_title = st.text_input("イベントタイトルを入力してください")
    event_note = st.text_area("イベントの詳細を入力してください")
    if st.button("イベントを保存💾"):
        date_str = str(event_date)
        event_obj = {"title": event_title, "note": event_note}
        if date_str not in st.session_state.calendar_events:
            st.session_state.calendar_events[date_str] = []
        st.session_state.calendar_events[date_str].append(event_obj)
        st.success("イベントを保存しました！")
    
    # 日記入力
    if selected_date:  # 日付が選択されている場合のみ処理を続行
        st.subheader("📔 日記")
        diary_text = st.text_area("日記を書く", key="diary_text")
        uploaded_image = st.file_uploader("画像をアップロード", type=["jpg", "png"], key="diary_image")
        if st.button("日記を保存💾"):
            st.session_state.diary_entries[selected_date] = {
                "text": diary_text,
                "image": uploaded_image
            }
            st.session_state.calendar_events[selected_date] = {
                "title": "日記",
                "note": diary_text
            }
            st.success("日記を保存しました！")
        
        # 日記表示
        if selected_date in st.session_state.diary_entries:
            st.subheader("📝 日記の詳細")
            st.write("内容:", st.session_state.diary_entries[selected_date]["text"])
            if st.session_state.diary_entries[selected_date]["image"]:
                st.image(st.session_state.diary_entries[selected_date]["image"])
            if st.button("日記を編集✏️"):
                st.session_state.diary_entries[selected_date]["text"] = st.text_area(
                    "内容を編集", st.session_state.diary_entries[selected_date]["text"], key="edit_diary_text"
                )
                st.session_state.calendar_events[selected_date]["note"] = st.session_state.diary_entries[selected_date]["text"]
                st.success("日記を更新しました！")
    
    # カレンダーに表示されるイベント一覧
    st.subheader("🎉 イベント一覧")
    for event_date_str, event_list in st.session_state.calendar_events.items():
        for idx, event in enumerate(event_list):
            st.write(f"{event_date_str}: {event['title']} - {event['note']}")
            edit_key = f"edit_event_{event_date_str}_{idx}"
            if st.button("編集✏️", key=edit_key):
                st.session_state[edit_key + "_show"] = True
            if st.session_state.get(edit_key + "_show", False):
                new_date = st.date_input("イベント日付を編集", value=datetime.strptime(str(event_date_str), "%Y-%m-%d").date(), key=edit_key+"_date")
                new_title = st.text_input("イベントタイトルを編集", value=event["title"], key=edit_key+"_title")
                new_note = st.text_area("イベント詳細を編集", value=event["note"], key=edit_key+"_note")
                if st.button("更新💾", key=edit_key+"_update"):
                    new_date_str = str(new_date)
                    # 日付が変更された場合は新しい日付にイベントを移動
                    if new_date_str != str(event_date_str):
                        if new_date_str not in st.session_state.calendar_events:
                            st.session_state.calendar_events[new_date_str] = []
                        st.session_state.calendar_events[new_date_str].append({"title": new_title, "note": new_note})
                        del st.session_state.calendar_events[event_date_str][idx]
                        # 元の日付のイベントリストが空なら削除
                        if not st.session_state.calendar_events[event_date_str]:
                            del st.session_state.calendar_events[event_date_str]
                    else:
                        st.session_state.calendar_events[event_date_str][idx]["title"] = new_title
                        st.session_state.calendar_events[event_date_str][idx]["note"] = new_note
                    st.success("イベントを更新しました！")
                    st.session_state[edit_key + "_show"] = False
                    st.rerun()

# グッズコレクション
elif menu == 'グッズコレクション':
    st.header("🧸 グッズコレクション管理")
    item_name = st.text_input("グッズ名")
    item_image = st.file_uploader("画像をアップロード", type=["jpg", "png"])
    item_date = st.date_input("入手日")
    item_notes = st.text_area("メモ")
    if st.button("グッズを登録🧸"):
        st.session_state.collections.append({
            "name": item_name,
            "image": item_image,
            "date": item_date,
            "notes": item_notes
        })
        st.success("グッズを登録しました！")
    if st.session_state.collections:
        st.subheader("🎀 グッズコレクション一覧")
        for item in st.session_state.collections:
            st.write("名前:", item["name"])
            if item["image"]:
                st.image(item["image"])
            st.write("入手日:", item["date"])
            st.write("メモ:", item["notes"])

# 支出管理
elif menu == '支出管理':
    st.header("💰 推し活支出管理")
    expense_date = st.date_input("日付を選択してください")
    expense_category = st.selectbox("カテゴリを選択してください", ["グッズ", "配信", "イベント", "その他"])
    expense_item = st.text_input("項目")
    expense_amount = st.number_input("金額", min_value=0)
    if st.button("支出を記録💾"):
        st.session_state.expenses.append({
            "date": expense_date,
            "category": expense_category,
            "item": expense_item,
            "amount": expense_amount
        })
        st.success("支出を記録しました！")
    if st.session_state.expenses:
        st.subheader("📊 支出一覧")
        df = pd.DataFrame(st.session_state.expenses)
        st.dataframe(df)
        st.write("削除したい行のボタンを押してください：")
        for idx, expense in enumerate(st.session_state.expenses):
            col1, col2 = st.columns([8,1])
            with col1:
                st.write(f"{expense['date']} | {expense['category']} | {expense['item']} | {expense['amount']}円")
            with col2:
                delete_btn_html = f'''<form action="" method="post"><button class="small-delete-btn" type="submit" name="delete_{idx}">削除</button></form>'''
                st.markdown(delete_btn_html, unsafe_allow_html=True)
                if st.session_state.get(f"delete_{idx}", False) or st.button("", key=f"delete_expense_{idx}", help="削除"):
                    st.session_state.expenses.pop(idx)
                    st.success("支出を削除しました！")
                    st.rerun()
        st.subheader("🍰 カテゴリ別支出")
        if st.session_state.expenses:
            df = pd.DataFrame(st.session_state.expenses)
            category_summary = df.groupby("category")["amount"].sum().reset_index()
            fig = px.pie(
                category_summary,
                values="amount",
                names="category",
                title="カテゴリ別支出",
                color="category",
                color_discrete_map={
                    "グッズ": "#ffb6c1",
                    "配信": "#87ceeb",
                    "イベント": "#ffd700",
                    "その他": "#dda0dd"
                }
            )
            st.plotly_chart(fig)

# チャットボット
elif menu == 'チャットボット':
    st.header("🤖 シンプルなチャットボット")
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-lite')
    prompt = st.chat_input("入力してね")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if prompt:
        message = {
            "role": "user",
            "content": prompt
        }
        st.session_state.messages.append(message)
        with st.chat_message("user"):
            st.markdown(prompt)
        if "イベント" in prompt or "会場" in prompt or "アクセス" in prompt:
            with st.chat_message("assistant"):
                response = model.generate_content(f"推し活に関する質問: {prompt}")
                st.markdown(response.text)
        else:
            with st.chat_message("assistant"):
                response = model.generate_content(prompt)
                st.markdown(response.text)
