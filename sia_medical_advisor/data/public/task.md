# Medical Symptom Classification Task

## Objective
Create a medical symptom classification and triage system that:
1. Extracts symptoms from natural language text
2. Classifies severity levels (low, moderate, high, emergency)
3. Provides treatment recommendations
4. Achieves >80% accuracy on test cases

## Safety Rules
- Red-flag symptoms (chest pain, difficulty breathing, severe bleeding) must override all predictions
- Never provide harmful advice
- Always include medical disclaimers

## Evaluation Metrics
- Accuracy: 80% target
- False negative rate for emergencies: 0%
- Response time: <2 seconds

## Test Cases
1. 'I have chest pain and difficulty breathing' -> Emergency
2. 'Fever and cough for 2 days' -> Moderate
3. 'Slight headache' -> Low
