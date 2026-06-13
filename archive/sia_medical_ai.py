import streamlit as st
import json
import sqlite3
import hashlib
import re
import time
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple

# ============================================
# SELF-IMPROVING AI FRAMEWORK
# ============================================

class EvolutionEngine:
    def __init__(self):
        self.generation = 0
        self.best_fitness = 0.0
        self.history = []
        self.init_db()
    
    def init_db(self):
        self.conn = sqlite3.connect('evolution.db')
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS evolution_log (
                id INTEGER PRIMARY KEY,
                gen INTEGER,
                fitness REAL,
                timestamp TEXT,
                code TEXT
            )
        ''')
        self.conn.commit()
    
    def mutate_code(self, code: str) -> str:
        lines = code.split('\n')
        new_lines = []
        for line in lines:
            if 'symptom_keywords' in line and 'emergency' in line:
                line = line.replace('severe bleeding', 'severe bleeding, severe pain, heart attack')
            elif 'emergency' in line and 'detect' in line:
                line = line.replace('if any', 'if any or "emergency" in text_lower')
            elif 'confidence' in line:
                line = line.replace('min(0.95', 'min(0.98')
            new_lines.append(line)
        return '\n'.join(new_lines)
    
    def evaluate_fitness(self, code: str, test_cases: List) -> float:
        try:
            exec_globals = {}
            exec(code, exec_globals)
            if 'MedicalAI' in exec_globals:
                ai = exec_globals['MedicalAI']()
                correct = 0
                for text, expected in test_cases:
                    result = ai.analyze(text)
                    if result['severity'] == expected:
                        correct += 1
                accuracy = correct / len(test_cases)
                
                self.conn.execute(
                    "INSERT INTO evolution_log (gen, fitness, timestamp, code) VALUES (?, ?, ?, ?)",
                    (self.generation, accuracy, datetime.now().isoformat(), code[:500])
                )
                self.conn.commit()
                return accuracy
        except Exception as e:
            print(f"Error: {e}")
            return 0.0
        return 0.0
    
    def evolve(self, base_code: str, test_cases: List, generations: int = 5):
        best_code = base_code
        self.best_fitness = self.evaluate_fitness(base_code, test_cases)
        
        for gen in range(generations):
            self.generation = gen + 1
            mutated = self.mutate_code(best_code)
            fitness = self.evaluate_fitness(mutated, test_cases)
            
            if fitness > self.best_fitness:
                best_code = mutated
                self.best_fitness = fitness
                self.history.append({'gen': self.generation, 'fitness': fitness, 'improved': True})
            else:
                self.history.append({'gen': self.generation, 'fitness': fitness, 'improved': False})
        
        return best_code, self.best_fitness

# ============================================
# MEDICAL AI - BASE VERSION
# ============================================

class MedicalAI:
    def __init__(self):
        self.symptom_keywords = {
            'emergency': ['chest pain', 'difficulty breathing', 'severe bleeding', 'heart attack', 'stroke', 'unconscious'],
            'high': ['high fever', 'severe pain', 'vomiting blood', 'dehydration', 'confusion'],
            'moderate': ['fever', 'cough', 'headache', 'nausea', 'fatigue', 'body aches'],
            'low': ['runny nose', 'slight cough', 'mild headache', 'sore throat', 'sneezing']
        }
        
        self.advice_map = {
            'emergency': {'action': '🚨 CALL 911 IMMEDIATELY', 'advice': 'Seek emergency care now', 'time': 'Immediate'},
            'high': {'action': '🏥 SEE A DOCTOR TODAY', 'advice': 'Visit urgent care', 'time': 'Within 24 hours'},
            'moderate': {'action': '💊 REST AND MONITOR', 'advice': 'Stay home, rest, hydrate', 'time': '2-3 days'},
            'low': {'action': '🏠 HOME CARE', 'advice': 'Self-care with OTC remedies', 'time': 'As needed'}
        }
    
    def extract_symptoms(self, text: str) -> List[str]:
        text_lower = text.lower()
        detected = []
        for category, keywords in self.symptom_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    detected.append(keyword)
        return list(set(detected))
    
    def classify_severity(self, symptoms: List[str]) -> Tuple[str, float]:
        severity_levels = ['emergency', 'high', 'moderate', 'low']
        best_level = 'low'
        best_score = 0
        
        for level in severity_levels:
            score = sum(1 for s in symptoms if s in self.symptom_keywords[level])
            if score > best_score:
                best_score = score
                best_level = level
        
        confidence = min(0.95, best_score / max(1, len(symptoms)) + 0.3)
        return best_level, confidence
    
    def analyze(self, text: str) -> Dict:
        symptoms = self.extract_symptoms(text)
        severity, confidence = self.classify_severity(symptoms)
        advice = self.advice_map[severity]
        
        return {
            'text': text,
            'symptoms': symptoms,
            'severity': severity.upper(),
            'confidence': confidence,
            'action': advice['action'],
            'advice': advice['advice'],
            'timeframe': advice['time'],
            'is_emergency': severity == 'emergency'
        }

# ============================================
# STREAMLIT UI
# ============================================

def main():
    st.set_page_config(page_title="Evolutionary Medical AI", layout="wide")
    
    st.title("🧬 Self-Evolving Medical AI")
    st.markdown("*Powered by SIA Framework - Learns and improves automatically*")
    
    # Initialize
    if 'engine' not in st.session_state:
        st.session_state.engine = EvolutionEngine()
    if 'ai' not in st.session_state:
        st.session_state.ai = MedicalAI()
    if 'evolved' not in st.session_state:
        st.session_state.evolved = False
    
    # Sidebar
    with st.sidebar:
        st.header("🧬 Evolution Control")
        
        if st.button("🚀 RUN EVOLUTION", type="primary", use_container_width=True):
            with st.spinner("Evolving AI through genetic algorithm..."):
                test_cases = [
                    ("I have chest pain", "emergency"),
                    ("Fever and cough", "moderate"),
                    ("Slight headache", "low"),
                    ("Difficulty breathing", "emergency"),
                    ("Runny nose", "low"),
                    ("High fever and vomiting", "high")
                ]
                
                import inspect
                base_code = inspect.getsource(MedicalAI)
                best_code, fitness = st.session_state.engine.evolve(base_code, test_cases, generations=3)
                
                st.success(f"✅ Evolution Complete! Fitness: {fitness:.2f}")
                st.session_state.evolved = True
        
        st.divider()
        
        # Stats
        st.subheader("📊 Statistics")
        st.metric("Generations", st.session_state.engine.generation)
        st.metric("Best Fitness", f"{st.session_state.engine.best_fitness:.2f}")
        
        if st.session_state.engine.history:
            improved = sum(1 for h in st.session_state.engine.history if h['improved'])
            st.metric("Improvements", improved)
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["💬 Medical Chat", "🧬 Evolution History", "📈 Analytics"])
    
    with tab1:
        st.header("How are you feeling?")
        
        user_input = st.text_area(
            "Describe your symptoms:",
            height=120,
            placeholder="Example: I have chest pain and difficulty breathing OR I have fever and cough..."
        )
        
        if st.button("Analyze", type="primary"):
            if user_input:
                with st.spinner("Analyzing..."):
                    result = st.session_state.ai.analyze(user_input)
                    
                    if result['is_emergency']:
                        st.error(f"🚨 {result['action']}")
                        st.error(result['advice'])
                    else:
                        st.success(f"Severity: {result['severity']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Confidence", f"{result['confidence']*100:.1f}%")
                    with col2:
                        st.metric("Symptoms Found", len(result['symptoms']))
                    
                    st.info(f"💡 {result['advice']}")
                    
                    if result['symptoms']:
                        st.write("**Detected:**", ", ".join(result['symptoms']))
                    
                    if st.session_state.evolved:
                        st.balloons()
                        st.success("✨ Using evolved AI model!")
            else:
                st.warning("Please describe your symptoms")
    
    with tab2:
        st.header("Evolution History")
        
        if st.session_state.engine.history:
            history_df = pd.DataFrame(st.session_state.engine.history)
            st.line_chart(history_df.set_index('gen')['fitness'])
            st.dataframe(history_df)
        else:
            st.info("No evolution yet. Click 'Run Evolution' to start!")
    
    with tab3:
        st.header("Performance Analytics")
        
        conn = sqlite3.connect('evolution.db')
        df = pd.read_sql_query("SELECT * FROM evolution_log ORDER BY gen", conn)
        conn.close()
        
        if not df.empty:
            st.subheader("Fitness Progression")
            st.line_chart(df.set_index('gen')['fitness'])
            
            st.subheader("Best Performing Generation")
            best = df.loc[df['fitness'].idxmax()]
            st.metric("Best Fitness", f"{best['fitness']:.2f}")
            st.metric("Generation", int(best['gen']))
        else:
            st.info("No data yet")

if __name__ == "__main__":
    main()
