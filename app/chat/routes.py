"""
app/chat/routes.py
──────────────────
Blueprint proxy: Flask web → FastAPI chatbot
Đặt file này tại: app/chat/routes.py
"""

import os
import requests
from flask import Blueprint, request, jsonify

chat_bp = Blueprint("chat", __name__)

# URL của FastAPI chatbot (chạy song song với Flask)
CHATBOT_API_URL = os.getenv("CHATBOT_API_URL", "http://localhost:8000/chat")
CHATBOT_TIMEOUT = int(os.getenv("CHATBOT_TIMEOUT", "30"))


@chat_bp.post("/api/chat")
def proxy_chat():
    """
    Nhận request từ widget JS, chuyển tiếp tới FastAPI chatbot,
    rồi trả kết quả về cho trình duyệt.
    """
    payload = request.get_json(silent=True)

    # Validate tối giản
    if not payload:
        return jsonify({"detail": "Request body trống."}), 400

    required = ("user_id", "chat_session_id", "new_query")
    for field in required:
        if not payload.get(field, "").strip():
            return jsonify({"detail": f"Thiếu hoặc rỗng: {field}"}), 400

    try:
        resp = requests.post(
            CHATBOT_API_URL,
            json={
                "user_id":         payload["user_id"].strip(),
                "chat_session_id": payload["chat_session_id"].strip(),
                "new_query":       payload["new_query"].strip(),
            },
            timeout=CHATBOT_TIMEOUT,
        )
        resp.raise_for_status()
        return jsonify(resp.json()), resp.status_code

    except requests.exceptions.ConnectionError:
        return jsonify({"detail": "Không thể kết nối tới chatbot server."}), 503

    except requests.exceptions.Timeout:
        return jsonify({"detail": "Chatbot phản hồi quá lâu, thử lại nhé!"}), 504

    except requests.exceptions.HTTPError as exc:
        # Trả nguyên lỗi từ FastAPI về client
        try:
            detail = exc.response.json()
        except Exception:
            detail = {"detail": "Lỗi từ chatbot server."}
        return jsonify(detail), exc.response.status_code

    except Exception as exc:  # noqa: BLE001
        return jsonify({"detail": f"Lỗi không xác định: {exc}"}), 500