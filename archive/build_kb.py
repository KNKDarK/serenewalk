import chromadb
from sentence_transformers import SentenceTransformer
import os

print("Building medical knowledge base...")

medical_data = [
    ("Common Cold", "Runny nose, sneezing, sore throat, mild cough", "Rest, fluids, rest"),
    ("Flu", "Fever, body aches, fatigue, dry cough", "Rest, hydration, monitor fever"),
    ("COVID-19", "Fever, cough, shortness of breath, loss of taste", "Isolation, rest, monitor oxygen"),
    ("Migraine", "Throbbing headache, nausea, light sensitivity", "Dark room, rest, cold compress"),
    ("Stomach Flu", "Nausea, vomiting, diarrhea, cramps", "Hydration, rest, bland foods")
]

os.makedirs("knowledge_base", exist_ok=True)
client = chromadb.PersistentClient(path="knowledge_base")

try:
    client.delete_collection("medical_knowledge")
except:
    pass

collection = client.create_collection("medical_knowledge")
model = SentenceTransformer("all-MiniLM-L6-v2")

for i, (condition, symptoms, treatment) in enumerate(medical_data):
    text = f"Condition: {condition} Symptoms: {symptoms} Treatment: {treatment}"
    embedding = model.encode(text).tolist()
    collection.add(
        documents=[text],
        embeddings=[embedding],
        ids=[f"doc_{i}"],
        metadatas=[{"condition": condition}]
    )
    print(f"Added: {condition}")

print(f"Done! Added {len(medical_data)} conditions")

# Add more conditions to build_kb.py
