# 🧠 Stroke Prediction System  
### Explainable Machine Learning for Early Stroke Detection

---

## 👥 Team

| Name | Roll Number |
|------|------------|
| Mohammad Anasuddin | 160922748106 |
| Mohammed Ayanuddin | 160922748109 |
| Md Khaleel ur Rahman | 160922748087 |

**Project Guide:** Ms. Naila Fathima  
**Institution:** Lords Institute of Engineering and Technology  

---

## 📌 About

This project is an **end-to-end stroke prediction system** built using Machine Learning techniques.  
It not only predicts whether a person is at risk of stroke but also provides **explainable insights** into the model’s decisions.

The system is designed for **early intervention**, helping healthcare professionals make informed decisions using data-driven predictions.

---

## 📊 Overview

| Component | Technique |
|----------|----------|
| Data Processing | Cleaning, Normalization |
| Imbalance Handling | SMOTE |
| Feature Selection | Chi-Square, ANOVA, Mutual Information |
| Models | ML Algorithms |
| Explainability | SHAP, LIME |
| Interface | GUI (Tkinter) |


## 🤖 Machine Learning Models

- Logistic Regression  
- Support Vector Machine (SVM)  
- K-Nearest Neighbors (KNN)  
- Random Forest  
- Naive Bayes  
- XGBoost  

---

## 🧠 Explainable AI (XAI)

The system uses **Explainable AI techniques** to interpret predictions:

### 🔍 SHAP (SHapley Additive Explanations)
- Shows feature importance  
- Explains contribution of each feature  

### 🔎 LIME (Local Interpretable Model-Agnostic Explanations)
- Explains individual predictions  
- Provides local interpretability  

---

## 📊 Dataset

**Healthcare Stroke Dataset**

### Features:
- Age  
- Gender  
- Hypertension  
- Heart Disease  
- BMI  
- Smoking Status  
- Glucose Level  

---

## 🔄 Workflow

1. Data Collection  
2. Data Preprocessing  
3. Data Visualization  
4. Feature Engineering  
5. Handling Imbalanced Data (SMOTE)  
6. Model Training  
7. Model Evaluation  
8. Explainability (SHAP & LIME)  
9. Prediction via GUI  

---

## 📈 Results

- Achieved accuracy of **~91%**  
- Compared multiple ML models  
- **Random Forest** and **XGBoost** performed best  

---

## 🛠️ Tech Stack

| Layer | Technology |
|------|-----------|
| Programming | Python |
| ML Libraries | Scikit-learn, XGBoost |
| Data Handling | Pandas, NumPy |
| Visualization | Matplotlib, Seaborn |
| Explainability | SHAP, LIME |
| GUI | Tkinter |

---

---

## 🚀 Setup & Run

### Prerequisites
- Python 3.7+
- Required libraries (see requirements.txt)

---

### 1. Clone Repository
```bash
git clone https://github.com/your-username/stroke-prediction.git
cd stroke-prediction


pip install -r requirements.txt

python main.py


