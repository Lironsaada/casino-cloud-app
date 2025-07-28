# 🎰 Casino Cloud App 🎰

*A luxurious, full-featured casino web application built with Flask*

**Developed by Liron Saada** | Built with ❤️ using Flask & Bootstrap

---

## 🌟 Overview

Casino Cloud App is a sophisticated web-based casino platform featuring multiple classic casino games, user management, social features, and a comprehensive admin panel. The application combines elegant UI design with robust backend functionality to deliver an authentic casino experience.

---

## 🎮 Game Features

### 🃏 **Blackjack**
- **Interactive card animations** with realistic playing cards
- **Natural Blackjack** detection with 3:2 payouts
- **Double Down** functionality with proper betting mechanics
- **Automatic game resolution** (bust detection, 21 auto-win)
- **Dealer AI** following standard casino rules (hit on 16, stand on 17)

### 🎡 **Roulette**
- **Realistic spinning wheel** with smooth physics-based animation
- **Multiple betting options**: Red, Black, Green
- **Visual feedback** with spinning animation and result highlighting
- **Authentic payouts**: 2x for Red/Black, 14x for Green
- **Sound effects** for enhanced gaming experience

### 🎰 **Slots**
- **Interactive slot machine** with spinning reel animations
- **Multiple betting tiers**: 10, 100, 1000 coins
- **Various symbols**: 🍒, 🔔, 🍋, ⭐, 💎, 7️⃣
- **Progressive payouts** based on symbol combinations
- **Jackpot system** for triple matches

---

## 🔧 Core Features

### 👤 **User Management**
- **Secure authentication** with hashed passwords (Werkzeug)
- **Persistent user accounts** with balance tracking
- **Session management** with secure cookies
- **User registration** and login system

### 💰 **Financial System**
- **Real-time balance updates** across all games
- **Transaction logging** for all bets and tips
- **Secure balance management** with validation
- **Anti-cheat measures** and input sanitization

### 🎁 **Social Features**
- **Tip system** for sending coins between users
- **Real-time balance updates** for both sender and receiver
- **Transaction history** tracking for all activities
- **User-friendly interface** with clear feedback

### 👑 **Admin Panel**
- **Password-protected access** (password: "admin")
- **User balance management** (add, subtract, set)
- **User statistics dashboard** with total users and balances
- **Quick action forms** for efficient administration
- **Dark-themed professional interface**

---

## 🎨 Design & UI

### ✨ **Visual Design**
- **Luxurious color palette** with gold accents and deep blues
- **Animated background particles** for dynamic ambiance
- **Gradient backgrounds** and professional shadows
- **Responsive design** optimized for all devices
- **Custom animations** for enhanced user experience

### 🃏 **Interactive Elements**
- **Custom card animations** in Blackjack (Ace + 10 reveal)
- **Spinning roulette wheel** with realistic physics
- **Slot machine lever** with pull-down animation
- **Hover effects** and smooth transitions throughout
- **Professional button styling** with gradients and shadows

---

## 🛠 Technology Stack

### **Backend**
- **Flask** - Python web framework
- **Werkzeug** - Password hashing and security
- **JSON** - Data persistence and user storage
- **Session management** - Secure user authentication

### **Frontend**
- **Bootstrap 5** - Responsive CSS framework
- **Font Awesome** - Professional icon library
- **Custom CSS** - Luxurious casino-themed styling
- **Vanilla JavaScript** - Interactive animations and AJAX

### **Security**
- **Environment variables** for sensitive configuration
- **Password hashing** using Werkzeug security
- **Input validation** and sanitization
- **Session-based authentication**
- **Comprehensive `.gitignore`** for data protection

---

## 🚀 Quick Start

### **Prerequisites**
- Python 3.7+
- Flask and dependencies (see requirements.txt)

### **Installation**

1. **Clone the repository**
   ```bash
   git clone https://github.com/lironsaada/casino-cloud-app.git
   cd casino-cloud-app
   ```

2. **Set up virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   export FLASK_SECRET_KEY="your-secret-key-here"
   # Or create a .env file with: FLASK_SECRET_KEY=your-secret-key-here
   ```

5. **Run the application**
   ```bash
   python3 -m app.app
   ```

6. **Access the application**
   ```
   Open your browser to: http://localhost:5000
   ```

### **First Time Setup**
1. Register a new user account
2. Start with 1000 coins default balance
3. Try the games or tip other users
4. Access admin panel with password: `admin`

---

## 📁 Project Structure

```
casino-cloud-app/
├── app/
│   ├── app.py              # Main Flask application
│   ├── casino.py           # Game logic and utilities
│   └── templates/          # HTML templates
│       ├── base.html       # Base template with navigation
│       ├── menu.html       # Game selection with animations
│       ├── blackjack_*.html # Blackjack game templates
│       ├── roulette.html   # Roulette game interface
│       ├── slots.html      # Slots game interface
│       ├── tip.html        # Tipping system
│       ├── admin*.html     # Admin panel templates
│       └── *.html          # Authentication templates
├── scripts/
│   └── migrate_passwords.py # Password migration utility
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore rules
├── SECURITY.md            # Security guidelines
└── README.md              # This file
```

---

## 🎯 Game Rules

### **Blackjack**
- Goal: Get as close to 21 without going over
- Face cards worth 10, Aces worth 1 or 11
- Natural Blackjack pays 3:2
- Double down doubles your bet for one card
- Dealer hits on 16, stands on 17

### **Roulette**
- Red/Black: 2x payout (18/38 chance)
- Green: 14x payout (2/38 chance)
- Animated wheel shows result

### **Slots**
- Bet 10, 100, or 1000 coins
- Three matching symbols for jackpot
- Two matching symbols for smaller wins
- Higher value symbols = bigger payouts

---

## 🔐 Security Features

- **Password hashing** using Werkzeug's secure methods
- **Environment variable** protection for secret keys
- **Input validation** on all user inputs
- **Session security** with secure cookie handling
- **Data file protection** via .gitignore
- **Admin access control** with password authentication

---

## 🐳 Docker Support

### **Build Docker Image**
```bash
docker build -t lironsaada/casino-app:latest .
```

### **Run with Docker**
```bash
docker run -p 5000:5000 -e FLASK_SECRET_KEY="your-secret-key" lironsaada/casino-app:latest
```

### **Push to Docker Hub**
```bash
docker push lironsaada/casino-app:latest
```

---

## 🛠 Development

### **Adding New Games**
1. Create game logic in `casino.py`
2. Add route in `app.py`
3. Create HTML template in `templates/`
4. Add game card to `menu.html`

### **Customizing UI**
- Modify CSS variables in `base.html`
- Update color scheme in the `:root` section
- Add animations in individual templates

### **Database Migration**
- Users stored in `users.json`
- Balance history in `balance_history.json`
- Use `scripts/migrate_passwords.py` for password updates

---

## 📊 Admin Features

Access the admin panel at `/admin_auth` with password: `admin`

**Available Actions:**
- View all user accounts and balances
- Add/subtract coins from user accounts
- Set specific balance amounts
- Monitor total platform statistics
- Quick action forms for efficiency

---

## 🎨 Customization

### **Color Scheme**
The app uses CSS custom properties for easy theming:
```css
--dark-blue: #1a237e
--primary-gold: #ffd700
--accent-purple: #6b46c1
```

### **Game Settings**
- Default starting balance: 1000 coins
- Blackjack natural payout: 3:2
- Roulette green payout: 14x
- Admin password: "admin"

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📝 License

This project is developed by **Liron Saada**. All rights reserved.

---

## 👨‍💻 Developer

**Liron Saada**
- 🎯 Full-stack developer specializing in Python/Flask
- 🎨 UI/UX design with focus on user experience
- 🔒 Security-conscious development practices
- 🎰 Passionate about creating engaging web applications

---

## 🎉 Acknowledgments

- **Flask** community for the excellent web framework
- **Bootstrap** team for responsive design components
- **Font Awesome** for beautiful icons
- **Casino gaming** industry for inspiration

---

*Built with ❤️ using Flask & Bootstrap*

**© 2025 Casino Cloud App | Developed by Liron Saada**
