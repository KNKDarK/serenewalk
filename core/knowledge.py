import os
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Optional

class KnowledgeBase:
    def __init__(self, path="data/kb"):
        self.path = path
        self.embed_model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
        self.collection = self._load_collection()

    def _load_collection(self):
        os.makedirs(self.path, exist_ok=True)
        client = chromadb.PersistentClient(path=self.path)
        try:
            return client.get_collection("medical_knowledge")
        except:
            return None

    def build_kb(self, data: List[dict]):
        """
        Builds the vector database from a list of medical conditions.
        Each entry should have 'condition', 'symptoms', 'treatment', 'when_to_see_doctor'.
        """
        client = chromadb.PersistentClient(path=self.path)
        try:
            client.delete_collection("medical_knowledge")
        except:
            pass
        
        collection = client.create_collection("medical_knowledge")
        
        for i, entry in enumerate(data):
            text = f"Condition: {entry['condition']}\nSymptoms: {entry['symptoms']}\nTreatment: {entry['treatment']}\nWhen to see doctor: {entry['when_to_see_doctor']}"
            embedding = self.embed_model.encode(text).tolist()
            collection.add(
                documents=[text],
                embeddings=[embedding],
                ids=[f"doc_{i}"],
                metadatas=[{"condition": entry["condition"]}]
            )
        self.collection = collection
        return len(data)

    def retrieve(self, query: str, n_results: int = 2) -> List[str]:
        if not self.collection:
            return []
        query_embedding = self.embed_model.encode(query).tolist()
        results = self.collection.query(query_embeddings=[query_embedding], n_results=n_results)
        return results["documents"][0] if results["documents"] else []
