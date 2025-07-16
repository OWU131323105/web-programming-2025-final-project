import streamlit as st
import google.generativeai as genai
import pandas as pd
from datetime import datetime, date
import plotly.express as px
import streamlit_calendar as st_calendar

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
    st.header("推し管理・プロフィール")
    oshiname = st.text_input("推しの名前")
    birthday = st.date_input("誕生日", min_value=date(1900, 1, 1), max_value=date.today())
    
    st.subheader("SNSリンク")
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
    
    st.subheader("好きな曲・動画リスト")
    video_link = st.text_input("YouTubeリンクを入力してください", placeholder="https://youtube.com/...")
    if st.button("リンクを追加"):
        st.session_state.favorite_videos.append(video_link)
        st.success("リンクを追加しました！")
    if st.session_state.favorite_videos:
        st.subheader("追加されたリンク")
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
            st.image(thumbnail_url, caption="サムネイル", use_column_width=True)
    
    appearances = st.text_area("出演情報リンク集")
    if st.button("プロフィールを保存"):
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
        st.subheader("推しプロフィール一覧")
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
                st.image(thumbnail_url, caption="サムネイル", use_column_width=True)
            st.write("出演情報リンク集:", profile["appearances"])

# カレンダーと日記の統合ページ
elif menu == 'カレンダーと日記':
    st.header("推し活カレンダーと日記")
    
    # カレンダー表示
    st.subheader("カレンダー")
    events = [{"date": str(date), "title": event["title"]} for date, event in st.session_state.calendar_events.items()]
    selected_date_dict = st_calendar.calendar(events=events)
    selected_date = str(selected_date_dict.get("selected_date", ""))  # 正しいキーを使用して日付を取得
    
    # イベント入力
    st.subheader("イベント入力")
    event_date = st.date_input("イベントの日付を選択してください", value=date.today())  # 自由に日付を選択可能
    event_title = st.text_input("イベントタイトルを入力してください")
    event_note = st.text_area("イベントの詳細を入力してください")
    if st.button("イベントを保存"):
        st.session_state.calendar_events[str(event_date)] = {
            "title": event_title,
            "note": event_note
        }
        st.success("イベントを保存しました！")
    
    # 日記入力
    if selected_date:  # 日付が選択されている場合のみ処理を続行
        st.subheader("日記")
        diary_text = st.text_area("日記を書く", key="diary_text")
        uploaded_image = st.file_uploader("画像をアップロード", type=["jpg", "png"], key="diary_image")
        if st.button("日記を保存"):
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
            st.subheader("日記の詳細")
            st.write("内容:", st.session_state.diary_entries[selected_date]["text"])
            if st.session_state.diary_entries[selected_date]["image"]:
                st.image(st.session_state.diary_entries[selected_date]["image"])
            if st.button("日記を編集"):
                st.session_state.diary_entries[selected_date]["text"] = st.text_area(
                    "内容を編集", st.session_state.diary_entries[selected_date]["text"], key="edit_diary_text"
                )
                st.session_state.calendar_events[selected_date]["note"] = st.session_state.diary_entries[selected_date]["text"]
                st.success("日記を更新しました！")
    
    # カレンダーに表示されるイベント一覧
    st.subheader("イベント一覧")
    for date, event in st.session_state.calendar_events.items():
        st.write(f"{date}: {event['title']} - {event['note']}")

# グッズコレクション
elif menu == 'グッズコレクション':
    st.header("グッズコレクション管理")
    item_name = st.text_input("グッズ名")
    item_image = st.file_uploader("画像をアップロード", type=["jpg", "png"])
    item_date = st.date_input("入手日")
    item_notes = st.text_area("メモ")
    if st.button("グッズを登録"):
        st.session_state.collections.append({
            "name": item_name,
            "image": item_image,
            "date": item_date,
            "notes": item_notes
        })
        st.success("グッズを登録しました！")
    if st.session_state.collections:
        st.subheader("グッズコレクション一覧")
        for item in st.session_state.collections:
            st.write("名前:", item["name"])
            if item["image"]:
                st.image(item["image"])
            st.write("入手日:", item["date"])
            st.write("メモ:", item["notes"])

# 支出管理
elif menu == '支出管理':
    st.header("推し活支出管理")
    expense_date = st.date_input("日付を選択してください")
    expense_category = st.selectbox("カテゴリを選択してください", ["グッズ", "配信", "イベント", "その他"])
    expense_item = st.text_input("項目")
    expense_amount = st.number_input("金額", min_value=0)
    if st.button("支出を記録"):
        st.session_state.expenses.append({
            "date": expense_date,
            "category": expense_category,
            "item": expense_item,
            "amount": expense_amount
        })
        st.success("支出を記録しました！")
    if st.session_state.expenses:
        st.subheader("支出一覧")
        df = pd.DataFrame(st.session_state.expenses)
        st.dataframe(df)
        st.subheader("カテゴリ別支出")
        category_summary = df.groupby("category")["amount"].sum().reset_index()
        fig = px.pie(category_summary, values="amount", names="category", title="カテゴリ別支出")
        st.plotly_chart(fig)

# チャットボット
elif menu == 'チャットボット':
    st.header("シンプルなチャットボット")
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

