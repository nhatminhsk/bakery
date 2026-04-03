# Tài khoản mẫu

- admin: `admin` / `Admin123`
- user: `user1` / `User1234`

---

# Hướng dẫn chạy app

## 1) Lần đầu pull về máy

1. Cài thư viện:

    ```bash
    pip install -r requirements.txt
    ```

2. Nâng cấp schema DB local:

    ```bash
    python upgrade_db_schema.py
    ```

3. Nạp dữ liệu từ snapshot (chỉ cần 1 lần để khởi tạo dữ liệu local):

    ```bash
    python initdata.py
    ```

4. Chạy app:

    ```bash
    python run.py
    ```

## 2) Các lần chạy sau

Chỉ cần chạy:

```bash
python run.py
```

## 3) Khi muốn đồng bộ dữ liệu mới cho cả team

Sau khi thêm/sửa/xóa dữ liệu local và muốn người khác pull về dùng cùng dữ liệu:

```bash
python updatedata.py
```

Sau đó commit file snapshot mới lên git.

## 4) Khi nào cần chạy lại initdata.py

Chỉ chạy khi bạn muốn reset/đồng bộ lại toàn bộ dữ liệu local theo snapshot hiện tại.
Không chạy thường xuyên trong lúc đang làm việc để tránh ghi đè dữ liệu local đang chỉnh sửa.

## II) Backend API Guide - LangGraph Chatbot
## 1. Tong quan
Backend cung cap 1 endpoint de he thong khac goi vao chatbot.

Endpoint: POST /chat
Input JSON:
user_id (string)
chat_session_id (string)
new_query (string)
Output JSON:
answer (string)
API duoc build bang FastAPI, goi LangGraph trong chatbot.py, va luu lich su chat vao SQLite theo cap:

1 user_id
Nhieu chat_session_id
## 2. Cau truc file lien quan
api/main.py: FastAPI app va endpoint /chat
chatbot.py: LangGraph flow + chat_once(...)
databases/sqlite_db.py: tao schema va luu lịch su hoi thoai
test.py: client chat terminal de test API
## 3. Chuan bi moi truong
3.1 Tao virtual env (khuyen nghi)
```bash
conda create -n env python=3.12 -y
```
3.2 Cai dependencies
pip install -r requirements.txt
## 4. Chay API
Tu root project:
```bash
uvicorn app.chat.api_chat:app --host 0.0.0.0 --port 8000 --reload
```
Kiem tra Swagger UI:

http://127.0.0.1:8000/docs
## 6. Contract API chi tiet
6.1 Request
POST http://127.0.0.1:8000/chat

Header:

Content-Type: application/json
Body:

{
  "user_id": "user_001",
  "chat_session_id": "session_a1",
  "new_query": "Shop co banh sinh nhat cho 6 nguoi khong?"
}
Validation:

Tat ca field la bat buoc
Field khong duoc rong sau khi trim
user_id, chat_session_id: max 128 ky tu
new_query: max 4000 ky tu
6.2 Response thanh cong
HTTP 200

{
  "answer": "..."
}
6.3 Response loi
HTTP 422: payload sai schema/validation cua FastAPI
HTTP 500: loi noi bo trong qua trinh goi model/DB
## 7. Vi du goi API
7.1 PowerShell
$body = @{
  user_id = "user_001"
  chat_session_id = "session_a1"
  new_query = "Goi y giup minh 3 loai banh socola"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/chat" -ContentType "application/json" -Body $body
7.2 curl
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user_001","chat_session_id":"session_a1","new_query":"Cho minh xem banh best seller"}'
## 8. Test nhanh bang terminal chat
Sau khi API dang chay, mo terminal khac:

python test.py
Tuy chon:

python test.py --url http://127.0.0.1:8000/chat --user demo_user --session demo_session_01
Lenh trong chat terminal:

/new: tao session moi
/exit: thoat
## 9. Luu tru lich su chat
SQLite tao cac bang:

users
chat_sessions
messages
Moi request /chat se:

Dam bao user/session ton tai
Luu message role user
Goi LangGraph
Luu message role assistant
Dong thoi LangGraph dung thread_id = user_id:chat_session_id de tach bo nho hoi thoai theo tung session.