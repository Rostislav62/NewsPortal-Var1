# News Portal: Dynamic News Platform

## Overview

### Problem
Online news platforms often lack efficient user engagement features, such as real-time notifications, subscription-based updates, and robust content management, leading to disconnected user experiences.

### Solution
**News Portal** is a Django-based web application that provides a dynamic platform for managing and displaying news articles, with user subscriptions, automated email notifications, and weekly digests powered by Celery and Redis.

### Impact
Enhances user engagement through timely updates, simplifies content management for authors, and streamlines administration, fostering a vibrant news community.

## About the Project
News Portal is a feature-rich news platform built with Django, designed to manage articles, user subscriptions, and automated notifications. Users can register, subscribe to categories, receive real-time and weekly article updates, and manage profiles. The platform includes advanced logging, caching, and asynchronous task processing with Celery and Redis. This project showcases my expertise in full-stack web development, asynchronous task management, and performance optimization.

## Features
- **User Registration and Authentication**: Email-based registration, Yandex OAuth, and password recovery.
- **Article Management**: Create, edit, and delete articles (news or posts) with rich text support, restricted to authors.
- **Category Subscriptions**: Users can subscribe to categories for real-time email notifications on new articles.
- **Weekly Digests**: Automated weekly email digests for subscribed categories (every Monday at 8:00 AM).
- **Welcome Emails**: Sent upon registration with activation links.
- **User Groups and Permissions**:
  - Basic: Read-only access.
  - Premium: Up to 5 posts/day.
  - Authors: Create/edit/delete articles.
- **Caching**: Low-level article caching, page-level caching, and template fragment caching.
- **Logging**: Custom logging for debugging, errors, security, and email alerts.
- **Admin Tools**: Custom admin panel with filters, custom commands, and data export/import.
- **Search**: Filter articles by title, content, rating, author, category, type, and date.
- **Security**: Protection against SQL injection, XSS, and CSRF attacks.

---

# Run Locally

> **Python version**: Known-good on Python **3.10**  
> Django version in requirements: **4.2.x**

## 1) Create a Virtual Environment

### Linux/macOS
```bash
cd /path/to/NewsPortal
python3.10 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Windows (PowerShell)
```powershell
cd C:\path\to\NewsPortal
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

> If PowerShell blocks script execution:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> ```

### Notes
- If `pip` fails to build **backports.zoneinfo** on Python ≥ 3.9, open `requirements.txt` and ensure this marker is present:
  ```text
  backports.zoneinfo==0.2.1; python_version < "3.9"
  ```

## 2) Create `.env`

Create a `.env` file in the project root (alongside `manage.py`). Minimal config for development:

```ini
# Security & debug
SECRET_KEY=replace-with-a-strong-secret
DEBUG=True

# Hosts & time
ALLOWED_HOSTS=localhost,127.0.0.1
TIME_ZONE=Europe/Dublin

# Email in console for local dev
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

Generate a random secret quickly:
```bash
python - << 'PY'
import secrets; print(secrets.token_urlsafe(50))
PY
```

## 3) Database

From the activated venv:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

## 4) Run Redis (for Celery features)
### Linux
```bash
sudo apt install -y redis-server
sudo systemctl enable --now redis-server
```
### Docker
```bash
docker run --name redis -p 6379:6379 -d redis:7
```

## 5) Run Celery
In separate terminals (with venv activated):
```bash
celery -A NewsPortal worker --loglevel=info
celery -A NewsPortal beat --loglevel=info
```

## 6) Run the Application
```bash
python manage.py runserver 0.0.0.0:8000
```
Open **http://127.0.0.1:8000** in your browser.

---

## Example User Flow
- Register with `user@example.com`, verify via activation link (printed to console in dev).
- Subscribe to "Technology" category.
- Create a news article: "AI Breakthroughs in 2025" (if Author).
- Receive an email notification (in console) for new articles in subscribed categories.
- Receive weekly digest on Monday at 8:00 AM.

## Project Structure (simplified)
- `manage.py` — Django entry point.
- `NewsPortal/` — settings, URLs, Celery config.
- `news/` — models, views, tasks, templates, custom commands.
- `accounts/` — user profiles, auth, templates.
- `static/` — front-end assets.
- `media/` — uploaded content.

## License
MIT License

---

**Author:** Rostislav — full‑stack developer (Django, Celery, async systems).
