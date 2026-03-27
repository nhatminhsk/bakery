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

