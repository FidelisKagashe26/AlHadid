# Al-Hadid Foundation Website

A comprehensive Django-based website for Al-Hadid Foundation featuring:

## Features

- **Dynamic Content Management**: Custom admin panel for managing all website content
- **Responsive Design**: Mobile-first approach with dark/light mode toggle
- **Multiple Pages**: Home, About, Programs, News & Events, Gallery, Donate, Contact
- **SEO Optimized**: Built-in sitemap generation and meta tags
- **Interactive Features**: Google Maps integration, WhatsApp integration, social media links
- **Donation System**: Multiple donation methods with transparent information

## Installation

1. **Clone or Download** the project files to your computer

2. **Create a Virtual Environment** (recommended):
```bash
python -m venv alhadid_env
# On Windows:
alhadid_env\Scripts\activate
# On macOS/Linux:
source alhadid_env/bin/activate
```

3. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

4. **Environment Setup**:
```bash
# Copy .env.example to .env
cp .env.example .env
# Edit .env with your settings (optional for development)
```

5. **Database Setup**:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create Admin User**:
```bash
python manage.py createsuperuser
```

7. **Run the Development Server**:
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to see the website and `http://127.0.0.1:8000/admin` for the admin panel.

## Admin Panel Features

The custom admin panel (accessible at `/admin`) provides:

- **Dashboard**: Overview of all content with statistics
- **Site Settings**: Manage contact info, social media links, Google Maps
- **Programs Management**: Add/edit/delete programs and projects
- **News Management**: Create and manage news articles
- **Events Management**: Schedule and manage events
- **Gallery Management**: Upload and manage photos
- **Donation Methods**: Configure payment methods and account details
- **Messages**: View and manage contact form submissions

## Configuration

### Site Settings
1. Login to admin panel at `/admin`
2. Go to "Site Settings"
3. Configure:
   - Site name and tagline
   - Contact information (phone, email, address)
   - Social media links
   - WhatsApp number
   - Google Maps embed code

### Google Maps Integration
1. Get embed code from Google Maps
2. Add it to Site Settings → Google Maps Embed field

### Email Configuration
For production, update email settings in `settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'your-smtp-server.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@domain.com'
EMAIL_HOST_PASSWORD = 'your-password'
```

## Project Structure

```
alhadid_foundation/
├── alhadid_foundation/       # Main project settings
├── website/                  # Public website app
├── admin_panel/             # Custom admin panel app
├── templates/               # HTML templates
├── static/                  # Static files (CSS, JS, images)
├── media/                   # User uploaded files
├── requirements.txt         # Python dependencies
└── manage.py               # Django management script
```

## Deployment Notes

1. **Set DEBUG=False** in production
2. **Configure proper SECRET_KEY**
3. **Set up proper email backend**
4. **Configure static files serving**
5. **Set up HTTPS** (recommended)
6. **Regular backups** of database and media files

## Support

For technical support or questions about the website, contact the development team or refer to Django documentation at https://docs.djangoproject.com

## Business Email Setup Guide

### Domain-based Email Configuration

To set up professional emails (@alhadidfoundation.org):

1. **Domain Registration**: Ensure the domain is registered and managed
2. **Email Hosting Provider**: Choose from:
   - Google Workspace (recommended)
   - Microsoft 365
   - cPanel/hosting provider email

3. **DNS Configuration**: Set up MX records pointing to your email provider

4. **Account Creation**: Create up to 10 professional email accounts

5. **Device Setup**: Configure email clients (Outlook, Mail app, etc.)

### Website Email Integration

Update these settings in `settings.py` for contact form functionality:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.your-provider.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'noreply@alhadidfoundation.org'
EMAIL_HOST_PASSWORD = 'your-email-password'
DEFAULT_FROM_EMAIL = 'Al-Hadid Foundation <noreply@alhadidfoundation.org>'
```