import json
import os
import sqlite3
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import random

class EvolutionEngine:
    def __init__(self, db_path: str = "data/evolution.db"):
        self.db_path = db_path
        self.generation = 0
        self.best_fitness = 0.0
        self.history: List[Dict] = []
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS evolution_log (
                id INTEGER PRIMARY KEY,
                gen INTEGER,
                fitness REAL,
                timestamp TEXT,
                improvement TEXT,
                tool_name TEXT
            )
        ''')
        self.conn.commit()

    def evaluate_fitness(self, test_cases: List[Tuple[str, str]], analyze_fn) -> float:
        correct = 0
        for text, expected_severity in test_cases:
            try:
                result = analyze_fn(text)
                if result.get("triage_level", "").lower() == expected_severity:
                    correct += 1
            except Exception:
                pass
        return correct / max(1, len(test_cases))

    def log_evolution(self, gen: int, fitness: float, improvement: str, tool_name: str = "system"):
        self.conn.execute(
            "INSERT INTO evolution_log (gen, fitness, timestamp, improvement, tool_name) VALUES (?, ?, ?, ?, ?)",
            (gen, fitness, datetime.now().isoformat(), improvement, tool_name)
        )
        self.conn.commit()
        self.history.append({
            "gen": gen,
            "fitness": fitness,
            "timestamp": datetime.now().isoformat(),
            "improvement": improvement,
            "tool_name": tool_name
        })

    def get_history(self) -> List[Dict]:
        cursor = self.conn.execute("SELECT * FROM evolution_log ORDER BY id DESC LIMIT 50")
        return [
            {"gen": row[1], "fitness": row[2], "timestamp": row[3], "improvement": row[4], "tool_name": row[5]}
            for row in cursor.fetchall()
        ]

    def get_stats(self) -> Dict:
        cursor = self.conn.execute("SELECT MAX(fitness), AVG(fitness), COUNT(*) FROM evolution_log")
        row = cursor.fetchone()
        return {
            "best_fitness": row[0] or 0.0,
            "avg_fitness": row[1] or 0.0,
            "total_evolutions": row[2] or 0,
            "current_generation": self.generation
        }

    def evolve(self, symptom_keywords: Dict, test_cases: List[Tuple[str, str]], analyze_fn, generations: int = 3) -> Dict:
        base_fitness = self.evaluate_fitness(test_cases, analyze_fn)
        self.best_fitness = base_fitness

        improvements = []

        for gen in range(generations):
            self.generation += 1
            mutated_keywords = self._mutate_keywords(symptom_keywords.copy())

            def mutated_analyze(text):
                from core.triage import extract_symptoms, classify_severity
                text_lower = text.lower()
                detected = []
                for category, keywords in mutated_keywords.items():
                    for keyword in keywords:
                        if keyword in text_lower:
                            detected.append(keyword)
                severity, confidence = classify_severity(detected)
                return {"triage_level": severity}

            fitness = self.evaluate_fitness(test_cases, mutated_analyze)

            if fitness > self.best_fitness:
                improvement = f"Generation {self.generation}: Fitness improved from {self.best_fitness:.2f} to {fitness:.2f}"
                self.log_evolution(self.generation, fitness, improvement, "keyword_mutation")
                self.best_fitness = fitness
                symptom_keywords = mutated_keywords
                improvements.append({
                    "generation": self.generation,
                    "fitness": fitness,
                    "keywords_mutated": True,
                    "improvement": improvement
                })
            else:
                self.log_evolution(self.generation, fitness, f"Generation {self.generation}: No improvement (fitness={fitness:.2f})", "keyword_mutation")

        return {
            "generations_run": generations,
            "initial_fitness": base_fitness,
            "final_fitness": self.best_fitness,
            "improvements": improvements,
            "evolved_keywords": symptom_keywords
        }

    def _mutate_keywords(self, keywords: Dict) -> Dict:
        mutation_strategies = [
            self._add_synonym,
            self._modify_threshold,
            self._merge_categories
        ]
        strategy = random.choice(mutation_strategies)
        return strategy(keywords)

    def _add_synonym(self, keywords: Dict) -> Dict:
        medical_synonyms = {
            "moderate": ["malaise", "discomfort", "unease"],
            "high": ["intense", "acute", "severe"],
            "low": ["mild", "minor", "slight"]
        }
        for category in keywords:
            if category in medical_synonyms and random.random() > 0.5:
                synonym = random.choice(medical_synonyms[category])
                if synonym not in keywords[category]:
                    keywords[category].append(synonym)
        return keywords

    def _modify_threshold(self, keywords: Dict) -> Dict:
        for category in keywords:
            if random.random() > 0.7 and keywords[category]:
                idx = random.randint(0, len(keywords[category]) - 1)
                word = keywords[category][idx]
                variations = {
                    "pain": ["discomfort", "ache", "soreness"],
                    "fever": ["temperature", "pyrexia", "hyperthermia"],
                    "cough": ["coughing", "hacking"]
                }
                for root, vars_ in variations.items():
                    if root in word and random.random() > 0.5:
                        keywords[category][idx] = random.choice(vars_)
        return keywords

    def _merge_categories(self, keywords: Dict) -> Dict:
        if "high" in keywords and "moderate" in keywords:
            if random.random() > 0.8:
                shared = set(keywords["high"]) & set(keywords["moderate"])
                if shared:
                    keyword = random.choice(list(shared))
                    keywords["high"] = [k for k in keywords["high"] if k != keyword]
                    keywords["moderate"].append(keyword)
        return keywords
