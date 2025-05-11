# Technical Specification - News Portal

## 1. Project Overview

### 1.1 Purpose
News Portal is a Django-based web application designed as a dynamic news platform for publishing articles, managing user subscriptions, and delivering automated email notifications. It supports real-time article notifications, weekly digests, and robust content management, showcasing expertise in full-stack development, asynchronous task processing, and performance optimization.

### 1.2 Objectives
- Develop a news portal with article creation, editing, and search capabilities.
- Implement user registration with email verification and Yandex OAuth.
- Enable category subscriptions with real-time and weekly email notifications.
- Integrate Celery and Redis for asynchronous notifications and digests.
- Optimize performance with caching and logging for debugging and monitoring.
- Ensure security and user group-based permissions.

### 1.3 Target Audience
- News readers seeking personalized content updates.
- Content creators and administrators managing news articles.
- Recruiters evaluating Django, Celery, and full-stack development skills.

## 2. Functional Requirements
### 2.1 User Registration and Authentication
- Registration:
  - Email-based with welcome email and activation link (via EmailContentBuilder).
  - Yandex OAuth support using django-allauth.
  - Automatic assignment to Basic group; optional Premium/Author selection.
- Authentication:
  - Login via email/password or Yandex.
  - Password recovery via email.
- Profile:
  - Model Profile for user details (first name, last name, etc.).
  - Edit profile, change password, or upgrade to Premium/Author.
- URLs:
/accounts/login/, /accounts/register/, /accounts/profile/, /accounts/password/reset/.

### 2.2 Article Management
- Creation/Editing:
  - Articles (news or posts) via Article model (fields: title, content, category, author_profile, publication_date, article_type). 
  - Rich text support (assumed django-tinymce).
  - Restricted to Authors; Basic users limited to 3 posts/day, Premium to 5 posts/day.
  - Notifications on post limits via email (EmailContentBuilder.generate_limit_email).
- Listing and Search:
  - List view with pagination and filtering by title, content, rating, author, category, type, or date.
  - Detail view with full content.
- URLs:
  - /news/ (list), /news/<id>/ (detail), /news/create/, /news/<id>/edit/, /news/<id>/delete/, /news/search/.

### 2.3 Category Subscriptions
- Subscription:
  - Users subscribe to categories via Category.subscribers (ManyToMany with User).
  - Real-time email notifications for new articles (EmailContentBuilder.generate_notification_email).
- Weekly Digests:
  - Scheduled via Celery Beat (Monday, 8:00 AM) using news.tasks.send_weekly_digest.
  - Emails include article titles, summaries, and links (EmailContentBuilder.generate_weekly_digest_email).

### 2.4 Notifications
- Welcome Email: Sent on registration with activation link.
- Article Notifications: Sent to category subscribers with article title, author, summary, and link.
- Post Limit Notifications: Sent when Basic (3 posts/day) or Premium (5 posts/day) limits are reached.
- Email Variants: Console (for testing, USE_CONSOLE_EMAIL_BACKEND=True) or SMTP (production).
- Celery: Asynchronous delivery via news.tasks.send_new_article_notification.

### 2.5 Admin Tools
- Admin Panel:
  - Custom admin classes for Profile, Article, Category, Rating with filters and custom displays (e.g., author_name, article_type_display).
- Custom Commands:
  - delete_category_news.py: Deletes news by category with console confirmation. 
  - Data export/import: export_all_to_json.py, export_all_to_xml.py, export_articles_and_categories_to_json.py, clear_database.py, import_from_json.py.

### 2.6 Caching
- Low-Level: Articles cached using cache.get/set with keys from utils.get_article_cache_key (cleared on edit/delete).
- Page-Level:
  - Article list: 5 minutes (cache_page, Redis).
  - Homepage: 1 minute (cache_page, Memcached).
- Template Fragments:
  - Menu and footer: 1 hour ({% cache %}).

### 2.7 Logging
- Console (DEBUG=True):
  - DEBUG+: Time, level, message.
  - WARNING+: Adds pathname.
  - ERROR/CRITICAL: Adds exc_info.
- general.log (DEBUG=False):
  - INFO+: Time, level, module, message.
- errors.log:
  - ERROR/CRITICAL from django.request, django.server, django.template, django.db.backends: Time, level, message, pathname, exc_info.
- security.log:
  - All levels from django.security: Time, level, module, message.
- Email (DEBUG=False):
  - ERROR/CRITICAL from django.request, django.server: Time, level, message, pathname (no exc_info).

## 3. Non-Functional Requirements
### 3.1 Performance
- Response time: <2 seconds for page loads (optimized via Silk, Django Debug Toolbar, caching).
- Support up to 1000 concurrent users with SQLite (scalable to PostgreSQL).

### 3.2 Scalability
- Modular app structure (news, accounts) for extensibility.
- Celery and Redis for asynchronous tasks.
- Django ORM optimized for query performance.

### 3.3 Security
- Protection against SQL injection, XSS, and CSRF (Django built-in).
- API keys in .env (excluded via .gitignore).
- Logging of security events (django.security).

### 3.4 Reliability
- Email delivery for notifications and digests.
- Error handling for invalid inputs and failed tasks.

## 4. Technical Architecture
### 4.1 Technologies
- Python 3.8: Core language.
- Django 3.2: Web framework.
- Celery: Asynchronous task processing.
- Redis: Message broker and caching.
- django-tinymce: WYSIWYG editor (assumed).
- django-allauth: Authentication and Yandex OAuth.
- Silk: Performance analysis.
- Django Debug Toolbar: Query debugging.
- Bootstrap: Responsive front-end.
- Git: Version control.

### 4.2 Project Structure
- manage.py: Django project entry point.
- NewsPortal/:
  - settings.py: Configuration (SMTP, Celery, Redis, caching, logging).
  - urls.py: URL routing.
  - celery.py: Celery configuration.
- news/:
  - models.py: Article, Category, Rating.
  - views.py: Article, search, and notification views.
  - tasks.py: Celery tasks (send_new_article_notification, send_weekly_digest).
  - templates/news/: Templates for articles, search, forms.
  - management/commands/: Custom commands (delete_category_news.py, etc.).
- accounts/:
  - models.py: Profile. 
  - views.py: Registration, authentication, profile views.
  - templates/accounts/: Templates for login, registration, profile.
- utils.py: Cache key generation and helper functions.

## 4.3 Database Setup
- Models:
  - news/models.py: Article (title, content, category, author_profile, publication_date, article_type), Category (name, subscribers), Rating.
  - accounts/models.py: Profile (user details).

### Setup:
1. Create virtual environment:
    ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/macOS

2. Install dependencies:
    ```bash
   pip install -r requirements.txt

3. Apply migrations:
    ```bash
   python manage.py makemigrations
   python manage.py migrate

4. Create superuser:
   ```bash
   python manage.py createsuperuser

### 4.4 Email and Notifications
- SMTP: Configured via .env (e.g., EMAIL_HOST, EMAIL_HOST_USER).
- EmailContentBuilder: Generates emails for welcome, subscriptions, notifications, digests, and post limits.
- Celery Tasks: Asynchronous delivery with send_new_article_notification and send_weekly_digest.

## 5. Deliverables
- Source code in Rostislav62/NewsPortal repository.
- README.md with project overview, usage, and setup instructions.
- Technical_Specification.md documenting functionality and architecture.
- SQLite database schema (db.sqlite3, excluded via .gitignore).
- Custom commands and scripts for data management.

## 6. Constraints
- Post Limits: Basic (3/day), Premium (5/day).
- Email Limits: SMTP service may have daily limits (e.g., Gmail).
- Database: SQLite for development, requires PostgreSQL for production.

## 7. Assumptions
- Users have email access for registration and notifications.
- Redis and SMTP services are configured correctly.
- Yandex OAuth credentials are provided.

## 8. Success Criteria
- Users can register, subscribe, and receive notifications/digests.
- Authors can create/edit articles with permissions enforced.
- Caching and logging improve performance and debugging.
- Admin tools and custom commands function reliably.
- Code is modular, secure, and publicly available on GitHub.
- Project showcases Django, Celery, and full-stack skills.

## 9. Author
Rostislav — Full-stack developer specializing in web applications and asynchronous systems.
