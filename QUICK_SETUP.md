# Quick Setup Guide for Your Live Site

## Your Live Little Lemon Restaurant
**URL**: https://little-lemon-restaurant-c912.onrender.com

## Complete Setup (One Command)

### **Step 1: Access Render Shell**
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Find your `little-lemon-restaurant` service
3. Click on the **"Shell"** tab

### **Step 2: Run Setup Command**
```bash
python manage.py setup_production --demo-user
```

This single command will:
- Create 8 menu items
- Create demo user (`demo`/`demo123`)
- Set up restaurant configuration
- Make your site portfolio-ready

### **Step 3: Create Admin User**
```bash
python manage.py createsuperuser
```
- **Username**: `admin`
- **Email**: `admin@littlelemon.com`
- **Password**: Choose secure password

## Your Menu Items (Auto-Created)
1. **Greek Salad** - $12.99
2. **Bruschetta** - $8.99
3. **Grilled Fish** - $18.99
4. **Pasta Primavera** - $16.99
5. **Beef Steak** - $25.99
6. **Lemon Dessert** - $7.99
7. **Mediterranean Pizza** - $22.99
8. **Lamb Souvlaki** - $24.99

## Add Images to Menu
1. Visit: https://little-lemon-restaurant-c912.onrender.com/admin/
2. Click **"Menus"**
3. Edit each item and upload food images
4. Save and view at: https://little-lemon-restaurant-c912.onrender.com/menu/

## Portfolio Demo Credentials
- **Demo User**: `demo` / `demo123`
- **Admin User**: `admin` / `[your-password]`

## Test All Features
- **Homepage**: https://little-lemon-restaurant-c912.onrender.com/
- **Menu**: https://little-lemon-restaurant-c912.onrender.com/menu/
- **Booking**: https://little-lemon-restaurant-c912.onrender.com/book/
- **Registration**: https://little-lemon-restaurant-c912.onrender.com/register/
- **Admin Panel**: https://little-lemon-restaurant-c912.onrender.com/admin/
- **API**: https://little-lemon-restaurant-c912.onrender.com/api/

## Share Your Portfolio
Your Little Lemon restaurant showcases:
- Professional Django development
- REST API with authentication
- Modern UI/UX design
- Production deployment skills
- Database management
- Enterprise-grade testing

**Perfect for job applications!**