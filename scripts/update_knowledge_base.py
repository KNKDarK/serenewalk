import pandas as pd
import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.knowledge import KnowledgeBase

def process_and_update_kb():
    print("Loading dataset...")
    csv_path = "data/raw_dataset/Final_Augmented_dataset_Diseases_and_Symptoms.csv"
    
    # Read CSV
    df = pd.read_csv(csv_path)
    
    print(f"Dataset loaded. Shape: {df.shape}")
    
    # Group by disease
    # We take the mean of symptoms for each disease. If its > 0.5, we count it as a symptom for that disease.
    # This helps filter out noise if the augmentation added random 1s.
    grouped = df.groupby('diseases').mean()
    
    kb_data = []
    
    print("Processing diseases...")
    for disease, symptoms_series in grouped.iterrows():
        # Get symptoms where value > 0.2 (common symptoms for this disease)
        common_symptoms = symptoms_series[symptoms_series > 0.2].index.tolist()
        
        if not common_symptoms:
            continue
            
        kb_data.append({
            "condition": disease,
            "symptoms": ", ".join(common_symptoms),
            "treatment": "Consult a healthcare professional for a formal diagnosis and treatment plan.",
            "when_to_see_doctor": "If symptoms persist, worsen, or interfere with daily activities."
        })
    
    print(f"Processed {len(kb_data)} unique diseases.")
    
    # Initialize and build KB
    print("Updating Vector Database (this might take a while)...")
    kb = KnowledgeBase(path="data/kb")
    count = kb.build_kb(kb_data)
    
    print(f"Successfully indexed {count} conditions into the knowledge base.")

if __name__ == "__main__":
    process_and_update_kb()
