# ⚖️ AI Legal Claim Assistant

AI-powered Legal Intelligence Platform built using FastAPI, React, RAG, Machine Learning, and MongoDB.

Live Demo: https://ai-legal-tech-assistant.onrender.com/

GitHub Repository:  

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

## 🏠 Homepage
- Real-time legal intelligence dashboard
- Live breach statistics
- AI-powered search
- Interactive case cards

---

## 🔒 Privacy Intelligence
- Identity theft risk analysis
- Exposure scoring
- Privacy recommendations
- AI-generated safety guidance

---

## 🧠 AI Decision Engine
Machine Learning powered claim eligibility prediction using:

- Breach type
- Exposed data
- Records affected
- User impact
- Similarity score
- Jurisdiction

Outputs:
- Claim probability
- Confidence score
- AI legal insights
- Action plan recommendations

---

## ⚖️ AI Legal Assistant (RAG Chatbot)
Production-style legal assistant capable of:
- Searching legal database
- Answering breach-related questions
- Providing AI legal guidance
- Retrieving relevant legal intelligence

---

## 📄 Claim Submission Workflow
Users can:
- View breach details
- Analyze eligibility
- Collect documents
- Access claim portals
- Submit legal registry information

---

## 📊 Legal Intelligence Database
Includes:
- Data breach cases
- Settlement cases
- Enforcement actions
- AI-generated summaries
- Legal metadata

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

:contentReference[oaicite:2]{index=2}

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

## Privacy Intelligence
- AI privacy analysis
- Exposure scoring

## AI Decision Engine
- ML-powered eligibility prediction

## AI Legal Assistant
- RAG-based chatbot

## Claim Workflow
- Document collection
- Registry submission
- Claim portal integration

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
:contentReference[oaicite:3]{index=3}

LinkedIn:  
:contentReference[oaicite:4]{index=4}

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
