# Git Commands for Ice Cream App

## 🚀 Initial Push to GitHub

### Step 1: Initialize Git (if not already done)
```bash
git init
```

### Step 2: Add Remote Repository
```bash
git remote add origin https://github.com/vikashere96/ice-cream-app.git
```

### Step 3: Add All Files
```bash
git add .
```

### Step 4: Commit Changes
```bash
git commit -m "Initial commit: Ice Cream QR Ordering System"
```

### Step 5: Push to GitHub
```bash
git push -u origin main
```

If you get an error about branch name, try:
```bash
git branch -M main
git push -u origin main
```

---

## 📥 Clone on Another Computer

### Step 1: Clone Repository
```bash
git clone https://github.com/vikashere96/ice-cream-app.git
cd ice-cream-app
```

### Step 2: Setup Environment
```bash
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure
```bash
# Copy environment file
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# Edit .env with your settings
```

### Step 4: Setup Database
```bash
python manage.py migrate
python manage.py createsuperuser
```

### Step 5: Run
```bash
python manage.py runserver
```

---

## 🔄 Regular Updates

### Pull Latest Changes
```bash
git pull origin main
```

### Push Your Changes
```bash
# Add changes
git add .

# Commit with message
git commit -m "Description of changes"

# Push to GitHub
git push origin main
```

---

## 📝 Common Git Commands

### Check Status
```bash
git status
```

### View Changes
```bash
git diff
```

### View Commit History
```bash
git log
```

### Discard Local Changes
```bash
git checkout -- filename
```

### Create New Branch
```bash
git checkout -b feature-name
```

### Switch Branch
```bash
git checkout main
```

---

## ⚠️ Important Notes

1. **Never commit `.env` file** - Contains sensitive data
2. **Never commit `db.sqlite3`** - Database file
3. **Never commit `media/` folder** - User uploads
4. **Never commit `venv/` folder** - Virtual environment
5. **Never commit `__pycache__/`** - Python cache

These are already in `.gitignore` file.

---

## 🔒 Security Checklist

Before pushing to GitHub:
- [ ] `.env` file is in `.gitignore`
- [ ] `firebase-service-account-key.json` is in `.gitignore`
- [ ] No passwords in code
- [ ] No API keys in code
- [ ] `DEBUG=False` for production

---

## 📦 What Gets Pushed

✅ **Included:**
- Source code (`.py` files)
- Templates (`.html` files)
- Static files (CSS, JS)
- Requirements file
- README and documentation
- `.gitignore` file
- `.env.example` file

❌ **Excluded:**
- `.env` file (sensitive data)
- `db.sqlite3` (database)
- `media/` folder (uploads)
- `venv/` folder (virtual environment)
- `__pycache__/` (Python cache)
- Firebase credentials

---

## 🆘 Troubleshooting

### Error: "fatal: remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/vikashere96/ice-cream-app.git
```

### Error: "Updates were rejected"
```bash
git pull origin main --rebase
git push origin main
```

### Error: "Permission denied"
- Check GitHub credentials
- Use personal access token instead of password
- Configure SSH keys

### Undo Last Commit (not pushed)
```bash
git reset --soft HEAD~1
```

### Force Push (use carefully!)
```bash
git push -f origin main
```

---

## 📚 Quick Reference

```bash
# Setup
git clone <url>           # Clone repository
git init                  # Initialize git

# Daily workflow
git status               # Check status
git add .                # Add all changes
git commit -m "message"  # Commit changes
git push                 # Push to GitHub
git pull                 # Pull from GitHub

# Branches
git branch               # List branches
git checkout -b <name>   # Create branch
git checkout <name>      # Switch branch
git merge <name>         # Merge branch

# Undo
git checkout -- <file>   # Discard changes
git reset HEAD <file>    # Unstage file
git reset --soft HEAD~1  # Undo commit
```

---

**Happy Coding! 🚀**
