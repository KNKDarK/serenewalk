from typing import List, Optional

MEDICAL_CONDITIONS = [
    {
        "condition": "Common Cold",
        "symptoms": "runny nose, sneezing, sore throat, mild cough, slight fatigue, nasal congestion",
        "treatment": "Rest, stay hydrated, use over-the-counter cold medications, saline nasal spray, honey for cough",
        "when_to_see_doctor": "If symptoms persist beyond 10 days, high fever develops, or difficulty breathing occurs"
    },
    {
        "condition": "Influenza (Flu)",
        "symptoms": "high fever, body aches, fatigue, cough, sore throat, headache, chills",
        "treatment": "Antiviral medications (if caught early), rest, hydration, fever reducers like acetaminophen or ibuprofen",
        "when_to_see_doctor": "If high fever persists beyond 3 days, difficulty breathing, chest pain, or confusion"
    },
    {
        "condition": "Migraine",
        "symptoms": "severe headache, nausea, sensitivity to light, sensitivity to sound, visual aura, throbbing pain",
        "treatment": "Rest in dark quiet room, caffeine, over-the-counter pain relievers, prescription migraine medications, cold compress",
        "when_to_see_doctor": "If migraines are frequent, severe, or accompanied by fever, stiff neck, or neurological symptoms"
    },
    {
        "condition": "Tension Headache",
        "symptoms": "mild headache, dull aching sensation, scalp tenderness, neck pain, pressure around forehead",
        "treatment": "Over-the-counter pain relievers, stress management, proper posture, adequate sleep, massage",
        "when_to_see_doctor": "If headaches are persistent, worsen, or interfere with daily activities"
    },
    {
        "condition": "Gastroenteritis (Stomach Flu)",
        "symptoms": "nausea, vomiting, diarrhea, stomach cramps, mild fever, dehydration",
        "treatment": "BRAT diet (bananas, rice, applesauce, toast), oral rehydration solutions, rest, avoid dairy and fatty foods",
        "when_to_see_doctor": "If symptoms last more than 3 days, severe dehydration, bloody stool, or high fever"
    },
    {
        "condition": "Allergic Rhinitis",
        "symptoms": "sneezing, runny nose, itchy eyes, nasal congestion, watery eyes, itchy throat",
        "treatment": "Antihistamines, nasal corticosteroid sprays, avoidance of allergens, air purifiers, saline nasal rinse",
        "when_to_see_doctor": "If over-the-counter medications are not effective, or symptoms significantly impact quality of life"
    },
    {
        "condition": "Bronchitis",
        "symptoms": "persistent cough, mucus production, chest discomfort, fatigue, mild fever, shortness of breath",
        "treatment": "Rest, hydration, cough suppressants, humidifier, bronchodilators if prescribed, avoid smoke",
        "when_to_see_doctor": "If cough lasts more than 3 weeks, fever above 102°F, bloody mucus, or difficulty breathing"
    },
    {
        "condition": "Strep Throat",
        "symptoms": "severe sore throat, fever, swollen lymph nodes, white patches on tonsils, difficulty swallowing",
        "treatment": "Antibiotics (prescribed), rest, warm salt water gargle, throat lozenges, hydration, soft foods",
        "when_to_see_doctor": "If sore throat is severe, accompanied by fever, or persists more than 48 hours"
    },
    {
        "condition": "Urinary Tract Infection (UTI)",
        "symptoms": "frequent urination, burning sensation during urination, cloudy urine, pelvic pain, urgency",
        "treatment": "Antibiotics (prescribed), increased water intake, cranberry juice, avoid irritants like caffeine, heating pad",
        "when_to_see_doctor": "If symptoms are present, as UTI requires prescription antibiotics to prevent kidney infection"
    },
    {
        "condition": "Sinusitis",
        "symptoms": "facial pain, nasal congestion, headache, thick nasal discharge, fever, reduced sense of smell",
        "treatment": "Nasal saline irrigation, steam inhalation, decongestants, pain relievers, warm compresses",
        "when_to_see_doctor": "If symptoms persist more than 10 days, severe pain, high fever, or vision changes"
    },
    {
        "condition": "Hypertension (High Blood Pressure)",
        "symptoms": "often no symptoms, severe headache, shortness of breath, nosebleeds, chest pain, dizziness",
        "treatment": "Lifestyle changes (diet, exercise, sodium reduction), antihypertensive medications, stress management",
        "when_to_see_doctor": "Regular monitoring is essential; seek immediate care if BP is extremely high with symptoms"
    },
    {
        "condition": "Type 2 Diabetes",
        "symptoms": "increased thirst, frequent urination, fatigue, blurred vision, slow healing, tingling in extremities",
        "treatment": "Blood sugar monitoring, metformin, lifestyle modifications, insulin if needed, regular exercise",
        "when_to_see_doctor": "If you experience diabetes symptoms or have risk factors; regular checkups are essential"
    },
    {
        "condition": "Asthma",
        "symptoms": "wheezing, shortness of breath, chest tightness, coughing (especially at night), difficulty breathing",
        "treatment": "Inhalers (rescue and maintenance), avoiding triggers, breathing exercises, allergy management",
        "when_to_see_doctor": "If asthma attacks are frequent, severe, or rescue inhaler is not providing relief"
    },
    {
        "condition": "Anxiety",
        "symptoms": "excessive worry, restlessness, fatigue, difficulty concentrating, irritability, sleep problems, rapid heartbeat",
        "treatment": "Therapy (CBT), medication (SSRIs), mindfulness, exercise, stress management techniques",
        "when_to_see_doctor": "If anxiety interferes with daily life, causes panic attacks, or persists for weeks"
    },
    {
        "condition": "Food Poisoning",
        "symptoms": "nausea, vomiting, watery diarrhea, stomach cramps, fever, chills",
        "treatment": "Hydration, rest, BRAT diet, avoid solid foods initially, electrolyte solutions",
        "when_to_see_doctor": "If severe dehydration, bloody stool, high fever, or symptoms last more than 3 days"
    },
    {
        "condition": "Pneumonia",
        "symptoms": "high fever, cough with phlegm, shortness of breath, chest pain when breathing, fatigue",
        "treatment": "Antibiotics (bacterial), antiviral medications, rest, hydration, fever reducers, oxygen therapy if severe",
        "when_to_see_doctor": "Immediate medical attention required; pneumonia can be life-threatening without treatment"
    },
    {
        "condition": "Chickenpox",
        "symptoms": "itchy rash, red spots, blisters, fever, fatigue, loss of appetite, headache",
        "treatment": "Calamine lotion, antihistamines, fever reducers, oatmeal baths, avoid scratching",
        "when_to_see_doctor": "If rash spreads to eyes, high fever, difficulty breathing, or signs of skin infection"
    },
    {
        "condition": "Ear Infection",
        "symptoms": "ear pain, hearing difficulty, fever, fluid drainage, dizziness, irritability (in children)",
        "treatment": "Antibiotics (if bacterial), pain relievers, warm compress, rest, avoid water in ear",
        "when_to_see_doctor": "If ear pain is severe, accompanied by high fever, or symptoms persist more than 2 days"
    },
    {
        "condition": "Conjunctivitis (Pink Eye)",
        "symptoms": "redness in eye, itching, discharge, tearing, sensitivity to light, crusting of eyelids",
        "treatment": "Antibiotic eye drops (bacterial), antihistamine drops (allergic), warm compress, good hygiene",
        "when_to_see_doctor": "If vision changes, severe pain, or symptoms persist more than a few days"
    },
    {
        "condition": "Back Pain",
        "symptoms": "muscle ache, shooting pain, limited flexibility, pain radiating down leg, stiffness",
        "treatment": "Rest (limited), ice/heat therapy, over-the-counter pain relievers, gentle stretching, proper posture",
        "when_to_see_doctor": "If pain is severe, lasts more than 2 weeks, accompanied by numbness or leg weakness"
    },
    {
        "condition": "Dehydration",
        "symptoms": "thirst, dry mouth, dark urine, fatigue, dizziness, confusion, decreased urination",
        "treatment": "Oral rehydration solution, water, electrolyte drinks, rest, avoid caffeine and alcohol",
        "when_to_see_doctor": "If severe confusion, inability to keep fluids down, rapid heartbeat, or no urination for 8 hours"
    },
    {
        "condition": "Heat Stroke",
        "symptoms": "high body temperature, confusion, rapid pulse, headache, dizziness, nausea, red hot skin",
        "treatment": "Immediate cooling, move to shade, cold water immersion, fanning, hydration if conscious",
        "when_to_see_doctor": "EMERGENCY - call emergency services immediately; heat stroke is life-threatening"
    },
    {
        "condition": "Skin Rash (Contact Dermatitis)",
        "symptoms": "red rash, itching, dry cracked skin, blisters, burning sensation, swelling",
        "treatment": "Topical corticosteroids, antihistamines, moisturizers, avoid irritants, cool compresses",
        "when_to_see_doctor": "If rash is severe, covers large area, shows signs of infection, or doesn't improve in a week"
    },
    {
        "condition": "Insomnia",
        "symptoms": "difficulty falling asleep, waking frequently, fatigue, irritability, poor concentration, morning tiredness",
        "treatment": "Sleep hygiene, consistent schedule, limiting screen time, relaxation techniques, CBT for insomnia",
        "when_to_see_doctor": "If sleep problems persist for weeks and affect daily functioning"
    },
    {
        "condition": "Acid Reflux (GERD)",
        "symptoms": "heartburn, regurgitation, chest pain, difficulty swallowing, chronic cough, hoarseness",
        "treatment": "Antacids, proton pump inhibitors, dietary changes, elevation of head while sleeping, weight loss",
        "when_to_see_doctor": "If symptoms are frequent, severe, or over-the-counter medications are not effective"
    }
]


class KnowledgeBase:
    def __init__(self, path: str = "data/kb"):
        self.conditions = MEDICAL_CONDITIONS
        self._build_index()

    def _build_index(self):
        self._index = []
        for c in self.conditions:
            tokens = (c["condition"] + " " + c["symptoms"]).lower().split(", ")
            for t in tokens:
                for word in t.split():
                    self._index.append((word.strip().rstrip("s"), c))

    def retrieve(self, query: str, n_results: int = 2) -> List[str]:
        query_words = set(query.lower().split())
        scores = {}
        for cond in self.conditions:
            text = (cond["condition"] + " " + cond["symptoms"]).lower()
            match_count = sum(1 for word in query_words if word in text)
            if match_count > 0:
                scores[cond["condition"]] = scores.get(cond["condition"], 0) + match_count

        if not scores:
            return []

        ranked = sorted(scores.items(), key=lambda x: -x[1])[:n_results]
        results = []
        for condition_name, _ in ranked:
            for c in self.conditions:
                if c["condition"] == condition_name:
                    text = (
                        f"Condition: {c['condition']}\n"
                        f"Symptoms: {c['symptoms']}\n"
                        f"Treatment: {c['treatment']}\n"
                        f"When to see doctor: {c['when_to_see_doctor']}"
                    )
                    results.append(text)
                    break
        return results

    def build_kb(self, data: list) -> int:
        self.conditions = [
            {
                "condition": d.get("condition", "Unknown"),
                "symptoms": d.get("symptoms", ""),
                "treatment": d.get("treatment", "Consult a healthcare professional."),
                "when_to_see_doctor": d.get("when_to_see_doctor", "If symptoms persist or worsen.")
            }
            for d in data
        ]
        self._build_index()
        return len(self.conditions)
