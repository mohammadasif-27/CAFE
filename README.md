# ☕ CafeHub — Cafe Management System

CafeHub is a Django-powered web application for managing a cafe's online menu and day-to-day food operations. It provides a customer-facing website alongside account and staff management features.

## ✨ Features

* Browse cafe food items and view their details and prices
* Explore the food menu
* Create and manage user accounts
* View and manage a shopping cart
* Staff dashboard for cafe operations
* Add, edit, and delete food items
* Upload food images
* Contact form for customer enquiries
* PostgreSQL database integration

## 🖥️ Tech Stack

| Area            | Technologies           |
| --------------- | ---------------------- |
| Backend         | Python, Django         |
| Frontend        | HTML, CSS, JavaScript  |
| Database        | PostgreSQL             |
| Python packages | psycopg, python-dotenv |
| Server support  | Gunicorn               |

## 📁 Project Structure

```text
CAFE/
├── accounts/
├── cafehub/
├── core/
├── menu/
├── orders/
├── staff/
├── static/
├── templates/
├── media/
├── manage.py
└── requirements.txt
```

## ⚙️ Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/mohammadasif-27/CAFE.git
cd CAFE
```

### 2. Create a virtual environment

**Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment and database

Create a `.env` file in the project root:

```env
DJANGO_SECRET_KEY=replace_with_a_private_secret_key
```

* Install and start PostgreSQL.
* Create a database named `new_cafe_db`.
* Configure your database username and password in your local Django settings.

**Important:** Never upload your `.env` file, secret key, or database passwords to GitHub.

### 5. Apply database migrations

```bash
python manage.py migrate
```

### 6. Create an admin account (optional)

```bash
python manage.py createsuperuser
```

### 7. Run the development server

```bash
python manage.py runserver
```

Open your browser:

```text
http://127.0.0.1:8000/
```

## 🔐 Notes

* This project uses PostgreSQL.
* Uploaded food images are stored in the local media directory during development.
* The Django development server is intended for local development, not production deployment.

## 👨‍💻 Developer

**Mohammad Asif**
Python Backend Developer

* GitHub: [@mohammadasif-27](https://github.com/mohammadasif-27)
* Project: [CafeHub](https://github.com/mohammadasif-27/CAFE)

---

<p align="center">
  Built with Python and Django ☕
</p>
