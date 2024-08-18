import os
import json
import streamlit as st
from PIL import Image
import pandas as pd
from datetime import datetime, timezone, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

# 現在のUTC時刻をISO 8601形式で取得
now = datetime.now(timezone.utc).isoformat()

# 4週間後の時刻を取得
four_weeks_later = (datetime.now(timezone.utc) + timedelta(weeks=4)).isoformat()

st.title('Wakana Golf School 予約サイト')

st.subheader('自己紹介')
st.text('Pythonに関する情報をYouTube上で発信しているPython VTuber サプーです。\n'
        'よければチャンネル登録よろしくお願いします!')

# Google Calendar API用のスコープ
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# 環境変数からサービスアカウントキーのJSON内容を取得
credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
credentials_info = json.loads(credentials_json) if credentials_json else None

# サービスアカウントの資格情報を設定
credentials = service_account.Credentials.from_service_account_info(credentials_info, scopes=SCOPES)

# Google Calendar APIクライアントの作成
service = build('calendar', 'v3', credentials=credentials)

# Google Calendarから今後の予約枠を取得
calendar_id = '80ad013a3c6366b0b3039a197b9579190b0c0a35459b874d2f63efd1a3ce6cd9@group.calendar.google.com'  # ここに使用したいカレンダーのIDを指定
events_result = service.events().list(
    calendarId=calendar_id,
    maxResults=10,
    singleEvents=True,
    orderBy='startTime',
    timeMin=now,  # 現在の時刻以降の予約枠を取得
    timeMax=four_weeks_later  # 4週間後までの予約枠を取得
).execute()

events = events_result.get('items', [])

if not events:
    st.write('今後4週間以内の予約枠はありません。')
else:
    st.write('今後4週間以内の予約枠:')

    # 予約枠の選択 (複数選択可能)
    options = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        option = f"{start}: {event['summary']}"
        options.append(option)
    
    selected_events = st.multiselect('予約する枠を選んでください:', options)
    
    
    # 予約ボタンの処理
    if st.button('予約する'):
        if not selected_events:
            st.write("予約枠が選択されていません。")
        else:
            for selected_event in selected_events:
                try:
                    # 予約イベントをGoogle Calendarに追加
                    event = {
                        'summary': '予約: ' + selected_event.split(': ')[1],
                        'start': {
                            'dateTime': selected_event.split(': ')[0],
                            'timeZone': 'Asia/Tokyo',  # 適切なタイムゾーンを指定
                        },
                        'end': {
                            'dateTime': (datetime.fromisoformat(selected_event.split(': ')[0]) + timedelta(hours=1)).isoformat(),
                            'timeZone': 'Asia/Tokyo',
                        },
                    }
                    service.events().insert(calendarId=calendar_id, body=event).execute()
                except Exception as e:
                    st.write(f"予約に失敗しました: {selected_event}")
                    st.write(f"エラー: {e}")
            st.write(f'以下の枠で予約を確定しました: {", ".join(selected_events)}')
