import streamlit as st
import sqlite3
import pandas as pd

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

# データベースからすべてのユーザーを取得してDataFrameに変換
def fetch_data():
    df = pd.read_sql("SELECT * FROM users", conn)
    return df

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

                # df = fetch_data()
                # st.dataframe(df)  # データフレームを表示

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
            st.success(f"ログインに成功しました！\nようこそ、{user[1]} {user[0]} さん")
            st.session_state['page'] = 'yoyaku'
        else:
            st.error('ユーザー名またはパスワードが間違っています。')

# メインアプリケーションの部分
def main():
    if 'page' not in st.session_state:
        st.session_state['page'] = 'login'

    if st.session_state['page'] == 'login':
        st.sidebar.title('メニュー')
        option = st.sidebar.selectbox('選択してください', ['サインアップ', 'ログイン'])

        if option == 'サインアップ':
            signup()
        elif option == 'ログイン':
            login()

    elif st.session_state['page'] == 'yoyaku':
        import yoyaku  # yoyaku.pyをインポートして表示

if __name__ == '__main__':
    main()

# データベース接続を閉じる
conn.close()
