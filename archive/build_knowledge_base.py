import json
import chromadb
from sentence_transformers import SentenceTransformer
import os

print("📚 Building Medical Knowledge Base...")

medical_knowledge = [
    {"condition": "Common Cold", "symptoms": "Runny nose, sneezing, sore throat, mild cough", "treatment": "Rest, fluids, over-the-counter cold medicines", "when_to_see_doctor": "Symptoms last more than 10 days, high fever"},
    {"condition": "Flu", "symptoms": "Fever, body aches, fatigue, dry cough, headache", "treatment": "Rest, hydration, antiviral medications if early", "when_to_see_doctor": "High fever, difficulty breathing, chest pain"},
    {"condition": "COVID-19", "symptoms": "Fever, cough, shortness of breath, loss of taste/smell", "treatment": "Isolation, rest, hydration, monitor oxygen levels", "when_to_see_doctor": "Difficulty breathing, chest pain, confusion"},
    {"condition": "Migraine", "symptoms": "Throbbing headache, nausea, light sensitivity, visual aura", "treatment": "Dark quiet room, cold compress, migraine medications", "when_to_see_doctor": "Sudden severe headache, neurological symptoms"},
    {"condition": "Stomach Flu", "symptoms": "Nausea, vomiting, diarrhea, stomach cramps", "treatment": "Hydration, BRAT diet, rest", "when_to_see_doctor": "Blood in vomit/stool, severe pain, dehydration"},
    {"condition": "Allergies", "symptoms": "Sneezing, itchy eyes, runny nose, rash", "treatment": "Antihistamines, avoid triggers, nasal sprays", "when_to_see_doctor": "Difficulty breathing, severe reactions"},
    {"condition": "Sore Throat", "symptoms": "Pain when swallowing, scratchy throat, swollen glands", "treatment": "Warm salt water gargle, honey tea, throat lozenges", "when_to_see_doctor": "Difficulty swallowing, fever >101°F, lasts >1 week"},
    {"condition": "Fever", "symptoms": "Temperature >100.4°F, chills, sweating, weakness", "treatment": "Rest, fluids, fever reducers", "when_to_see_doctor": "Fever >103°F, lasts >3 days, infants with fever"},
    {"condition": "Headache", "symptoms": "Pain in head, pressure, tension", "treatment": "Rest, hydration, OTC pain relievers", "when_to_see_doctor": "Sudden severe headache, with fever, after head injury"},
    {"condition": "Back Pain", "symptoms": "Aching or sharp pain in back, muscle stiffness", "treatment": "Rest, ice/heat therapy, gentle stretching", "when_to_see_doctor": "After injury, with leg weakness, loss of bladder control"},
    {"condition": "Hypertension", "symptoms": "Often asymptomatic, headaches, shortness of breath", "treatment": "Low sodium diet, exercise, medications", "when_to_see_doctor": "Regular monitoring, very high readings"}
]

os.makedirs("knowledge_base", exist_ok=True)
client = chromadb.PersistentClient(path="knowledge_base")

try:
    client.delete_collection("medical_knowledge")
except:
    pass

collection = client.create_collection("medical_knowledge")
model = SentenceTransformer("all-MiniLM-L6-v2")

for i, entry in enumerate(medical_knowledge):
    text = f"Condition: {entry['condition']}
Symptoms: {entry['symptoms']}
Treatment: {entry['treatment']}
When to see doctor: {entry['when_to_see_doctor']}"
    embedding = model.encode(text).tolist()
    collection.add(
        documents=[text],
        embeddings=[embedding],
        ids=[f"doc_{i}"],
        metadatas=[{"condition": entry["condition"]}]
    )
    print(f"✓ Added: {entry['condition']}")

print(f"
✅ Knowledge base built with {len(medical_knowledge)} medical conditions")
print("📊 Vector database saved to knowledge_base/ directory")
