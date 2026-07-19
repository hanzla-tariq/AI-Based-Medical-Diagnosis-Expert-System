# 🩺 ShifaBot – AI Medical Diagnosis Expert System

ShifaBot is an **AI-powered Medical Diagnosis Expert System** built with **Python Flask**, **MySQL**, and the **Groq API (Llama 3.3 70B)**. It enables users to receive AI-assisted health recommendations through a symptom form or chatbot, while administrators can manage users, consultations, reports, and analytics from a dedicated dashboard.

---

## ✨ Features

### 👤 Patient Features

- 🔐 User Registration & Login
- 💬 AI-powered chatbot consultation
- 📝 Symptom-based diagnosis form
- 🤖 AI-generated medical recommendations
- 🥗 Personalized food and medication suggestions
- 📄 Download and print medical reports
- 📚 Consultation history
- 📱 Responsive healthcare-themed interface

### 👨‍💼 Admin Features

- 📊 Analytics dashboard
- 👥 User management
- 📋 Consultation management
- 📑 Medical report management
- 📈 Daily diagnosis statistics
- 🩺 Most common symptoms visualization
- 👶 Age group distribution charts
- 🔍 Search, activate/deactivate, and delete users

---

# 🛠️ Tech Stack

### Backend

- 🐍 Python
- ⚡ Flask
- 🗄️ MySQL
- 🔐 Flask-Login
- 🔒 Flask-Bcrypt
- 🌐 Flask-CORS
- 📄 xhtml2pdf

### Frontend

- HTML5
- CSS3
- Bootstrap
- JavaScript

### AI

- 🤖 Groq API
- 🧠 Llama 3.3 70B

---

# 📋 Prerequisites

Before running the project, ensure you have installed:

- 🐍 Python 3.10 or later
- 🗄️ MySQL Server 8.0 or later
- 📦 pip (Python Package Manager)

---

# 🚀 Installation

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/shifabot.git
```

```bash
cd shifabot
```

---

## 2️⃣ Create the Database

Open MySQL Terminal or phpMyAdmin and execute:

```sql
CREATE DATABASE shifabot_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

Or import the provided schema:

```bash
mysql -u root < backend/database/schema.sql
```

> **Note:**  
> This project is configured for a MySQL server **without a password**.  
> If your MySQL server requires one, update the `.env` file:

```env
DB_PASSWORD=your_password
```

---

## 3️⃣ Configure the Groq API

1. Visit:

```
https://console.groq.com/keys
```

2. Create an account.

3. Generate an API key.

4. Open:

```text
backend/.env
```

Replace:

```env
GROQ_API_KEY=your-groq-api-key-here
```

with your actual API key.

---

## 4️⃣ Install Dependencies

Navigate to the backend directory:

```bash
cd backend
```

Install the required packages:

```bash
pip install -r requirements.txt
```

---

## 5️⃣ Run the Application

Start the Flask server:

```bash
python run.py
```

The application will be available at:

```
http://localhost:5000
```

On the first run, the application automatically:

- ✅ Creates database tables
- ✅ Seeds the default administrator account

---

# 🌐 Access the Application

Open your browser and visit:

```
http://localhost:5000
```

---

# 👤 Patient Workflow

1. Click **Get Started**
2. Create an account
3. Log in
4. Choose:

- 📝 Symptom Form
- 💬 AI Chatbot

5. Receive AI-generated diagnosis suggestions
6. Download or print the medical report
7. View consultation history

---

# 👨‍💼 Admin Panel

Login using the default administrator credentials:

**Email**

```text
hanzlasial690@gmail.com
```

**Password**

```text
654321
```

Open:

```
http://localhost:5000/admin
```

### Admin Dashboard Includes

- 📊 Analytics Dashboard
- 👥 User Management
- 📋 Consultation Management
- 📄 Report Management
- 📈 Diagnosis Charts
- 🩺 Symptom Statistics
- 👶 Age Distribution

---

# 📁 Project Structure

```text
ShifaBot/
│
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── utils/
│   │   ├── config.py
│   │   ├── extensions.py
│   │   ├── seed_admin.py
│   │   └── __init__.py
│   │
│   ├── database/
│   │   └── schema.sql
│   │
│   ├── .env
│   ├── .env.example
│   ├── requirements.txt
│   └── run.py
│
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   │
│   └── templates/
│       ├── auth/
│       ├── dashboard/
│       ├── diagnosis/
│       ├── reports/
│       ├── history/
│       └── admin/
│
└── README.md
```

---

# 📦 Key Components

| Component | Description |
|------------|-------------|
| 🔐 Authentication | User registration, login, logout |
| 🤖 Groq Service | AI diagnosis using Llama 3.3 70B |
| 📝 Diagnosis | Symptom form & chatbot |
| 📄 Reports | Generate, print, and download PDF reports |
| 📚 History | Patient consultation history |
| 👥 Admin | Manage users, reports, consultations |
| 📊 Analytics | Dashboard with charts and statistics |

---

# 🛡️ Security Features

- 🔐 Password hashing with Flask-Bcrypt
- 👤 Role-based authentication
- 🚫 Admin-only routes
- 🔑 Environment variable configuration
- 🌐 Secure session management

---

# 📊 Analytics Dashboard

The administrator dashboard includes:

- 📈 Daily Diagnosis Trends
- 🩺 Most Common Symptoms
- 👶 Age Group Distribution
- 👥 User Statistics
- 📋 Consultation Statistics

---

# 🧰 Troubleshooting

| Issue | Solution |
|--------|----------|
| 🚫 Access denied for MySQL | Verify your database credentials in `.env` |
| 📦 ModuleNotFoundError | Run `pip install -r requirements.txt` |
| 🔑 GROQ_API_KEY not configured | Add your API key to `.env` |
| 🚪 Port 5000 already in use | Change the port in `run.py` |
| 📄 PDF generation issues | Ensure `xhtml2pdf` is installed |
| 👨‍💼 Admin login fails | Start the server once to seed the admin account |

---

# 🚀 Future Improvements

- 📅 Doctor appointment booking
- 🏥 Nearby hospital locator
- 💊 Medicine database integration
- 🌍 Multi-language support
- 📱 Mobile application
- 📈 AI prediction confidence scores
- 🧠 Medical image analysis
- ☁️ Cloud deployment
- 📧 Email notifications
- 🔔 Push notifications

---

# 👨‍💻 Author

**Muhammad Hanzla**

Python Developer | Flask Developer | AI Integration | REST APIs

---

⭐ If you found this project useful, consider giving it a **star** on GitHub!
