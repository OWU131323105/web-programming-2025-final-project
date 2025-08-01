import streamlit as st
from PIL import Image
import google.generativeai as genai
import pandas as pd
from datetime import datetime, date
import plotly.express as px
import streamlit_calendar as st_calendar




# サイドバーの一番上にテーマカラー選択
with st.sidebar:
    st.markdown('### 🎨 テーマカラーを選択')
    default_color = '#ffb6c1'
    theme_color = st.color_picker('好きな色を選んでね', value=st.session_state.get('theme_color', default_color), key='theme_color')

# 明るい色・濃い色を自動生成（簡易）
import colorsys
def adjust_color(hex_color, factor):
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
    l = max(0, min(1, l * factor))
    r2, g2, b2 = colorsys.hls_to_rgb(h, l, s)
    return '#{:02x}{:02x}{:02x}'.format(int(r2*255), int(g2*255), int(b2*255))

color_main = theme_color
color_dark = adjust_color(theme_color, 0.7)  # 濃い色
color_light = adjust_color(theme_color, 1.3)  # 明るい色

st.markdown(f'''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kosugi+Maru&display=swap');
    html, body, [class^="css"] {{
        font-family: 'Kosugi Maru', 'Rounded Mplus 1c', 'Meiryo', sans-serif;
        background: linear-gradient(135deg, {color_light} 0%, #fff0f5 100%);
    }}
    .stApp {{
        background: linear-gradient(135deg, {color_light} 0%, #fff0f5 100%);
    }}
    h1, h2, h3, h4 {{
        color: {color_dark};
        font-family: 'Kosugi Maru', 'Rounded Mplus 1c', 'Meiryo', sans-serif;
        border-radius: 12px;
        padding: 4px 12px;
        background: {color_light};
        display: inline-block;
    }}
    .stButton>button {{
        background-color: {color_main};
        color: #fff;
        border-radius: 20px;
        border: none;
        padding: 8px 24px;
        font-size: 18px;
        font-family: 'Kosugi Maru', 'Rounded Mplus 1c', 'Meiryo', sans-serif;
        transition: 0.2s;
    }}
    .stButton>button:hover {{
        background-color: {color_dark};
        color: #fff;
    }}
    .small-delete-btn {{
        background-color: {color_main} !important;
        color: #fff !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 2px 10px !important;
        font-size: 12px !important;
        cursor: pointer !important;
        margin-left: 4px !important;
        transition: 0.2s !important;
        min-width: 0 !important;
        width: auto !important;
        height: auto !important;
    }}
    .small-delete-btn:hover {{
        background-color: {color_dark} !important;
        color: #fff !important;
    }}
    .stTextInput>div>input, .stTextArea textarea {{
        border-radius: 12px;
        border: 2px solid {color_main};
        background: {color_light};
    }}
    .stDataFrameContainer {{
        border-radius: 12px;
        border: 2px solid {color_main};
        background: {color_light};
    }}
    .stSidebar {{
        background: linear-gradient(135deg, {color_light} 0%, #fff0f5 100%);
    }}
    </style>
''', unsafe_allow_html=True)

st.title('推し活サポートアプリ')

# サイドバーで機能選択
menu = st.sidebar.selectbox(
    '機能を選択してください',
    ('プロフィール管理', 'カレンダー', 'グッズコレクション', '支出管理', 'AIチャット')
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
    st.header("💖 推しプロフィール")
    st.markdown("""
あなたの「推し」のすべてをここに集約！名前や誕生日、SNS、推しの「ここが好き！」ポイントまで、あなただけの特別な「推しのプロフィール」を作成・管理できるよ。
""")
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
    
    appearances = st.text_area("🌟 その他")
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
            st.write("その他:", profile["appearances"])

# カレンダー
elif menu == 'カレンダー':
    st.header("📅 推し活カレンダー")
    st.markdown("""
大切な推し活の思い出をカレンダーに記録しよう！イベントに参加した日や配信を見た日、その時の感動や出来事を日記のように残せるよ。後から見返して、推しと過ごした日々を振り返ろう！
""")
    
    # カレンダー表示
    st.subheader("🗓️ カレンダー")
    events = []
    for event_date_str, event_list in st.session_state.calendar_events.items():
        for idx, event in enumerate(event_list):
            events.append({"date": str(event_date_str), "title": event["title"], "color": theme_color})
    selected_date_dict = st_calendar.calendar(events=events)
    selected_date = str(selected_date_dict.get("selected_date", ""))  # 正しいキーを使用して日付を取得
    
    # イベント入力
    st.subheader("🎀 イベント入力")
    event_date = st.date_input("イベントの日付を選択してください", value=date.today())  # 自由に日付を選択可能
    event_title = st.text_input("イベントタイトルを入力してください")
    event_note = st.text_area("イベントの詳細・日記を入力してください")
    if st.button("イベントを保存💾"):
        date_str = str(event_date)
        event_obj = {"title": event_title, "note": event_note}
        if date_str not in st.session_state.calendar_events:
            st.session_state.calendar_events[date_str] = []
        st.session_state.calendar_events[date_str].append(event_obj)
        st.success("イベントを保存しました！")
        st.rerun()
    
    
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
    st.markdown("""
お気に入りの推しグッズを、写真付きで楽しくコレクション！いつ手に入れたかなどの情報も記録して、あなただけのグッズカタログを作ろう！持っているグッズをいつでも一目で確認できるよ。
""")
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
        for idx, item in enumerate(st.session_state.collections):
            col1, col2 = st.columns([8,2])
            with col1:
                st.write("名前:", item["name"])
                if item["image"]:
                    st.image(item["image"])
                st.write("入手日:", item["date"])
                st.write("メモ:", item["notes"])
            with col2:
                if st.button("編集", key=f"edit_goods_{idx}"):
                    st.session_state[f"edit_goods_show_{idx}"] = True
            if st.session_state.get(f"edit_goods_show_{idx}", False):
                new_name = st.text_input("グッズ名を編集", value=item["name"], key=f"edit_goods_name_{idx}")
                new_image = st.file_uploader("画像を再アップロード（省略可）", type=["jpg", "png"], key=f"edit_goods_image_{idx}")
                new_date = st.date_input("入手日を編集", value=item["date"], key=f"edit_goods_date_{idx}")
                new_notes = st.text_area("メモを編集", value=item["notes"], key=f"edit_goods_notes_{idx}")
                if st.button("更新", key=f"edit_goods_update_{idx}"):
                    st.session_state.collections[idx]["name"] = new_name
                    if new_image is not None:
                        st.session_state.collections[idx]["image"] = new_image
                    st.session_state.collections[idx]["date"] = new_date
                    st.session_state.collections[idx]["notes"] = new_notes
                    st.session_state[f"edit_goods_show_{idx}"] = False
                    st.success("グッズ情報を更新しました！")
                    st.rerun()
            st.divider()

# 支出管理
elif menu == '支出管理':
    st.header("💰 推し活支出管理")
    st.markdown("""
推し活にかける愛の証を「見える化」！グッズ購入や配信への課金など、推し活の支出を記録すれば、何にどれくらい使っているかがグラフで一目瞭然。かしこく楽しい推し活にしよう！
""")
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
                delete_btn = st.button("削除", key=f"delete_expense_{idx}")
                st.markdown('<style>div[data-testid="stButton"] button {min-width:0;width:auto;height:auto;padding:2px 10px;font-size:12px;border-radius:50px;background-color:#ffb6c1;color:#fff;}</style>', unsafe_allow_html=True)
                if delete_btn:
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
elif menu == 'AIチャット':
    st.header("推し活サポートAIチャット")
    st.markdown("""
推し活での「知りたい！」や「困ったな」は、AIチャットボットにお任せ！イベント情報から会場アクセス、ライブの準備、お得なグッズ購入方法まで、あなたの質問に的確にお答えするよ。
""")
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-lite')
    prompt = st.chat_input("「このイベントの会場はどのくらいのキャパ？」「この会場に行くまでに、◯◯からだとどのくらいかかる？」「次のライブに向けて何を準備したらいい？」")
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

