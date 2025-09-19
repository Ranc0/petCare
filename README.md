# 🐾 PetCare — Pet Adoption, Breeding, Store & AI Diagnosis Platform

**PetCare** is a full-stack Django application designed for pet lovers, breeders, and veterinarians.  
It combines **pet adoption & breeding listings**, **e-commerce for pet products**, **real-time chat**, and **AI-powered disease diagnosis** for cats and dogs.

Built as a **graduation project**, it integrates:
- Django REST Framework for the API
- Django Channels + Daphne for real-time chat
- AI models for disease detection
- External API for skin photo diagnosis
- Secure media storage for images

---

## ✨ Features

### 🐶 Pet Adoption & Breeding
- Create, filter, and search adoption and breeding posts
- Structured filters (type, breed, gender, age, country) + free-text search
- Optimized queries with `select_related` for performance

### 🏪 Store & Products
- Each user can own a store with logo and product listings
- Product categories: toys, food, clothes
- Product filtering (category, price, country) and search
- Image upload & validation for stores and products

### 💬 Real-Time Chat
- Built with **Django Channels** and **Daphne**
- Persistent message storage
- Supports private conversations between users

### 🧠 AI Diagnosis
- Two integrated AI models for cat and dog disease detection
- External API integration for skin photo diagnosis
- Upload pet images and receive instant diagnostic feedback

---

## 📦 Requirements

All dependencies are listed in `requirements.txt`.

**Core stack:**
- Python 3.12+
- Django
- Django REST Framework
- Django Channels
- Daphne
- Pillow
- python-dotenv
- rest_framework_simplejwt (JWT authentication)

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository
```bash
git clone https://github.com/Ranc0/petCare.git
cd petCare
```

### 2️⃣ Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Create a `.env` file
In the project root, create `.env`:

```env
SECRET_KEY = (generate ur own secret key and paste it here )
(for otp email confirmation add these ):
EMAIL_HOST =
EMAIL_HOST_USER = 
EMAIL_HOST_PASSWORD = 
DEFAULT_FROM_EMAIL = 

(api key for the vision model)
API_KEY=
```

> ⚠️ **Never commit `.env`** — it’s in `.gitignore`.

### 5️⃣ Apply migrations
```bash
python manage.py migrate
```

### 6️⃣ Create a superuser
```bash
python manage.py createsuperuser
```

### 7️⃣ Run the development server with Daphne
```bash
daphne -p 8000 PetCare.asgi:application
```

---

## 💬 Running the Chat Server
Django Channels is already configured. Daphne serves both HTTP and WebSocket traffic.  

---

## 📡 API Highlights

### Authentication
- JWT-based authentication via `rest_framework_simplejwt`
- Obtain token: `POST /account/sign_in`
- Refresh token: `POST /api/token/refresh/`

### All other urls in the urls.py files

---

## 🛡️ Security Notes
- All secrets are stored in `.env`
- All secrets were only used for development and changed later
- Image uploads are validated before saving
- Ownership checks prevent unauthorized edits/deletes

---

## 🤝 Contributing
Pull requests are welcome!  
For major changes, please open an issue first to discuss what you’d like to change.

---

## 📄 License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
