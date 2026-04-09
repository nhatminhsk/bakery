from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_core.documents import Document


class Retriever:
    def __init__(self, collection, embedding_model, index_name, text_key):
        self.collection = collection
        self.embedding_model = embedding_model
        self.index_name = index_name
        self.text_key = text_key

    def retrieve(self, query: str, top_k: int = 5, exact: bool = True):
        # Tạo embedding cho truy vấn
        query_embedding = self.embedding_model.embed_query(query)

        # MongoDB Atlas Vector Search: exact search để quét toàn bộ dữ liệu
        pipeline = [
            {
                "$vectorSearch": {
                    "index": self.index_name,
                    "path": "embeddings",
                    "queryVector": query_embedding,
                    "exact": exact,  # exact=True quét toàn bộ 43 mẫu, chính xác 100%
                    "limit": top_k
                }
            },
            {
                "$project": {
                    "similarityScore": {"$meta": "vectorSearchScore"},
                    "_id": 1,
                    self.text_key: 1
                }
            }
        ]

        # Thực hiện truy vấn và lấy kết quả
        results = list(self.collection.aggregate(pipeline))

        # Chuyển đổi kết quả thành danh sách Document
        docs = [
            Document(
                page_content=result.get(self.text_key, ""),
                metadata={k: v for k, v in result.items()
                         if k not in [self.text_key, "embeddings", "_id"]}
            )
            for result in results
        ]
        return docs