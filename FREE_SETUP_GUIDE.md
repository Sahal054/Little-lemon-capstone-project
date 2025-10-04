# Free Methods to Set Up Your Production Site

## Method 1: Trigger Auto-Rebuild (Easiest)

Your build script now automatically sets up everything! Just trigger a rebuild:

### **Option A: Push a Small Change**
```bash
# Make a small change to trigger rebuild
echo "# Updated $(date)" >> README.md
git add README.md
git commit -m "trigger rebuild for auto-setup"
git push origin restaurant
```

### **Option B: Redeploy from Render Dashboard**
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Find your `little-lemon-restaurant` service
3. Click **"Manual Deploy"** → **"Deploy Latest Commit"**

## What Happens Automatically
When Render rebuilds, it will:
- Create admin user: `admin`/`admin123`
- Create demo user: `demo`/`demo123`
- Load 8 menu items automatically
- Set up restaurant configuration
- Make your site portfolio-ready

## Method 2: Manual Setup via Admin Panel

If auto-setup doesn't work, manually add menu items:

1. **Login to Admin**:
   - Visit: https://little-lemon-restaurant-c912.onrender.com/admin/
   - Try: `admin`/`admin123` (if auto-created)

2. **Add Menu Items Manually**:
   Click **"Add Menu"** and create:
   
   - **Greek Salad** - $12.99 - Inventory: 20
   - **Bruschetta** - $8.99 - Inventory: 15
   - **Grilled Fish** - $18.99 - Inventory: 12
   - **Pasta Primavera** - $16.99 - Inventory: 18
   - **Beef Steak** - $25.99 - Inventory: 8
   - **Lemon Dessert** - $7.99 - Inventory: 25
   - **Mediterranean Pizza** - $22.99 - Inventory: 10
   - **Lamb Souvlaki** - $24.99 - Inventory: 14

## Method 3: Use Django Admin Directly

Create a superuser account first:

1. **Go to Django Admin Registration**:
   Visit: https://little-lemon-restaurant-c912.onrender.com/register/

2. **Register as Regular User** then **Make Yourself Staff**:
   - Create account with your email
   - Contact site admin to make you staff (that's you!)

## Recommended: Try Method 1 First

Just push this small change to trigger auto-setup:

```bash
echo "# Portfolio ready - $(date)" >> README.md
git add README.md  
git commit -m "trigger auto-setup deployment"
git push origin restaurant
```

Wait 5-10 minutes for Render to rebuild, then check:
- https://little-lemon-restaurant-c912.onrender.com/admin/ (admin/admin123)
- https://little-lemon-restaurant-c912.onrender.com/menu/ (should show 8 items)

## After Setup Complete

Your site will have:
- **Admin Access**: `admin`/`admin123`
- **Demo User**: `demo`/`demo123`  
- **8 Menu Items** ready to showcase
- **Portfolio Ready** for employers

Perfect for job applications!