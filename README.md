# Little Lemon Restaurant 🍋

A modern Django REST Framework application for a Mediterranean restaurant with user authentication, booking system, and menu management.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Pipenv (for virtual environment management)
- MySQL database

### Installation
```bash
# Clone the repository
git clone https://github.com/Sahal054/Little_Lemon.git
cd capestone_project

# Install dependencies
pipenv install

# Activate virtual environment
pipenv shell

# Run migrations
python manage.py migrate

# Start the development server
python manage.py runserver
```

## 🔑 Superuser Credentials

**Django Admin Access:**
- **Username**: `admin`
- **Email**: `admin@example.com`
- **Password**: `admin123`

**Admin Panel**: http://127.0.0.1:8000/admin/

## 📱 Application URLs

### Web Interface (Templates)
- **Home**: http://127.0.0.1:8000/ (Public)
- **About**: http://127.0.0.1:8000/about/ (Public)
- **Menu**: http://127.0.0.1:8000/menu/ (🔒 Login Required)
- **Book Table**: http://127.0.0.1:8000/book/ (🔒 Login Required)
- **My Bookings**: http://127.0.0.1:8000/my-bookings/ (🔒 Login Required)
- **Login**: http://127.0.0.1:8000/login/
- **Register**: http://127.0.0.1:8000/register/

### API Endpoints
- **Menu Items API**: http://127.0.0.1:8000/api/menu-items/
- **Booking API**: http://127.0.0.1:8000/api/bookings/
- **User Management API**: http://127.0.0.1:8000/api/users/
- **Token Authentication**: http://127.0.0.1:8000/api-token-auth/

### Djoser Authentication APIs
- **Register**: http://127.0.0.1:8000/auth/users/
- **Login**: http://127.0.0.1:8000/auth/token/login/
- **Logout**: http://127.0.0.1:8000/auth/token/logout/

## 🏗️ Architecture

### Technology Stack
- **Backend**: Django 5.2.6 + Django REST Framework
- **Database**: MySQL
- **Authentication**: Django + Djoser + Token Authentication
- **Frontend**: Django Templates + Custom CSS
- **Environment**: Pipenv Virtual Environment

### Key Features
- ✅ **User Authentication System** (Registration, Login, Logout)
- ✅ **Protected Routes** (Menu & Booking require login)
- ✅ **Personal Booking Management** ("My Bookings" feature)
- ✅ **API-First Architecture** (All views use API logic internally)
- ✅ **Consistent Validation** (Same serializers for web & API)
- ✅ **User-Specific Data** (Each user sees only their bookings)
- ✅ **Admin Panel** (Full CRUD operations for staff)

## 💾 Database Schema

### Models
```python
class Menu:
    title = CharField(max_length=255)
    price = DecimalField(max_digits=10, decimal_places=2)
    inventory = IntegerField()

class Booking:
    user = ForeignKey(User, on_delete=CASCADE)  # Links to authenticated user
    name = CharField(max_length=255)
    no_of_guests = IntegerField()
    booking_date = DateTimeField()
```

## 🧪 Testing the Application

### Test Flow
1. **Visit Protected Pages**: Try accessing `/menu/` or `/book/` → redirected to login
2. **Register New User**: Go to `/register/` and create an account
3. **Login**: Use your credentials to log in → **automatic redirect to requested page**
4. **Make Bookings**: Use `/book/` to create reservations (**proper web forms, no API interface**)
5. **View Your Bookings**: Check `/my-bookings/` to see your reservation history (**web interface only**)

### Authentication Flow
- **Session-Based**: Web interface uses Django sessions (no manual tokens needed)
- **Automatic Login**: After successful authentication, users stay logged in
- **Protected Routes**: Menu, booking, and personal pages require login
- **Clean Redirects**: Login redirects users back to the page they wanted to visit

### Sample Data
The application includes sample menu items:
- Greek Salad ($12.99)
- Bruschetta ($8.99)
- Grilled Salmon ($18.99)
- Lemon Pasta ($16.99)
- Mediterranean Bowl ($14.99)

## 🔧 Development Commands

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Django shell
python manage.py shell

# Run tests
python manage.py test
```

## 📁 Project Structure

```
capestone_project/
├── littlelemon/           # Main project settings
├── restaurant/            # Main app
│   ├── models.py         # Database models
│   ├── views.py          # API + Template views
│   ├── serializers.py    # DRF serializers
│   ├── urls.py           # App URLs
│   ├── templates/        # HTML templates
│   └── static/css/       # Stylesheets
├── manage.py
├── Pipfile               # Dependencies
└── README.md
```

## 🎨 Frontend Features

### Navigation
- **Public Users**: Home, About, Login, Register
- **Authenticated Users**: Home, About, Menu, Book, My Bookings, Logout

### My Bookings Page
- Shows all user's reservations
- Status indicators (Upcoming/Completed)
- Total booking count
- Quick links to make new reservations

## 🔒 Security Features

- **Authentication Required**: Menu and booking pages protected
- **User-Specific Data**: Users can only see their own bookings
- **Staff Access**: Admin users can view all bookings
- **Token Authentication**: API endpoints secured with tokens
- **CSRF Protection**: Form submissions protected

## 🚀 Deployment Notes

For production deployment:
1. Set `DEBUG = False` in settings
2. Configure proper database settings
3. Set up static file serving
4. Use a production WSGI server (gunicorn, uWSGI)
5. Configure reverse proxy (nginx, Apache)

## 📞 Support

For issues or questions:
- **Repository**: https://github.com/Sahal054/Little_Lemon
- **Branch**: restaurant

---

**Little Lemon Restaurant** - A family-owned Mediterranean restaurant focused on traditional recipes served with a modern twist. 🇬🇷🍋