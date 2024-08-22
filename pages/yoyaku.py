import streamlit as st
import datetime
from dateutil import parser
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Google Calendar APIの認証情報をセットアップ
def get_calendar_service():
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["google_credentials"],
        scopes=["https://www.googleapis.com/auth/calendar.events"]
    )
    service = build("calendar", "v3", credentials=credentials)
    return service

# 予約を表示する関数
def display_reservations(service, user_name):
    # 現在の時刻を取得
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # 予約枠を取得するカレンダーIDを指定
    calendar_id = '80ad013a3c6366b0b3039a197b9579190b0c0a35459b874d2f63efd1a3ce6cd9@group.calendar.google.com'

    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=now,
        maxResults=10,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])

    if not events:
        st.write("予約可能な枠が見つかりませんでした。")
        return

    options = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        summary = event['summary']
        option = f"{start}: {summary}"
        options.append(option)
    
    selected_events = st.multiselect('予約する枠を選んでください:', options)

    if st.button('予約する'):
        if not selected_events:
            st.write("予約枠が選択されていません。")
        else:
            for selected_event in selected_events:
                start_time = selected_event.split(': ')[0]
                summary = selected_event.split(': ')[1]
                try:
                    start_time_dt = parser.parse(start_time)
                except ValueError as e:
                    st.error(f"日時のパースに失敗しました: {str(e)}")
                    return

                formatted_start = start_time_dt.strftime("%Y/%m/%d (%A) %H:%M")
                end_time_dt = start_time_dt + datetime.timedelta(hours=1)
                formatted_end = end_time_dt.strftime("%H:%M")
                formatted_summary = f"予約枠: {summary}"
                
                st.write(f"{user_name}さん、以下の枠で予約を確定しました: {formatted_start}-{formatted_end}; {formatted_summary}")

# メイン
def main():
    if 'logged_in_user' not in st.session_state:
        st.warning("まずはログインしてください。")
        st.stop()

    st.title('予約ページ')
    service = get_calendar_service()
    user_name = st.session_state['logged_in_user']['first_name']  # ログインしたユーザーの名前を取得
    display_reservations(service, user_name)

if __name__ == '__main__':
    main()
