
# Eduford – Full-Stack Educational Web Platform

🔗 **Live Demo:** https://abelkadii.web.app *(replace with actual link if needed)*

---

## 📌 Overview

Eduford is a full-stack educational web platform developed as a freelance project.  
It combines multiple advanced features including user management, optimized search, e-commerce, geolocation, and AI integration.

The project focuses on building a complete system that integrates backend logic, frontend interfaces, and third-party services.

---

## 🚀 Key Features

- 🔐 User authentication and account management  
- 📚 Optimized search engine on a large dataset of books (collected via web scraping)  
- 💰 Multi-source price comparison system  
- 🛒 E-commerce module with payment integration  
- 📄 Backend-generated PDF reports  
- 🧠 Disease prediction based on user-provided symptoms  
- 🤝 Study partner recommendation system using geolocation  
- 🤖 AI-powered conversational assistant (Gemini API)  

---

## 🧠 Technical Highlights

- **Backend:** Django  
- **Frontend:** HTML, CSS, JavaScript (no framework)  
- **Database:** SQLite (development)  
- **Data collection:** Web scraping and data structuring  
- **External APIs:**
  - Checkout.com (payments)  
  - Google Maps API (geolocation)  
  - Gemini API (LLM integration)  

---

## ⚙️ Architecture

The project is organized into multiple Django apps:

- `authentication` – user management  
- `pc` – price comparison system  
- `shop` – e-commerce module  
- `predictor` – disease detection system  
- `study` – study partner recommendation  
- `ai` – conversational assistant  
- `payment` – payment integration  

---

## 📷 Screenshots

*(Add 2–3 screenshots here for better presentation)*

---

## ⚠️ Notes

- Built under client constraints and tight deadlines  
- Some areas (UI/UX, responsiveness) could be improved  
- API keys and secrets are not included in this repository  

---

## 📦 Installation (Development)

```bash
git clone https://github.com/abelkadii/eduford.git
cd eduford
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
