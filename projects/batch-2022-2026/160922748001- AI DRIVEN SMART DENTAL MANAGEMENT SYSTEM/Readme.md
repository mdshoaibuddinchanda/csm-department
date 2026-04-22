# 🦷 AI-Driven Smart Dental Management System

### Multi-Channel Appointment Intelligence Platform using Conversational AI, Voice Agents & Computer Vision

---

## 📌 Overview

The *AI-Driven Smart Dental Management System* is an intelligent clinic automation platform designed to streamline dental appointment scheduling using *Conversational AI, Voice Assistants, and Computer Vision technologies*.

The system enables patients to schedule appointments through *three smart communication channels*:

* Website Chatbot Interface
* WhatsApp Conversational Agent
* AI Voice-Based Calling Assistant

Additionally, the platform integrates a *Dental X-Ray Image Analysis Module* for AI-assisted diagnostic support and is currently expanding with a *Decision Tree–based Patient No-Show Prediction Model* to optimize appointment attendance planning.

This project demonstrates the real-world application of *Artificial Intelligence in healthcare workflow automation and clinical decision support systems*.

---

# 🚀 Key Features

## 📅 Multi-Channel Appointment Booking System

Patients can schedule appointments using three intelligent interfaces:

### 🌐 Website Chatbot Booking

Interactive conversational chatbot allows users to:

* check slot availability
* select appointment timings
* confirm bookings instantly
* interact with automated scheduling logic

Implemented using:


channel/web.py
agent.py


---

### 💬 WhatsApp Appointment Booking Agent

Patients can book appointments directly through WhatsApp messaging.

Features:

* conversational scheduling workflow
* automated slot confirmation
* reminder automation support
* seamless remote accessibility

Implemented using:


channel/whatsapp.py
follow_up_agent.py
services/notification_service.py


---

### 📞 Voice-Based Appointment Booking Assistant

Patients can call and interact with an AI voice assistant to schedule appointments.

Features:

* speech-based slot selection
* automated confirmation workflow
* accessibility-friendly interface
* hands-free scheduling support

Implemented using:


voice_agent.py
voice_routes.py
call_log_route.py


---

# 🦷 AI Dental X-Ray Image Analysis Module (Implemented)

The system includes a *Computer Vision–based Dental X-Ray Analysis Module* designed to assist dentists in identifying abnormalities from radiographic dental images.

This module enhances diagnostic workflows by automatically analyzing uploaded X-ray images using trained deep learning models.

Capabilities include:

* cavity detection
* infection identification
* impacted tooth localization
* abnormality highlighting
* assistive diagnostic visualization

Implemented using:


xray_routes.py
services/dental_ai_service.py
best.pt


This transforms the system from a scheduling platform into a *complete AI-assisted dental healthcare solution*.

---

# 🧠 Patient No-Show Prediction Module (In Progress)

The system is currently integrating a *Decision Tree Classification Model* to predict whether a patient is likely to miss a scheduled appointment.

This predictive analytics module will help clinics:

* reduce scheduling losses
* optimize appointment planning
* prioritize reminder notifications
* improve attendance prediction accuracy
* enhance clinic resource utilization

Algorithm Used:

Decision Tree Classifier

Implementation pipeline handled through:


extractor.py
schema.py
state.py
tools.py


The module is currently under testing and integration into the appointment workflow engine.

---

# 🔔 Smart Notification & Follow-Up System

Automated reminder and follow-up system improves appointment attendance efficiency.

Implemented using:


services/notification_service.py
email_service.py
follow_up_agent.py


Supports:

* appointment confirmation alerts
* reminder automation
* follow-up scheduling assistance
* attendance optimization messaging

---

# 📅 Google Calendar Integration

The system synchronizes appointments using secure Google Calendar OAuth integration.

Implemented using:


calendar_oauth.py


Features:

* automatic calendar booking
* real-time slot synchronization
* availability tracking
* schedule conflict prevention

---

# 🔐 Doctor Authentication & Access Control System

Secure doctor login and onboarding workflow implemented through:


auth_store.py
auth_utils.py
bootstrap_doctor_auth.py
create_doctor_auth_table.py
doctor_config.py


Includes:

* role-based authentication
* secure credential handling
* onboarding interface
* protected dashboard access

---

# 📊 Doctor Dashboard Interface

Doctor interaction dashboard built using HTML, CSS, and JavaScript.

Located inside:


static/


Includes:


doc_dashboard.html
doc_login.html
doc_signup.html
doc_onboard.html
voice_dashboard.html
homepage.html
index.html
style.css
script.js


Supports:

* appointment monitoring
* doctor authentication
* onboarding workflow
* voice dashboard interface
* scheduling visualization

---

# 🗂️ Database Architecture

Structured appointment and patient data storage implemented using SQLAlchemy ORM.

Located inside:


db/database.py
db/models.py
db/repository.py
schema.py


Supports:

* appointment tracking
* patient records
* doctor configuration storage
* scheduling analytics support

---

# 🏗️ System Architecture Workflow

The platform integrates multiple intelligent pipelines:

Website Chatbot
↓
WhatsApp Agent
↓
Voice Assistant
↓
Slot Extraction Engine
↓
Scheduling Logic
↓
Database Storage
↓
Calendar Synchronization
↓
Notification Engine
↓
Prediction Pipeline Integration

---

# 📂 Repository Structure

```
APPOINTMENT-BOOKING-AGENT/
│
├── alembic/                         # Database migration management (Alembic)
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
│
├── channel/                         # Multi-channel appointment interfaces
│   ├── web.py                       # Website chatbot scheduling interface
│   └── whatsapp.py                  # WhatsApp conversational booking agent
│
├── db/                              # Database configuration and ORM models
│   ├── __init__.py
│   ├── database.py                  # Database connection setup
│   ├── models.py                    # SQLAlchemy data models
│   └── repository.py                # Data access layer
│
├── services/                        # Core service layer modules
│   ├── dental_ai_service.py         # Dental X-ray AI inference service
│   └── notification_service.py      # Reminder & alert system
│
├── static/                          # Frontend dashboard interfaces
│   ├── index.html
│   ├── homepage.html
│   ├── doc_login.html
│   ├── doc_signup.html
│   ├── doc_dashboard.html
│   ├── doc_onboard.html
│   ├── voice_dashboard.html
│   ├── style.css
│   └── script.js
│
├── agent.py                         # Core scheduling orchestration agent
├── main.py                          # Application entry point
│
├── voice_agent.py                   # Voice-call appointment booking agent
├── voice_routes.py                  # Voice API routing handlers
├── call_log_route.py                # Call interaction logging system
│
├── xray_routes.py                   # Dental X-ray prediction endpoints
├── follow_up_agent.py               # Automated patient follow-up logic
│
├── extractor.py                     # Slot extraction & NLP processing pipeline
├── schema.py                        # Request/response schema definitions
├── state.py                         # Agent workflow state management
├── tools.py                         # Utility functions for scheduling engine
├── treatments.py                    # Treatment configuration logic
│
├── email_service.py                 # Email notification module
├── calendar_oauth.py                # Google Calendar integration
│
├── auth_store.py                    # Authentication credential storage
├── auth_utils.py                    # Authentication helper utilities
├── bootstrap_doctor_auth.py         # Doctor onboarding initialization
├── create_doctor_auth_table.py      # Authentication database setup
├── doctor_config.py                 # Doctor configuration settings
│
├── best.pt                          # Trained Dental X-ray AI model
│
├── requirements.txt                 # Python dependencies
├── runtime.txt                      # Runtime configuration
└── .env                             # Environment variables (not committed)
```
---


# 🛠️ Technology Stack

| Category              | Technology                |
| --------------------- | ------------------------- |
| Programming Language  | Python                    |
| Backend Framework     | FastAPI                   |
| Frontend              | HTML, CSS, JavaScript     |
| Conversational AI     | Custom Scheduling Agent   |
| Messaging Integration | WhatsApp Agent            |
| Voice Assistant       | Voice Scheduling Agent    |
| Machine Learning      | Decision Tree Classifier  |
| Computer Vision       | Deep Learning X-ray Model |
| ORM                   | SQLAlchemy                |
| Migration Tool        | Alembic                   |
| Calendar Integration  | Google OAuth API          |

---

# ⚙️ Installation Guide

### Clone Repository


git clone https://github.com/your-repository-link


### Navigate to Project Folder


cd appointment-booking-agent


### Install Dependencies


pip install -r requirements.txt


### Run Application


python main.py


---

# 📊 Applications

Dental Clinics
Hospitals
Healthcare Automation Platforms
Telemedicine Scheduling Systems
AI Healthcare Assistant Systems

---

# 👨‍💻 Contributors

| Name                      | Roll Number  |
| ------------------------- | ------------ |
| Mir Asghar Ali Khan       | 160922748001 |
| Mustafa                   | 160922748012 |
| Muntazir Mehdi Ali        | 160922748022 |
| Syed Mohammad Abbas Kazmi | 160922748027 |

Project Guide:
Mr. Mohammad Mazheruddin,
Assistant Professor

Branch & Section:
CSM – 4A

Institution:
Lords Institute of Engineering and Technology

---

# 🔮 Future Enhancements

* full deployment of no-show prediction engine
* mobile application integration
* speech-to-text optimization for voice assistant
* deep learning multi-class dental disease detection
* cloud-based scalable appointment engine
