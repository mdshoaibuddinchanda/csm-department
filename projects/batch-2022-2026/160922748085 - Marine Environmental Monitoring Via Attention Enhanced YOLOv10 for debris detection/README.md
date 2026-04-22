# 🌊 Marine Environmental Monitoring System  
### Attention-Enhanced YOLOv10 for Underwater Debris Detection

---

## 👥 Team

| Name | Roll Number |
|------|------------|
| MD Fardeen Ismail Khan | 160922748085 |
| Mohammed Abdul Akbar Khan Noman | 160922748098 |
| Abdul Waleed | 160922748067 |
| MD Sahil Khan | 160922748093 |

**Project Guide:** Ms. Raheela Tabassum  
**Institution:** Lords Institute of Engineering and Technology  

---

## 📌 About

This project presents an **advanced marine environmental monitoring system** designed to detect underwater debris using **Attention-Enhanced YOLOv10**.

Marine pollution is a growing global concern affecting ecosystems, biodiversity, and the blue economy. This system leverages **state-of-the-art deep learning techniques** to accurately identify and classify underwater waste in real-time.

The integration of **attention mechanisms** improves detection accuracy, especially in challenging underwater conditions such as low visibility, distortion, and noise.

---

## 📊 Overview

| Component | Technique |
|----------|----------|
| Data Processing | Image Cleaning, Augmentation |
| Model | YOLOv10 (Attention-Enhanced) |
| Feature Extraction | CNN Backbone (CSPDarknet) |
| Optimization | Transfer Learning |
| Detection | Real-Time Object Detection |
| Deployment | Edge/IoT Compatible |

---

## 🤖 Model Details

- **YOLOv10n (Lightweight Version)** for fast inference  
- Integrated **Attention Mechanism** for improved feature focus  
- Optimized for **low-resource environments** (e.g., underwater drones, IoT devices)  

---

## 🧠 Key Features

- 🎯 Real-time underwater debris detection  
- ⚡ Lightweight and efficient model  
- 🌊 Robust to underwater distortions  
- 📦 Supports multiple debris categories  
- 🤖 Suitable for autonomous marine robots  

---

## 📊 Dataset

**Underwater Debris Dataset**

### Classes:
- Plastic Waste  
- Metal Objects  
- Fishing Nets  
- Glass Bottles  
- Miscellaneous Marine Debris  

---

## 🔄 Workflow

1. Data Collection (Underwater Images/Videos)  
2. Data Preprocessing & Augmentation  
3. Annotation (Bounding Boxes)  
4. Model Training (YOLOv10 + Attention)  
5. Model Evaluation (mAP, Precision, Recall)  
6. Optimization & Fine-Tuning  
7. Real-Time Detection  
8. Deployment on Edge Devices  

---

## 📈 Results

- Achieved high detection accuracy with improved **mAP score**  
- Significant improvement in detecting **small and occluded objects**  
- Attention-enhanced model outperformed baseline YOLO models  

---

## 🛠️ Tech Stack

| Layer | Technology |
|------|-----------|
| Programming | Python |
| Deep Learning | PyTorch |
| Model | YOLOv10 |
| Image Processing | OpenCV |
| Data Handling | NumPy, Pandas |
| Visualization | Matplotlib |
| Annotation Tools | LabelImg / Roboflow |

---

## 🚀 Setup & Run

### Prerequisites
- Python 3.8+
- GPU (recommended for training)

---

### 1. Clone Repository
```bash
git clone https://github.com/your-username/marine-debris-detection.git
cd marine-debris-detection