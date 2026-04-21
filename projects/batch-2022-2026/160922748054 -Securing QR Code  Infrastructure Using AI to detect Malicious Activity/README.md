# Securing QR Code Infrastructure Using AI
### Detection of Malicious QR Code Activity

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green?style=for-the-badge)
![Django](https://img.shields.io/badge/Django-Backend-darkgreen?style=for-the-badge&logo=django)
![Status](https://img.shields.io/badge/Status-Completed-brightgreen?style=for-the-badge)

> A computer vision-based system for detecting and analyzing QR codes to identify potential security threats.

---

## Overview

This project enhances **QR code security** by detecting QR codes from images or real-time camera input and analyzing their content to classify them as **safe or potentially malicious**.

With the increasing use of QR codes in payments, authentication, and web navigation, this system provides a basic security layer against:

- QR-based phishing attacks
- Malicious redirects
- Unsafe embedded links

---

## Key Features

- **QR Code Detection** — using OpenCV
- **QR Decoding** — extracts embedded data from detected codes
- **Malicious Pattern Detection** — rule-based classification engine
- **Real-Time Scanning** — via live camera input
- **Lightweight Execution** — efficient and fast processing

---

## System Workflow

```
Input (Image / Camera Feed)
         │
         ▼
 QR Detection (OpenCV)
         │
         ▼
     QR Decoding
         │
         ▼
 Pattern Analysis Engine
         │
    ┌────┴────┐
    ▼         ▼
  Safe ✅  Malicious ⚠️
```

---

## Technology Stack

| Category         | Technology |
|------------------|------------|
| Language         | Python     |
| Computer Vision  | OpenCV     |
| Data Processing  | NumPy      |
| Backend          | Django     |

---

## Project Structure

```
Qavi_QR_Detection/
│
├── QR_Detection/       # Core QR detection logic
├── admins/             # Admin module
├── assets/             # Static assets
├── saved_models/       # Stored models (if any)
├── users/              # User module
├── manage.py           # Django entry point
├── requirements.txt    # Dependencies
└── README.md
```

---

## Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Project

```bash
python manage.py runserver
```

---

## Dataset

The dataset used for training and validation is not included due to:

- Security restrictions (pattern similarity to sensitive keys)
- Large file size

---

## Use Cases

- Secure QR scanning systems
- QR-based phishing detection
- Mobile security applications
- Safe URL validation

---

## Limitations

- Rule-based classification (not fully ML-driven)
- Limited dataset exposure
- May not detect highly sophisticated attacks

---

## Future Enhancements

- Machine learning-based classification
- API-based threat intelligence integration
- Mobile application deployment
- Cloud-based QR validation system

---

## Team

| Name | Roll Number |
|------|-------------|
| Mohammed Abdul Qavi Quadri | 160922748042 |
| Mohammed Mubashir Ul Baqui | 160922748045 |
| Mohammed Khaja Moinuddin   | 160922748054 |

---

## Institution

**Lords Institute of Engineering and Technology**  
Department of Computer Science (CSM)

---
