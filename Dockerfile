# Pythonの公式イメージをベースに使用
FROM python:3.11

# 作業ディレクトリを作成
WORKDIR /app

# 必要な依存パッケージをインストール
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのソースコードをコピー
COPY . .

# Streamlitのポートを指定
EXPOSE 8501

# アプリケーションを起動
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]

COPY .streamlit /app/.streamlit

