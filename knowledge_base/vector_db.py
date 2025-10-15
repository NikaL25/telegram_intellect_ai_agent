import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction


class VectorKnowledgeBase:
    """
    Векторная база знаний на Chroma + sentence-transformers.
    Позволяет добавлять документы и делать поиск по смыслу.
    """

    def __init__(self, persist_directory: str = "./knowledge_base/chroma_data"):
        self.client = chromadb.Client(
            Settings(persist_directory=persist_directory))
        self.embedding_function = SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2")
        self.collection = self.client.get_or_create_collection(
            name="kb_docs",
            embedding_function=self.embedding_function
        )

    def add_document(self, doc_id: str, text: str):
        self.collection.add(
            documents=[text],
            ids=[doc_id]
        )

    def query(self, text: str, top_k: int = 3):
        results = self.collection.query(
            query_texts=[text],
            n_results=top_k
        )
        docs = []
        for doc, score in zip(results['documents'][0], results['distances'][0]):
            docs.append({"text": doc, "score": score})
        return docs
