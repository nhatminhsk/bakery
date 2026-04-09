from langgraph.graph import StateGraph, MessagesState, START, END
from app.chat.llms.gemini import LLM
from app.chat.databases.database import MongoDB
from app.chat.databases.sqlite_db import init_db
from app.chat.retriever.retriever import Retriever
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from typing import Any, List
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import os
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

# Khởi tạo database
init_db()

class State(MessagesState):
    context: List[str]

# Build Retriever
mongo_atlas_uri = os.getenv("MONGO_ATLAS_URI")
collection = MongoDB(uri=mongo_atlas_uri, db_name="mydb", collection_name="backery")
embedding_model = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
retriever = Retriever(collection=collection, embedding_model=embedding_model, index_name="vector_index", text_key="document")
def retrieve(state: State):
    query = state["messages"][-1].content
    docs = retriever.retrieve(query)
    docs = [doc.page_content for doc in docs]
    return {"context": docs}

# Build LLM
instruction = """Bạn là trợ lý tư vấn bán hàng của tiệm bánh [TÊN TIỆM]. Nhiệm vụ của bạn là giúp khách hàng tìm kiếm, tư vấn và đặt mua bánh một cách thân thiện, nhiệt tình.

## VAI TRÒ
- Tư vấn sản phẩm bánh phù hợp với nhu cầu khách hàng
- Cung cấp thông tin chi tiết về sản phẩm (tên, giá, mô tả, tình trạng hàng)
- Hỗ trợ khách hàng trong quá trình chọn mua

## DỮ LIỆU SẢN PHẨM
Bạn được cung cấp danh sách bánh với các trường thông tin sau:
- **Tên bánh**: tên sản phẩm
- **Giá**: giá bán (có thể có nhiều mức theo size/biến thể)
- **Tình trạng hàng**: còn hàng / hết hàng / theo đơn đặt trước
- **Mô tả**: thành phần, hương vị, đặc điểm sản phẩm
- **Link sản phẩm**: đường dẫn xem chi tiết và đặt hàng
- **Ảnh**: hình minh họa sản phẩm

## QUY TẮC TƯ VẤN
1. Khi khách hỏi chung chung ("có bánh gì?", "bánh sinh nhật"), hãy hỏi thêm để thu hẹp lựa chọn: dịp gì, sở thích hương vị, ngân sách, số lượng người ăn.
2. Gợi ý tối đa 3-5 sản phẩm phù hợp nhất, kèm ảnh và link nếu có.
3. Nếu sản phẩm **hết hàng**, thông báo rõ ràng và gợi ý sản phẩm thay thế tương tự.
4. Luôn hiển thị giá rõ ràng. Nếu có nhiều mức giá theo size, liệt kê đầy đủ.
5. Không bịa thêm thông tin ngoài dữ liệu được cung cấp. Nếu không có thông tin, hãy nói thật và đề nghị khách liên hệ trực tiếp.
6. Khi khách muốn đặt hàng, cung cấp link sản phẩm và hướng dẫn đặt hàng qua [KÊNH ĐẶT HÀNG: website / Zalo / fanpage].

## PHONG CÁCH GIAO TIẾP
- Thân thiện, niềm nở, dùng ngôn ngữ tự nhiên
- Xưng hô: "em" với khách, gọi khách là "anh/chị" (hoặc điều chỉnh theo ngữ cảnh)
- Dùng emoji bánh nhẹ nhàng để tạo cảm giác thân thiện 🎂🍰
- Phản hồi ngắn gọn, đúng trọng tâm, không dài dòng

## GIỚI HẠN
- Chỉ tư vấn về sản phẩm bánh và dịch vụ của tiệm
- Không thảo luận các chủ đề không liên quan đến việc mua bánh
- Nếu khách hỏi ngoài phạm vi, lịch sự dẫn chủ đề về sản phẩm/dịch vụ

## DỮ LIỆU SẢN PHẨM
{PRODUCT_DATA}"""

model = LLM()

def call_model(state: State):
    contexts = state["context"]

    sys_prompt = instruction.format(PRODUCT_DATA="\n\n".join(contexts))
    
    response = model.invoke([SystemMessage(content=sys_prompt, id="system")] + state["messages"])

    return {"messages": response}

# Build Graph
builder = StateGraph(State)

builder.add_node(retrieve)
builder.add_node(call_model)

builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "call_model")
builder.add_edge("call_model", END)

memory = MemorySaver()

graph = builder.compile(checkpointer=memory)


def _content_to_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict):
                text_parts.append(str(item.get("text", item)))
            else:
                text_parts.append(str(item))
        return "\n".join(text_parts)
    return str(content)


def chat_once(user_id: str, chat_session_id: str, new_query: str) -> str:
    thread_id = f"{user_id}:{chat_session_id}"
    result = graph.invoke(
        {"messages": [HumanMessage(content=new_query)]},
        config={"configurable": {"thread_id": thread_id}},
    )

    messages = result.get("messages", [])
    for message in reversed(messages):
        if isinstance(message, AIMessage):
            return _content_to_text(message.content)

    if messages:
        return _content_to_text(getattr(messages[-1], "content", ""))
    return ""
