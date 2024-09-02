import streamlit as st
import sqlite3

# SQLiteデータベースに接続（なければ自動で作成）
conn = sqlite3.connect('wgs.db', check_same_thread=False)
c = conn.cursor()

# ユーザー情報のテーブル作成
c.execute('''CREATE TABLE IF NOT EXISTS users
             (last_name TEXT, first_name TEXT, email TEXT, username TEXT, password TEXT)''')

# データの挿入関数
def add_user(last_name, first_name, email, username, password):
    c.execute("INSERT INTO users (last_name, first_name, email, username, password) VALUES (?, ?, ?, ?, ?)", 
              (last_name, first_name, email, username, password))
    conn.commit()

# 登録済みGmailアドレスの確認関数
def is_email_registered(email):
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    return c.fetchone()

# ユーザーの認証関数
def authenticate_user(identifier, password):
    if '@' in identifier:  # Gmailアドレスでの認証
        c.execute("SELECT * FROM users WHERE email = ? AND password = ?", (identifier, password))
    else:  # ユーザー名での認証
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (identifier, password))
    
    return c.fetchone()

# サインアップ機能
def signup():
    st.title('サインアップ')

    last_name = st.text_input('姓を入力してください')
    first_name = st.text_input('名を入力してください')
    email = st.text_input('Gmailアドレスを入力してください。お持ちでない場合には "none" と入力してください')
    password = st.text_input('パスワードを入力してください', type='password')

    username = ""
    email_valid = True

    if st.button('サインアップ'):
        if email.endswith('@gmail.com'):
            username = email
            email_valid = True
            st.write(f"ユーザー名としてGmailアドレスを使用します: {username}")
        elif email == "none":
            username = st.text_input('任意のユーザー名を入力してください')
            email_valid = True
        else:
            email_valid = False
            st.error('Gmailアドレスに誤りがあるか、"none" と記入されていません')

        if last_name and first_name and username and password and email_valid:
            if email != "none" and is_email_registered(email):
                st.error('このGmailアドレスは既に登録されています。別のGmailアドレスを使用してください。')
            else:
                add_user(last_name, first_name, email, username, password)
                st.success('サインアップが完了しました！')
                st.session_state['page'] = 'yoyaku'  # サインアップ後に予約ページにリダイレクト

        else:
            st.error('すべてのフィールドを正しく入力してください。')

# ログイン機能
def login():
    st.title('ログイン')

    identifier = st.text_input('Gmailアドレスまたはユーザー名を入力してください')
    password = st.text_input('パスワードを入力してください', type='password')

    if st.button('ログイン'):
        user = authenticate_user(identifier, password)
        if user:
            st.session_state['logged_in_user'] = {
                'last_name': user[0],
                'first_name': user[1]
            }
            st.success(f"ようこそ、{user[1]}{user[0]}さん。ログインに成功しました！\n左上の 'yoyaku' から予約を行ってください。")

        else:
            st.error('ユーザー名またはパスワードが間違っています。')

# 予約ページ機能
def yoyaku_page():
    st.header('予約ページ')
    st.write("ここで予約の操作を行います。")

# メインアプリケーションの部分
def main():
    if 'page' not in st.session_state:
        st.session_state['page'] = 'login'  # デフォルトはログインページ

    # サイドバーでメニューを追加
    st.sidebar.title("メニュー")
    st.write(f"Current page: {st.session_state['page']}")

    # テスト用：予約ページに直接移動するためのオプションをコメントアウト
    # if st.sidebar.checkbox('テストモード（予約ページ）', value=False):
    #     st.session_state['page'] = 'yoyaku'
    # else:
    # サイドバーから選択したページに移動
    page_selection = st.sidebar.radio('ページを選択してください', ('ログイン', 'サインアップ', '予約ページ'))
    if page_selection == 'ログイン':
        st.session_state['page'] = 'login'
    elif page_selection == 'サインアップ':
        st.session_state['page'] = 'signup'
    elif page_selection == '予約ページ':
        st.session_state['page'] = 'yoyaku'

    # 現在のページに基づいて機能を表示
    if st.session_state['page'] == 'login':
        login()
    elif st.session_state['page'] == 'signup':
        signup()
    elif st.session_state['page'] == 'yoyaku':
        yoyaku_page()  # 予約ページの内容を表示

    st.write(st.session_state)



if __name__ == '__main__':
    main()


# データベース接続を閉じる
conn.close()