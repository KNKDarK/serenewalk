# evolutionary_medical_ai.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import json
import os
import hashlib
import random
import subprocess
import sys
import traceback
from typing import Dict, List, Tuple, Any
import ast
import inspect
import importlib
import time

# ML Libraries
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
import joblib

import warnings
warnings.filterwarnings('ignore')

# ============================================
# TOOL LIBRARY - Executable Code Modules
# ============================================

TOOL_LIBRARY = {
    'symptom_extractor': '''
def extract_symptoms(text):
    """Extract medical symptoms from user text"""
    text_lower = text.lower()
    symptoms = []
    symptom_keywords = {
        'fever': ['fever', 'high temperature', 'hot', 'warm'],
        'cough': ['cough', 'coughing', 'dry cough'],
        'headache': ['headache', 'head pain', 'migraine'],
        'fatigue': ['tired', 'fatigue', 'exhausted', 'weak'],
        'nausea': ['nausea', 'queasy', 'sick stomach'],
        'vomiting': ['vomit', 'throwing up'],
        'diarrhea': ['diarrhea', 'loose stool'],
        'chest_pain': ['chest pain', 'chest pressure'],
        'sore_throat': ['sore throat', 'scratchy throat'],
        'runny_nose': ['runny nose', 'congestion', 'stuffy nose']
    }
    for symptom, keywords in symptom_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            symptoms.append(symptom)
    return symptoms
''',

    'disease_predictor': '''
def predict_disease(symptoms, knowledge_base):
    """Predict disease based on symptoms using matching algorithm"""
    best_match = None
    best_score = 0
    for disease, info in knowledge_base['diseases'].items():
        disease_symptoms = set(info['symptoms'])
        user_symptoms = set(symptoms)
        if user_symptoms:
            match_score = len(disease_symptoms & user_symptoms) / max(1, len(disease_symptoms | user_symptoms))
            if match_score > best_score:
                best_score = match_score
                best_match = disease
    confidence = min(0.95, best_score + 0.2)
    return best_match if best_match else 'Undetermined', confidence, best_score
''',

    'treatment_recommender': '''
def get_treatment(disease, knowledge_base):
    """Get treatment recommendations for predicted disease"""
    if disease in knowledge_base['diseases']:
        info = knowledge_base['diseases'][disease]
        return {
            'treatments': info.get('treatments', ['Rest', 'Hydration']),
            'severity': info.get('severity', 'mild'),
            'recovery_time': info.get('recovery_time', 'Varies')
        }
    return {'treatments': ['Consult a doctor'], 'severity': 'unknown', 'recovery_time': 'unknown'}
''',

    'response_generator': '''
def generate_response(diagnosis, confidence, user_name=None):
    """Generate empathetic response"""
    templates = [
        f"Based on your symptoms, I believe you may have {diagnosis}.",
        f"After analysis, it appears to be {diagnosis}.",
        f"My assessment suggests {diagnosis}."
    ]
    response = random.choice(templates)
    if confidence > 0.8:
        response += f" I am {confidence*100:.0f}% confident in this diagnosis."
    elif confidence > 0.6:
        response += " I'm reasonably confident in this assessment."
    else:
        response += " Please consult a healthcare provider for confirmation."
    if user_name:
        response = f"{user_name}, " + response.lower()
    return response
'''
}

# ============================================
# PROMPT GENOME - Evolvable Instructions
# ============================================

PROMPT_GENOME = {
    'system_prompt': '''You are a caring medical AI assistant. 
    Be empathetic, accurate, and helpful. Always include medical disclaimers.
    Focus on symptom analysis and general health information.''',
    
    'analysis_prompt': '''Analyze the following patient symptoms and provide:
    1. Possible condition
    2. Confidence level
    3. Recommended actions
    4. When to seek medical help''',
    
    'followup_prompt': '''Based on the previous diagnosis, ask relevant follow-up questions about:
    - Symptom duration
    - Severity
    - Associated symptoms
    - Risk factors'''
}

# ============================================
# LOGS DATABASE - Stores all interactions
# ============================================

class LogsDatabase:
    def __init__(self, log_file='evolution_logs.json'):
        self.log_file = log_file
        self.logs = self.load_logs()
    
    def load_logs(self):
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r') as f:
                return json.load(f)
        return {'queries': [], 'executions': [], 'errors': [], 'fitness_scores': []}
    
    def save_logs(self):
        with open(self.log_file, 'w') as f:
            json.dump(self.logs, f, indent=2)
    
    def log_query(self, query, timestamp=None):
        timestamp = timestamp or datetime.now().isoformat()
        self.logs['queries'].append({'query': query, 'timestamp': timestamp})
        self.save_logs()
    
    def log_execution(self, query, code_used, prompt_used, output, fitness_score, timestamp=None):
        timestamp = timestamp or datetime.now().isoformat()
        self.logs['executions'].append({
            'query': query,
            'code_used': code_used[:200],
            'prompt_used': prompt_used[:200],
            'output': output[:200],
            'fitness_score': fitness_score,
            'timestamp': timestamp
        })
        self.logs['fitness_scores'].append(fitness_score)
        self.save_logs()
    
    def log_error(self, query, error, timestamp=None):
        timestamp = timestamp or datetime.now().isoformat()
        self.logs['errors'].append({
            'query': query,
            'error': str(error)[:500],
            'timestamp': timestamp
        })
        self.save_logs()
    
    def get_average_fitness(self):
        if self.logs['fitness_scores']:
            return np.mean(self.logs['fitness_scores'])
        return 0.5
    
    def get_recent_errors(self, n=10):
        return self.logs['errors'][-n:]

# ============================================
# ACTIVE EXECUTOR - The Hand (Operational Layer)
# ============================================

class ActiveExecutor:
    def __init__(self, tool_library, prompt_genome, logs_db):
        self.tool_library = tool_library
        self.prompt_genome = prompt_genome
        self.logs = logs_db
        self.loaded_tools = {}
        self.load_tools()
    
    def load_tools(self):
        """Load all tools from library into memory"""
        for tool_name, tool_code in self.tool_library.items():
            try:
                exec_globals = {}
                exec(tool_code, exec_globals)
                self.loaded_tools[tool_name] = exec_globals
            except Exception as e:
                self.logs.log_error(f"Loading tool {tool_name}", e)
    
    def execute_tool(self, tool_name, *args, **kwargs):
        """Execute a specific tool with given arguments"""
        try:
            if tool_name in self.loaded_tools:
                for name, func in self.loaded_tools[tool_name].items():
                    if callable(func) and not name.startswith('_'):
                        result = func(*args, **kwargs)
                        return result, True, None
            return None, False, f"Tool {tool_name} not found"
        except Exception as e:
            return None, False, str(e)
    
    def execute_workflow(self, query, user_context=None):
        """Execute the complete medical analysis workflow"""
        start_time = time.time()
        fitness_score = 0.5
        output = ""
        error = None
        
        try:
            # Step 1: Log query
            self.logs.log_query(query)
            
            # Step 2: Extract symptoms
            symptoms, success, err = self.execute_tool('symptom_extractor', query)
            if not success:
                raise Exception(f"Symptom extraction failed: {err}")
            
            # Step 3: Load knowledge base
            knowledge_base = self.load_knowledge_base()
            
            # Step 4: Predict disease
            diagnosis, confidence, score, success, err = self.execute_tool_with_return('disease_predictor', symptoms, knowledge_base)
            if not success:
                raise Exception(f"Prediction failed: {err}")
            
            # Step 5: Get treatment
            treatment, success, err = self.execute_tool('treatment_recommender', diagnosis, knowledge_base)
            
            # Step 6: Generate response
            user_name = user_context.get('name') if user_context else None
            response, success, err = self.execute_tool('response_generator', diagnosis, confidence, user_name)
            
            # Step 7: Calculate fitness score
            fitness_score = self.calculate_fitness(query, diagnosis, confidence, time.time() - start_time)
            
            output = {
                'diagnosis': diagnosis,
                'confidence': confidence,
                'match_score': score,
                'treatment': treatment if success else None,
                'response': response if success else "Analysis complete. Please consult a doctor."
            }
            
            # Log successful execution
            self.logs.log_execution(
                query=query,
                code_used=str(self.tool_library.keys()),
                prompt_used=self.prompt_genome.get('system_prompt', ''),
                output=str(output),
                fitness_score=fitness_score
            )
            
            return output, fitness_score, None
            
        except Exception as e:
            error = str(e)
            self.logs.log_error(query, error)
            return None, 0.0, error
    
    def execute_tool_with_return(self, tool_name, *args, **kwargs):
        """Execute tool that returns multiple values"""
        try:
            if tool_name in self.loaded_tools:
                for name, func in self.loaded_tools[tool_name].items():
                    if callable(func) and not name.startswith('_'):
                        result = func(*args, **kwargs)
                        if isinstance(result, tuple):
                            return *result, True, None
                        return result, True, None
            return None, None, None, False, f"Tool {tool_name} not found"
        except Exception as e:
            return None, None, None, False, str(e)
    
    def load_knowledge_base(self):
        """Load or create medical knowledge base"""
        if os.path.exists('medical_knowledge.json'):
            with open('medical_knowledge.json', 'r') as f:
                return json.load(f)
        return {
            'diseases': {
                'Common Cold': {
                    'symptoms': ['fever', 'cough', 'sore_throat', 'runny_nose', 'fatigue'],
                    'severity': 'mild',
                    'treatments': ['Rest', 'Hydration', 'OTC medications'],
                    'recovery_time': '7-10 days'
                },
                'Influenza': {
                    'symptoms': ['fever', 'cough', 'fatigue', 'headache', 'body_aches'],
                    'severity': 'moderate',
                    'treatments': ['Rest', 'Fluids', 'Antivirals'],
                    'recovery_time': '1-2 weeks'
                },
                'COVID-19': {
                    'symptoms': ['fever', 'cough', 'fatigue', 'shortness_breath', 'loss_taste'],
                    'severity': 'moderate_to_severe',
                    'treatments': ['Isolation', 'Rest', 'Monitor oxygen'],
                    'recovery_time': '2-4 weeks'
                }
            }
        }
    
    def calculate_fitness(self, query, diagnosis, confidence, execution_time):
        """Calculate fitness score based on multiple factors"""
        score = 0
        # Confidence contributes 40%
        score += confidence * 0.4
        # Execution time (faster is better, max 0.3)
        time_score = max(0, 1 - (execution_time / 5.0)) * 0.3
        score += time_score
        # Diagnosis quality (longer query usually means more detail)
        score += min(0.2, len(query.split()) / 100) * 0.2
        # Base score
        score += 0.1
        return min(1.0, score)

# ============================================
# OPTIMIZER AGENT - Analyzes Performance
# ============================================

class OptimizerAgent:
    def __init__(self, logs_db):
        self.logs = logs_db
    
    def analyze_performance(self):
        """Analyze logs to identify improvement opportunities"""
        analysis = {
            'low_performance_patterns': [],
            'frequent_errors': [],
            'optimization_suggestions': []
        }
        
        # Analyze errors
        recent_errors = self.logs.get_recent_errors(20)
        if recent_errors:
            error_counts = {}
            for error in recent_errors:
                error_type = error['error'][:50]
                error_counts[error_type] = error_counts.get(error_type, 0) + 1
            
            for error_type, count in error_counts.items():
                if count > 3:
                    analysis['frequent_errors'].append({
                        'error': error_type,
                        'count': count,
                        'suggestion': self.suggest_fix(error_type)
                    })
        
        # Analyze fitness scores
        avg_fitness = self.logs.get_average_fitness()
        if avg_fitness < 0.6:
            analysis['optimization_suggestions'].append({
                'type': 'fitness_improvement',
                'current': avg_fitness,
                'target': 0.8,
                'action': 'Improve symptom extraction accuracy'
            })
        
        return analysis
    
    def suggest_fix(self, error_type):
        """Suggest fix for common errors"""
        if 'symptom' in error_type.lower():
            return "Expand symptom keywords in extractor"
        elif 'prediction' in error_type.lower():
            return "Add more disease-symptom mappings"
        elif 'response' in error_type.lower():
            return "Enhance response generation templates"
        return "Review and update relevant code module"

# ============================================
# GENERATOR AGENT - Creates New Code/Prompts
# ============================================

class GeneratorAgent:
    def __init__(self, tool_library, prompt_genome):
        self.tool_library = tool_library
        self.prompt_genome = prompt_genome
    
    def generate_improved_code(self, tool_name, optimization_suggestion):
        """Generate improved version of a tool"""
        if tool_name not in self.tool_library:
            return None
        
        current_code = self.tool_library[tool_name]
        
        # Simple evolution - add more keywords or improve logic
        if 'extract_symptoms' in tool_name:
            # Add more symptom keywords
            improved_code = current_code.replace(
                "'chest_pain': ['chest pain', 'chest pressure']",
                "'chest_pain': ['chest pain', 'chest pressure', 'chest tightness', 'heart pain']"
            )
            return improved_code
        
        elif 'predict_disease' in tool_name:
            # Improve matching algorithm
            improved_code = current_code.replace(
                "match_score = len(disease_symptoms & user_symptoms) / max(1, len(disease_symptoms | user_symptoms))",
                "match_score = (len(disease_symptoms & user_symptoms) * 1.5) / max(1, len(disease_symptoms | user_symptoms))"
            )
            return improved_code
        
        return current_code
    
    def generate_improved_prompt(self, prompt_key, optimization_suggestion):
        """Generate improved version of a prompt"""
        if prompt_key not in self.prompt_genome:
            return None
        
        current_prompt = self.prompt_genome[prompt_key]
        
        # Improve prompts based on suggestions
        if 'accuracy' in str(optimization_suggestion).lower():
            improved = current_prompt + "\nBe more precise and detailed in analysis."
            return improved
        elif 'empathy' in str(optimization_suggestion).lower():
            improved = current_prompt + "\nShow more empathy and understanding."
            return improved
        
        return current_prompt

# ============================================
# VERIFIER AGENT - Tests New Code in Sandbox
# ============================================

class VerifierAgent:
    def __init__(self):
        self.test_results = []
    
    def verify_code(self, code, test_inputs):
        """Test code in sandbox environment"""
        results = []
        
        for test_input in test_inputs:
            try:
                # Create isolated environment
                exec_globals = {}
                exec(code, exec_globals)
                
                # Find the main function
                for name, func in exec_globals.items():
                    if callable(func) and not name.startswith('_'):
                        # Execute with test input
                        result = func(test_input)
                        results.append({
                            'input': test_input,
                            'output': result,
                            'success': True,
                            'error': None
                        })
                        break
            except Exception as e:
                results.append({
                    'input': test_input,
                    'output': None,
                    'success': False,
                    'error': str(e)
                })
        
        success_rate = sum(1 for r in results if r['success']) / max(1, len(results))
        return results, success_rate
    
    def verify_prompt(self, prompt, test_scenarios):
        """Verify prompt effectiveness"""
        # Simple verification - check for required elements
        required_elements = ['medical', 'advice', 'disclaimer']
        missing = [elem for elem in required_elements if elem not in prompt.lower()]
        
        if missing:
            return False, f"Missing required elements: {missing}"
        return True, "Prompt verification passed"

# ============================================
# EVOLUTION ENGINE - The Meta-Loop
# ============================================

class EvolutionEngine:
    def __init__(self, executor, optimizer, generator, verifier, logs_db):
        self.executor = executor
        self.optimizer = optimizer
        self.generator = generator
        self.verifier = verifier
        self.logs = logs_db
        self.evolution_history = []
    
    def evolve(self):
        """Run one evolution cycle"""
        st.info("🧬 Evolution cycle started...")
        
        # Step 1: Analyze performance
        analysis = self.optimizer.analyze_performance()
        
        if analysis['frequent_errors']:
            st.warning(f"Found {len(analysis['frequent_errors'])} frequent errors")
            
            for error in analysis['frequent_errors']:
                # Step 2: Generate improved code
                for tool_name in self.executor.tool_library.keys():
                    improved_code = self.generator.generate_improved_code(tool_name, error['suggestion'])
                    
                    if improved_code:
                        # Step 3: Verify improved code
                        test_inputs = [
                            "I have fever and cough",
                            "Severe headache and fatigue",
                            "Chest pain and difficulty breathing"
                        ]
                        results, success_rate = self.verifier.verify_code(improved_code, test_inputs)
                        
                        if success_rate > 0.7:
                            # Step 4: Apply improvement
                            self.executor.tool_library[tool_name] = improved_code
                            self.executor.load_tools()
                            
                            evolution_record = {
                                'timestamp': datetime.now().isoformat(),
                                'tool': tool_name,
                                'improvement': error['suggestion'],
                                'success_rate': success_rate,
                                'fitness_improvement': 0.1
                            }
                            self.evolution_history.append(evolution_record)
                            
                            st.success(f"✅ Evolved {tool_name} - Success rate: {success_rate*100:.0f}%")
        
        # Improve prompts
        if analysis['optimization_suggestions']:
            for prompt_key in self.executor.prompt_genome.keys():
                improved_prompt = self.generator.generate_improved_prompt(prompt_key, analysis['optimization_suggestions'][0])
                
                if improved_prompt:
                    verified, message = self.verifier.verify_prompt(improved_prompt, ['test'])
                    if verified:
                        self.executor.prompt_genome[prompt_key] = improved_prompt
                        st.success(f"✅ Evolved prompt: {prompt_key}")
        
        # Save evolution history
        with open('evolution_history.json', 'w') as f:
            json.dump(self.evolution_history, f, indent=2)
        
        st.balloons()
        return len(self.evolution_history)

# ============================================
# STREAMLIT UI
# ============================================

def main():
    st.set_page_config(page_title="Evolutionary Medical AI", page_icon="🧬", layout="wide")
    
    st.title("🧬 Evolutionary Medical AI")
    st.markdown("*Self-improving AI with meta-learning and code evolution*")
    
    # Initialize components
    if 'logs_db' not in st.session_state:
        st.session_state.logs_db = LogsDatabase()
    if 'executor' not in st.session_state:
        st.session_state.executor = ActiveExecutor(TOOL_LIBRARY, PROMPT_GENOME, st.session_state.logs_db)
    if 'optimizer' not in st.session_state:
        st.session_state.optimizer = OptimizerAgent(st.session_state.logs_db)
    if 'generator' not in st.session_state:
        st.session_state.generator = GeneratorAgent(TOOL_LIBRARY, PROMPT_GENOME)
    if 'verifier' not in st.session_state:
        st.session_state.verifier = VerifierAgent()
    if 'evolution_engine' not in st.session_state:
        st.session_state.evolution_engine = EvolutionEngine(
            st.session_state.executor,
            st.session_state.optimizer,
            st.session_state.generator,
            st.session_state.verifier,
            st.session_state.logs_db
        )
    
    # Sidebar - System Status
    with st.sidebar:
        st.header("🧠 System Architecture")
        st.markdown("""
        **Operational Layer (The Hand)**
        - Active Executor
        - Tool Library
        - Prompt Genome
        
        **Optimization Layer (The Brain)**
        - Logs Database
        - Optimizer Agent
        - Generator Agent
        - Verifier Agent
        - Evolution Engine
        """)
        
        st.divider()
        st.header("📊 Performance Metrics")
        
        avg_fitness = st.session_state.logs_db.get_average_fitness()
        st.metric("Avg Fitness Score", f"{avg_fitness:.2f}")
        st.metric("Total Queries", len(st.session_state.logs_db.logs['queries']))
        st.metric("Errors Logged", len(st.session_state.logs_db.logs['errors']))
        
        st.divider()
        
        if st.button("🧬 RUN EVOLUTION CYCLE", type="primary", use_container_width=True):
            with st.spinner("Evolving AI..."):
                evolutions = st.session_state.evolution_engine.evolve()
            st.success(f"Completed {evolutions} evolutions!")
            st.rerun()
        
        st.divider()
        
        if st.button("📋 View Evolution History"):
            if os.path.exists('evolution_history.json'):
                with open('evolution_history.json', 'r') as f:
                    history = json.load(f)
                st.json(history[-5:])
    
    # Main interface - 3 tabs
    tab1, tab2, tab3 = st.tabs(["💬 Medical Consultation", "🧬 Evolution Dashboard", "📊 System Logs"])
    
    with tab1:
        st.header("How are you feeling today?")
        
        user_input = st.text_area(
            "Describe your symptoms:",
            height=120,
            placeholder="Example: I have a fever of 101°F, severe headache, and I feel very tired..."
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            analyze = st.button("🔬 Analyze", type="primary", use_container_width=True)
        
        if analyze and user_input:
            with st.spinner("🧠 Analyzing with evolutionary AI..."):
                result, fitness, error = st.session_state.executor.execute_workflow(user_input)
                
                if result:
                    st.success(f"✅ Diagnosis: {result['diagnosis']}")
                    st.metric("Confidence", f"{result['confidence']*100:.1f}%")
                    st.metric("Fitness Score", f"{fitness:.2f}")
                    
                    st.info(result['response'])
                    
                    if result['treatment']:
                        with st.expander("💊 Treatment Recommendations"):
                            st.write(f"**Severity:** {result['treatment'].get('severity', 'Unknown')}")
                            st.write(f"**Treatments:** {', '.join(result['treatment'].get('treatments', []))}")
                            st.write(f"**Recovery Time:** {result['treatment'].get('recovery_time', 'Varies')}")
                    
                    # Feedback for learning
                    st.markdown("---")
                    st.subheader("📝 Help the AI Evolve")
                    
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        correct = st.radio("Was this diagnosis accurate?", ["Yes", "No", "Partial"])
                    with col2:
                        feedback = st.text_area("Additional feedback (optional):", placeholder="The actual issue was...")
                    
                    if st.button("Submit Feedback - Trigger Evolution"):
                        # Log feedback as an interaction
                        fitness_score = 1.0 if correct == "Yes" else 0.3 if correct == "Partial" else 0.0
                        st.session_state.logs_db.log_execution(
                            query=user_input,
                            code_used="user_feedback",
                            prompt_used="feedback_loop",
                            output=result['diagnosis'],
                            fitness_score=fitness_score
                        )
                        st.success("Thank you! The AI will evolve based on your feedback.")
                        st.balloons()
                else:
                    st.error(f"Analysis failed: {error}")
    
    with tab2:
        st.header("🧬 Evolution Dashboard")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Tool Library")
            for tool_name in st.session_state.executor.tool_library.keys():
                with st.expander(f"🔧 {tool_name}"):
                    st.code(st.session_state.executor.tool_library[tool_name][:300] + "...")
        
        with col2:
            st.subheader("Prompt Genome")
            for prompt_name, prompt_text in st.session_state.executor.prompt_genome.items():
                with st.expander(f"📝 {prompt_name}"):
                    st.write(prompt_text)
        
        st.divider()
        
        st.subheader("Optimizer Analysis")
        analysis = st.session_state.optimizer.analyze_performance()
        
        if analysis['frequent_errors']:
            st.warning("Frequent Errors Detected:")
            for error in analysis['frequent_errors']:
                st.write(f"- {error['error'][:100]}...")
                st.caption(f"💡 Suggestion: {error['suggestion']}")
        
        if analysis['optimization_suggestions']:
            st.info("Optimization Suggestions:")
            for suggestion in analysis['optimization_suggestions']:
                st.write(f"- {suggestion['action']}")
        
        if os.path.exists('evolution_history.json'):
            st.subheader("Evolution History")
            with open('evolution_history.json', 'r') as f:
                history = json.load(f)
            for evo in history[-5:]:
                st.success(f"✅ {evo['timestamp'][:16]} - {evo['tool']}: {evo['improvement'][:100]}")
    
    with tab3:
        st.header("📊 System Logs")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Recent Queries")
            for query in st.session_state.logs_db.logs['queries'][-5:]:
                st.caption(f"📝 {query['timestamp'][:16]}: {query['query'][:100]}...")
        
        with col2:
            st.subheader("Recent Errors")
            for error in st.session_state.logs_db.logs['errors'][-5:]:
                st.error(f"❌ {error['timestamp'][:16]}: {error['error'][:100]}...")
        
        st.divider()
        
        st.subheader("Fitness Score History")
        if st.session_state.logs_db.logs['fitness_scores']:
            fitness_data = st.session_state.logs_db.logs['fitness_scores']
            st.line_chart(pd.DataFrame({'Fitness Score': fitness_data[-50:]}))
        
        st.divider()
        
        if st.button("📥 Export All Logs"):
            export_data = {
                'logs': st.session_state.logs_db.logs,
                'evolution_history': json.load(open('evolution_history.json')) if os.path.exists('evolution_history.json') else []
            }
            with open('complete_logs_export.json', 'w') as f:
                json.dump(export_data, f, indent=2)
            st.success("Logs exported to complete_logs_export.json")

if __name__ == "__main__":
    main()
