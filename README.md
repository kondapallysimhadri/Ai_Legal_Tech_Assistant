# ⚖️ AI Legal Claim Assistant

AI-powered Legal Intelligence Platform built using FastAPI, React, RAG, Machine Learning, and MongoDB.

Live Demo: https://ai-legal-tech-assistant.onrender.com/

GitHub Repository:  https://github.com/kondapallysimhadri

---

# 🚀 Overview

AI Legal Claim Assistant is a production-style AI platform that helps users:

- Analyze real-world data breaches
- Predict legal claim eligibility
- Search legal intelligence databases
- Receive AI-generated legal guidance
- Explore breach analytics and privacy intelligence
- Access AI-powered claim workflows

The platform combines:

- ⚡ FastAPI Backend
- ⚛️ React Frontend
- 🧠 Machine Learning Models
- 🔍 RAG (Retrieval-Augmented Generation)
- 📊 Privacy Intelligence Dashboard
- 🤖 AI Legal Assistant Chatbot
- 🗄️ MongoDB Integration
- ☁️ Render Cloud Deployment

---
# ✨ Features

# 🏗️ System Architecture

The AI Legal Claim Assistant is structured as a multi-component AI application that separates the user interface, backend API layer, AI workflows, machine learning services, retrieval logic, and data storage.

```text
                         ┌──────────────────────┐
                         │        User          │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    React Frontend    │
                         │  Vite + Tailwind CSS │
                         └──────────┬───────────┘
                                    │
                              REST API Requests
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   FastAPI Backend    │
                         │   Application Layer  │
                         └──────────┬───────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
   ┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
   │   RAG Pipeline    │ │ ML Decision Engine│ │  Claim Workflow   │
   │                   │ │                   │ │                   │
   │ Legal Retrieval   │ │ Eligibility Model │ │ Breach Analysis   │
   │ Context Selection │ │ Risk Prediction   │ │ Document Guidance │
   │ AI Assistance     │ │ Confidence Output │ │ Claim Navigation  │
   └─────────┬─────────┘ └─────────┬─────────┘ └─────────┬─────────┘
             │                     │                     │
             └─────────────────────┼─────────────────────┘
                                   │
                                   ▼
                        ┌──────────────────────┐
                        │   AI Engine Layer    │
                        │                     │
                        │ AI-assisted Insights│
                        │ Guidance Workflows  │
                        │ Response Generation │
                        └──────────┬───────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    │                             │
                    ▼                             ▼
         ┌────────────────────┐        ┌────────────────────┐
         │      MongoDB       │        │ Legal Intelligence │
         │                    │        │       Data         │
         │ Application Data   │        │                    │
         │ Legal Records      │        │ Breach Cases       │
         │ Workflow Data      │        │ Settlement Data    │
         └────────────────────┘        └────────────────────┘
```

## Architecture Flow

1. **User Interaction**  
   Users interact with the LegalTech platform through the React-based frontend.

2. **Frontend Application**  
   The frontend provides legal intelligence search, privacy analysis, eligibility prediction, AI assistance, and claim workflow interfaces.

3. **FastAPI Backend**  
   REST API endpoints receive application requests and route them to the appropriate AI, retrieval, machine learning, or workflow component.

4. **RAG Pipeline**  
   The retrieval workflow searches relevant legal intelligence and provides contextual information for AI-assisted responses.

5. **ML Decision Engine**  
   The machine learning service evaluates claim-related inputs and produces eligibility predictions, confidence information, and decision-support outputs.

6. **Claim Workflow**  
   The claim workflow connects breach information, eligibility analysis, document guidance, and claim navigation.

7. **AI Engine**  
   AI-assisted workflows combine retrieved context and application logic to generate legal information and user guidance.

8. **Data Layer**  
   MongoDB and project datasets support application data, legal intelligence records, breach information, and workflow operations.

## Architectural Design Goals

- Separation of frontend and backend responsibilities
- Modular AI and machine learning workflows
- API-driven component communication
- Independent RAG and prediction services
- Extensible legal intelligence workflows
- Cloud-deployable application architecture

> **Current Status:** This repository represents an AI LegalTech MVP and engineering portfolio product. Production legal deployment would require additional authentication, role-based access control, retrieval evaluation, security hardening, legal data validation, observability, and privacy governance.

# 🔍 Retrieval & AI Assistance Architecture

The Legal Assistant is designed around a retrieval-assisted workflow for using relevant legal intelligence as context during user interactions.

The current MVP focuses on the separation of **legal information retrieval, contextual selection, application logic, and AI-assisted response workflows**.

```text
                         User Question
                              │
                              ▼
                   ┌─────────────────────┐
                   │  React Chat UI      │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │  /chatbot API       │
                   │  FastAPI Backend    │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │ Query Processing    │
                   │                     │
                   │ User Input Handling │
                   │ Query Preparation   │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │ Legal Intelligence  │
                   │ Retrieval Layer     │
                   │                     │
                   │ Breach Information  │
                   │ Legal Records       │
                   │ Case Context        │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │ Context Selection   │
                   │                     │
                   │ Relevant Legal Data │
                   │ Breach Context      │
                   │ Workflow Context    │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │ AI Assistance Layer │
                   │                     │
                   │ Context Processing  │
                   │ Guidance Logic      │
                   │ Response Workflow   │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │ User Response       │
                   │                     │
                   │ Legal Information   │
                   │ Suggested Actions   │
                   │ Guidance            │
                   └─────────────────────┘
```

## Retrieval Workflow

### 1. User Query

The user submits a legal or data-breach-related question through the AI Legal Assistant interface.

### 2. API Processing

The frontend sends the request to the FastAPI `/chatbot` endpoint, which acts as the backend interface for the assistant workflow.

### 3. Query Processing

The application processes the incoming question and prepares it for the legal intelligence retrieval workflow.

### 4. Legal Intelligence Retrieval

The retrieval layer searches available project data and legal intelligence sources for information relevant to the user's question.

The current project focuses on legal and breach-related context such as:

- Data breach information
- Legal case records
- Settlement information
- Enforcement-related data
- Claim workflow context

### 5. Context Selection

Relevant application and legal intelligence context is selected for the response workflow.

The goal is to reduce generic responses by using information connected to the user's legal or breach-related question.

### 6. AI-Assisted Response Workflow

The AI assistance layer combines retrieved context with application logic to produce informational guidance and suggested next actions.

### 7. Response Delivery

The generated response is returned through the backend API and displayed in the React-based Legal Assistant interface.

---

## Current RAG Status

This project represents an **MVP retrieval-assisted legal AI workflow**.

The current implementation demonstrates the architectural separation between:

- User interaction
- API processing
- Legal intelligence retrieval
- Context selection
- AI assistance
- Response delivery

A production-grade RAG implementation would extend this architecture with:

- Document ingestion pipelines
- Document parsing and cleaning
- Configurable chunking strategies
- Embedding generation
- Dedicated vector database storage
- Semantic vector retrieval
- Metadata filtering
- Retrieval reranking
- Source citations
- Retrieval quality evaluation
- Hallucination and groundedness evaluation

> The current system should be treated as an AI LegalTech MVP and engineering prototype rather than a production legal advice system.

---

## Production RAG Evolution

```text
Legal Documents / Case Data
             │
             ▼
     Document Ingestion
             │
             ▼
      Parsing & Cleaning
             │
             ▼
       Text Chunking
             │
             ▼
     Embedding Generation
             │
             ▼
       Vector Database
             │
             ▼
      Semantic Retrieval
             │
             ▼
         Reranking
             │
             ▼
     Context Construction
             │
             ▼
           LLM
             │
             ▼
 Grounded Answer + Sources
```

The production roadmap is intended to evolve the current retrieval-assisted workflow into a fully evaluated, vector-based RAG architecture with source-grounded responses and retrieval-quality monitoring.

---

# 🛠️ Tech Stack

## Frontend
- React.js
- Vite
- Tailwind CSS
- Framer Motion
- Lucide React

---

## Backend
- FastAPI
- Python 3.11
- Uvicorn

---

## AI / ML
- Scikit-learn
- Pandas
- NumPy
- ML Prediction Engine
- RAG Pipeline

---

## Database
- MongoDB

---

## Deployment
- Render
- GitHub Actions Workflow
- Cloud Deployment Pipeline

---

# 📁 Project Structure

```bash
ai_legal_assistant/
│
├── frontend/                 # React Frontend
├── ml_service/               # ML prediction services
├── rag/                      # RAG chatbot pipeline
├── models/                   # ML models
├── data/                     # Legal datasets
├── scripts/                  # Utility scripts
├── logs/                     # Application logs
│
├── ai_engine.py              # AI engine logic
├── scraper.py                # Data scraping pipeline
├── db_connected.py           # MongoDB connection
├── requirements.txt          # Python dependencies
├── runtime.txt               # Runtime configuration
├── README.md                 # Project documentation
│
└── .env                      # Environment variables
```

---

# ⚙️ Installation

## 1️⃣ Clone Repository

```bash
git clone https://github.com/kondapallysimhadri/Ai_Legal_Tech_Assistant.git
```

---

## 2️⃣ Move Into Project

```bash
cd Ai_Legal_Tech_Assistant
```

---

## 3️⃣ Create Virtual Environment

```bash
python -m venv venv
```

Activate:

### Mac/Linux
```bash
source venv/bin/activate
```

### Windows
```bash
venv\Scripts\activate
```

---

## 4️⃣ Install Backend Dependencies

```bash
pip install -r requirements.txt
```

---

## 5️⃣ Install Frontend Dependencies

```bash
cd frontend
npm install
```

---

# ▶️ Running the Project

## Backend

```bash
uvicorn ai_engine:app --reload
```

Runs on:
```bash
http://localhost:8000
```

---

## Frontend

```bash
cd frontend
npm run dev
```

Runs on:
```bash
http://localhost:5173
```

---

# 🌐 API Endpoints

## Cases API
```bash
GET /cases
```

Returns legal case intelligence data.

---

## Stats API
```bash
GET /stats
```

Returns:
- total cases
- breaches
- vector statistics

---

## Predict Eligibility
```bash
POST /predict
```

Machine learning claim prediction.

---

## AI Chatbot
```bash
POST /chatbot
```

AI Legal Assistant interaction endpoint.

---

# ☁️ Deployment

This project is deployed on Render.

## Deployment Features
- Automatic GitHub deployment
- Continuous Integration
- Cloud hosting
- Public production URL

Live URL:

:https://ai-legal-tech-assistant.onrender.com/

---

# 🔄 Deployment Workflow

```bash
git add .
git commit -m "update"
git push origin main
```

Render automatically:
- Detects changes
- Builds application
- Deploys latest version

---

# 📸 Screenshots

## Homepage
- Live legal intelligence dashboard
- Real-time breach cards

- <img width="1440" height="900" alt="Screenshot 2026-05-28 at 9 43 33 PM" src="https://github.com/user-attachments/assets/277b3ea8-5883-4e2e-a63a-00a9a11978d7" />


## Privacy Intelligence
- AI privacy analysis
- Exposure scoring
- <img width="1440" height="900" alt="Screenshot 2026-05-28 at 9 44 02 PM" src="https://github.com/user-attachments/assets/435c1bf8-8810-491b-8f54-6ef654fe5d54" />
-<img width="1440" height="900" alt="Screenshot 2026-05-28 at 9 44 17 PM" src="https://github.com/user-attachments/assets/35261a96-778d-409e-9d49-d557f1dc44ed" />

## AI Decision Engine
- ML-powered eligibility prediction
- <img width="1440" height="900" alt="Screenshot 2026-05-28 at 9 44 43 PM" src="https://github.com/user-attachments/assets/631083ce-8988-420d-a86f-ecedf2205fa7" />
-<img width="1440" height="900" alt="Screenshot 2026-05-28 at 9 45 02 PM" src="https://github.com/user-attachments/assets/9bff2e25-68f4-42d9-ada8-ea7508a4fe99" />
-<img width="1440" height="900" alt="Screenshot 2026-05-28 at 9 45 23 PM" src="https://github.com/user-attachments/assets/e718794b-12a5-4821-b6f2-0a9c84e02b8d" />

## AI Legal Assistant
- RAG-based chatbot
- <img width="1440" height="900" alt="Screenshot 2026-05-28 at 9 45 39 PM" src="https://github.com/user-attachments/assets/2b22c2e0-953d-4638-b447-5443e11e184c" />

## Claim Workflow
- Document collection
- Registry submission
- Claim portal integration
- <img width="1440" height="900" alt="Screenshot 2026-05-28 at 9 46 08 PM" src="https://github.com/user-attachments/assets/e4057114-471d-494d-9e82-2b65994107da" />
-<img width="1440" height="900" alt="Screenshot 2026-05-28 at 9 46 44 PM" src="https://github.com/user-attachments/assets/4abdcf75-312d-436e-af47-121121d265f3" />
-<img width="1440" height="900" alt="Screenshot 2026-05-28 at 9 47 17 PM" src="https://github.com/user-attachments/assets/764a2f96-7635-4d69-99c6-67b57844498f" />

---

# 🔐 Environment Variables

Create `.env` file:

```env
MONGO_URI=your_mongodb_connection
OPENAI_API_KEY=your_api_key
SECRET_KEY=your_secret
```

---

# 📈 Future Improvements

- JWT Authentication
- Real LLM Integration
- Pinecone Vector DB
- PDF Upload Analysis
- Admin Dashboard
- Payment Gateway
- User Claim Tracking
- Docker Deployment
- CI/CD Pipelines
- Real-time Scraping Automation

---

# 🎯 Use Cases

- Legal Intelligence Platforms
- Privacy Risk Analysis
- Data Breach Monitoring
- AI Legal Guidance
- Claim Eligibility Prediction
- Legal Tech Research

---

# 👨‍💻 Author

## Simhadri Kondapally

Aspiring Data Scientist & AI Developer

### Connect With Me

GitHub:  
:https://github.com/kondapallysimhadri

LinkedIn:  
:https://www.linkedin.com/in/kondapally-simhadri/

---

# 📜 License

This project is licensed under the MIT License.

---

# ⭐ Support

If you like this project:

⭐ Star the repository  
🍴 Fork the project  
🚀 Share with others

---

# 🧠 AI + Legal Tech + Machine Learning

Building the future of intelligent legal assistance.
