# News Portal: Dynamic News Platform
## Overview
### Problem
Online news platforms often lack efficient user engagement features, such as real-time notifications, subscription-based updates, and robust content management, leading to disconnected user experiences.
### Solution
News Portal is a Django-based web application that provides a dynamic platform for managing and displaying news articles, with user subscriptions, automated email notifications, and weekly digests powered by Celery and Redis.
### Impact
Enhances user engagement through timely updates, simplifies content management for authors, and streamlines administration, fostering a vibrant news community.

## About the Project
News Portal is a feature-rich news platform built with Django, designed to manage articles, user subscriptions, and automated notifications. Users can register, subscribe to categories, receive real-time and weekly article updates, and manage profiles. The platform includes advanced logging, caching, and asynchronous task processing with Celery and Redis. This project showcases my expertise in full-stack web development, asynchronous task management, and performance optimization.

## Features
- User Registration and Authentication: Email-based registration, Yandex OAuth, and password recovery. 
- Article Management: Create, edit, and delete articles (news or posts) with rich text support, restricted to authors. 
- Category Subscriptions: Users can subscribe to categories for real-time email notifications on new articles. 
- Weekly Digests: Automated weekly email digests for subscribed categories (every Monday at 8:00 AM). 
- Welcome Emails: Sent upon registration with activation links. 
- User Groups and Permissions:
  - Basic: Read-only access. 
  - Premium: Up to 5 posts/day. 
  - Authors: Create/edit/delete articles.
- Caching: Low-level article caching, page-level caching (5 min for articles, 1 min for homepage), and template fragment caching (1 hour for menu/footer). 
- Logging: Custom logging for debugging, errors, security, and email alerts (ERROR/CRITICAL levels). 
- Admin Tools: Custom admin panel with filters, custom commands (e.g., delete category news), and data export/import.
- Search: Filter articles by title, content, rating, author, category, type, and date.
- Security: Protection against SQL injection, XSS, and CSRF attacks.

## How to Work with News Portal
### Access the Platform
Visit the deployed website (e.g., https://newsportal.example.com) or run locally (see Setup Instructions).

### User Workflow

1. Register:
- Go to the registration page, enter email, and choose Basic or Premium group.
- Optionally register via Yandex OAuth.
- Receive a welcome email with an activation link.


2. Subscribe to Categories:
- Log in, visit an article, and subscribe to its category.
- Receive email notifications for new articles in subscribed categories.


3. Create/Edit Articles (Authors only):
- Navigate to "News +" or "Article +", create/edit news or posts.
- Basic users: Limited to 3 posts/day; Premium: 5 posts/day.
- Receive limit exceeded notifications if applicable.


4. Search and Browse:
- Use the search page to filter articles by title, content, author, category, type, or date.
- View article details with full content.


5. Manage Profile:
- Edit profile details, change password, or upgrade to Premium/Author.


6. Weekly Digests:
- Receive weekly emails (Monday, 8:00 AM) with new articles from subscribed categories.

### Example Usage
- Register with user@example.com, verify via activation link.
- Subscribe to "Technology" category.
- Create a news article: "AI Breakthroughs in 2025" (if Author).
- Receive an email notification for a new "Technology" article.
- Check weekly digest on Monday for all new articles.

### Notes
- Basic users are limited to 3 posts/day, Premium to 5 posts/day.
- Email notifications are sent for new articles, weekly digests, and post limits.
- Caching improves performance but clears on article edits/deletes.
- Logging captures DEBUG (console), INFO (general.log), ERROR/CRITICAL (errors.log, email), and security events (security.log).

## Setup Instructions
### Create Virtual Environment

1. Clone the repository:
    ```bash
   git clone https://github.com/Rostislav62/NewsPortal.git
   cd NewsPortal

2. Create and activate a virtual environment:python -m venv venv
    ```bash
   .\venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/macOS

3. Install dependencies:
    ```bash
   pip install -r requirements.txt

### Create Database
1. Apply migrations to set up the SQLite database:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   
2. Create a superuser for admin access:
   ```bash
   python manage.py createsuperuser

### Configure Celery and Redis

1. Install Redis (e.g., for Windows, download from https://redis.io).
2. Start Redis server:
   ```bash
   redis-server
3. Run Celery Worker:   
   ```bash
   celery -A NewsPortal worker --loglevel=info

4. Run Celery Beat for scheduled tasks:
   ```bash
   celery -A NewsPortal beat --loglevel=info


### Run the Application
1. Start the development server:
   ```bash
   python manage.py runserver
2. Access the site at http://localhost:8000.

## API Keys and Services
- The platform uses external services for notifications and authentication:

SMTP Service: Configure via .env (e.g., Gmail SMTP, SendGrid). 
Example: 
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=your_email@gmail.com
   EMAIL_HOST_PASSWORD=your_password

- Yandex OAuth: Configure via .env (client ID and secret from Yandex Developer Console).
- Redis: Required for Celery (default: redis://127.0.0.1:6379/0).

## Project Structure
- manage.py: Django project entry point.
- NewsPortal/:
  - settings.py: Configuration (SMTP, Celery, Redis, caching, logging).
  - urls.py: URL routing.
  - celery.py: Celery configuration.

- news/:
  - models.py: Article, Category, Rating models.
  - views.py: Article listing, creation, editing, search, and notification views.
  - tasks.py: Celery tasks for notifications and weekly digests.
  - templates/news/: Templates for articles, search, and forms.
  - management/commands/: Custom commands (e.g., delete_category_news.py).

- accounts/:
  - models.py: Profile model.
  - views.py: Registration, authentication, and profile views.
  - templates/accounts/: Templates for login, registration, profile.

- utils.py: Helper functions (e.g., cache key generation).

## Technologies

- Python 3.8: Core language.
- Django 3.2: Web framework. 
- Celery: Asynchronous task processing.
- Redis: Message broker and caching.
- django-tinymce: WYSIWYG editor (assumed for rich text).
- django-allauth: Authentication and Yandex OAuth.
- Silk: Performance analysis.
- Django Debug Toolbar: Query debugging.
- Bootstrap: Responsive front-end.
- Git: Version control.

## Author
Rostislav — Full-stack developer specializing in web applications and asynchronous systems. This project is part of my portfolio, showcasing expertise in Django, task automation, and user engagement systems.

## License
MIT License
