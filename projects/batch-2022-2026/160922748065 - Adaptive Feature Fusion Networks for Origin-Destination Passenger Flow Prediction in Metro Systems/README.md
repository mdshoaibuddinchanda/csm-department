🚇 Metro Passenger Flow Prediction System  
Adaptive Feature Fusion Network (AFFN) for OD Flow Prediction  

---

👥 Team  
Name | Roll Number  
--- | ---  
Abdul Rahman Anas | 160922748065  
Md Zuber Ali | 160922748094  
Ahmed Waliuddin Quadri | 160922748069  
Amaan Ahmed | 160922748071  

Project Guide: Ms. Sadia Kausar  
Institution: Lords Institute of Engineering and Technology  

---

📌 About  

This project focuses on predicting **Origin-Destination (OD) passenger flow** in metro systems using advanced deep learning techniques.  

The system leverages an **Adaptive Feature Fusion Network (AFFN)** to capture complex spatial and temporal dependencies in metro transportation data.  

It helps improve:  
- Metro scheduling  
- Passenger flow management  
- Urban transportation planning  

---

🎯 Objective  

- Accurately predict OD passenger flow  
- Capture spatial and temporal dependencies  
- Handle sparse and incomplete OD matrices  
- Improve prediction accuracy using deep learning  

---

📊 Key Challenges  

- High temporal dynamics  
- Complex spatial correlations  
- Influence of external factors (weather, holidays)  
- Sparse and incomplete OD matrices  

---

🧠 Proposed System  

The system uses **AFFN (Adaptive Feature Fusion Network)**:  

- Combines spatial + temporal features  
- Uses **EMGC-GRU (Enhanced Multi-Graph Convolution GRU)**  
- Integrates external factors using attention mechanism  
- Multi-task learning with IO (Inflow/Outflow) prediction  

---

⚙️ Models Used  

- Existing Model: MLP (Multi-Layer Perceptron)  
- Proposed Model: AFFN (EMGC-GRU)  
- Extended Model: AFFN (EMGC-LSTM)  

---

📈 Features  

- Multi-graph spatial learning  
- Temporal sequence modeling  
- Attention-based feature fusion  
- Performance comparison (RMSE & MAP)  
- Visualization graphs  

---

📊 Workflow  

1. Upload Dataset  
2. Preprocess Dataset  
3. Train MLP Model  
4. Train AFFN (GRU) Model  
5. Train AFFN (LSTM) Model  
6. Compare Results  
7. Visualize Graphs  

---

🧩 Modules  

- User Login  
- Dataset Upload & Processing  
- MLP Prediction  
- AFFN (GRU) Prediction  
- AFFN (LSTM) Prediction  
- Graph Visualization  

---

📉 Evaluation Metrics  

- RMSE (Root Mean Square Error)  
- MAP (Mean Absolute Percentage Error)  

---

🛠️ Tech Stack  

Layer | Technology  
--- | ---  
Programming | Python  
Framework | Django  
ML Libraries | Scikit-learn, Keras, TensorFlow  
Data Processing | Pandas, NumPy  
Visualization | Matplotlib  
Database | MySQL  
GUI | Web Interface  

---

💻 System Requirements  

### Hardware  
- Processor: Pentium IV  
- RAM: 4GB (minimum)  
- Hard Disk: 20GB  

### Software  
- OS: Windows  
- Language: Python  
- Frontend: HTML, CSS, JavaScript  
- Backend: Django ORM  
- Database: MySQL  

---

🚀 Setup & Run  

### 1. Clone Repository  
```bash
git clone https://github.com/your-username/metro-flow-prediction.git
cd metro-flow-prediction

pip install -r requirements.txt

python manage.py runserver