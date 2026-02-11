# Chemical Equipment Parameter Visualizer

A full-stack, cross-platform application (Web & Desktop) designed for monitoring critical chemical plant data. This system features real-time anomaly detection for safety, automated PDF reporting, and a unified REST API backend.

![Project Banner](https://img.shields.io/badge/Status-Production%20Ready-success)
![Python](https://img.shields.io/badge/Backend-Django%20REST-blue)
![React](https://img.shields.io/badge/Frontend-React%20%2B%20Tailwind-teal)
![Desktop](https://img.shields.io/badge/Desktop-PyQt5-orange)

---

## Standout Features (Why this project is unique)

* **Automated Anomaly Detection:** The system automatically flags equipment operating outside safe parameters (**Pressure > 5.0 Bar** or **Temp > 80°C**) in real-time, highlighting them in Red across both Web and Desktop interfaces.
* **Cross-Platform Sync:** Data uploaded via the Desktop app is instantly available on the Web dashboard (and vice-versa) thanks to a centralized API architecture.
* **Automated Reporting:** Generates professional, executive-level PDF reports with embedded matplotlib charts and executive summaries on the fly.
* **Deployment Ready:** Includes `Dockerfile` and containerization support for the backend.
* **Live Filtering:** Client-side, instant search allows operators to filter through thousands of equipment records in milliseconds without server lag.

---

## Tech Stack

### **Backend (The Core)**
* **Framework:** Django & Django REST Framework (DRF)
* **Database:** SQLite (Dev) / PostgreSQL (Ready)
* **Analysis:** Pandas & NumPy (Data Processing)
* **Reporting:** ReportLab (PDF Generation) & Matplotlib (Server-side Charting)

### **Web Frontend (The Operator Console)**
* **Framework:** React.js
* **Styling:** Tailwind CSS
* **Charts:** Chart.js & React-Chartjs-2
* **HTTP Client:** Axios

### **Desktop Frontend (The Engineer Station)**
* **Framework:** PyQt5 (Python)
* **Visualization:** Matplotlib Integration (Qt5Agg)
* **Style:** Custom "Modern-Flat" Stylesheet

---

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **Node.js 14+ and npm** ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/downloads))
- **(Optional) Docker** for containerized deployment ([Download](https://www.docker.com/))

---

## Project Structure

```text
chemical-equipment-visualizer/
├── backend/                 # Django DRF Server
│   ├── api/                 # API Views, Models, Serializers
│   ├── manage.py
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile           # Containerization Config
├── web-frontend/            # React Application
│   ├── public/
│   ├── src/
│   │   ├── components/      # Dashboard & Charts
│   │   ├── assets/          # Icons & Images
│   │   └── App.js
│   ├── package.json
│   └── tailwind.config.js
├── desktop-frontend/        # PyQt5 Application
│   ├── assets/              # Icons (Synced with Web)
│   ├── main.py              # Desktop Entry Point
│   └── requirements.txt     # Desktop dependencies
└── README.md
```

---

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/hazelr125/chemical-equipment-visualizer.git
cd chemical-equipment-visualizer
```

### 2. Backend Setup (Run this first!)

The backend serves the API for both the Web and Desktop apps.

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run Migrations
python manage.py migrate

# Create Admin User (For Login)
python manage.py createsuperuser
# Follow prompts to set username/password

# Start Server
python manage.py runserver
```

**Backend running at:** `http://127.0.0.1:8000/`

---

### 3. Web Frontend Setup

Open a **new terminal window** (keep the backend running):

```bash
cd web-frontend

# Install Node Modules
npm install

# Start React Dev Server
npm start
```

**Web app running at:** `http://localhost:3000/`

---

### 4. Desktop Frontend Setup

Open another **new terminal window**:

```bash
cd desktop-frontend

# Install Desktop Requirements
pip install -r requirements.txt
# Or manually: pip install PyQt5 matplotlib requests pandas

# Run the Desktop App
python main.py
```

---

## Docker Deployment (Alternative)

For containerized deployment of the backend:

```bash
cd backend

# Build Docker image
docker build -t chemical-visualizer-api .

# Run container
docker run -p 8000:8000 chemical-visualizer-api
```

For production with PostgreSQL, update your `settings.py` and use `docker-compose`.

---

## Login Credentials

Use the credentials you created during the `createsuperuser` step:

- **Username:** `admin` (or whatever you set)
- **Password:** `your-secure-password`

> **Note:** These credentials work for both Web and Desktop applications.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/login/` | Authenticates user & returns Auth Token |
| `POST` | `/api/upload/` | Uploads CSV & returns analysis JSON |
| `GET` | `/api/history/` | Returns list of past uploaded datasets |
| `GET` | `/api/history/<id>/` | Returns specific dataset details |
| `GET` | `/api/report/<id>/` | Downloads the generated PDF Report |

### Example API Request

```bash
# Login
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"yourpassword"}'

# Upload CSV (with authentication token)
curl -X POST http://127.0.0.1:8000/api/upload/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -F "file=@data.csv"
```

---

## Sample Data (Testing Anomaly Detection)

Create a file named `data.csv` with the following format:

```csv
Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-A,Pump,100,4.5,75
Valve-X,Valve,50,9.2,85
Tank-99,Tank,200,3.0,105
Reactor-5,Reactor,150,2.8,65
```

**Anomaly Rules:**
- **Red Alert:** Pressure > 5.0 Bar OR Temperature > 80°C
- **Normal:** All parameters within safe range

In the example above:
- `Valve-X` triggers RED (Pressure = 9.2 > 5.0)
- `Tank-99` triggers RED (Temperature = 105 > 80)

---

## Screenshots

### Web Dashboard
![Web Dashboard Preview](https://via.placeholder.com/800x400?text=Web+Dashboard+Screenshot)

### Desktop Application
![Desktop App Preview](https://via.placeholder.com/800x400?text=Desktop+App+Screenshot)

### PDF Report Sample
![Report Preview](https://via.placeholder.com/800x400?text=PDF+Report+Screenshot)

> *Replace placeholder images with actual screenshots from your application*

---

## Security Considerations

- **Never commit** your `SECRET_KEY` or database credentials to version control
- Store sensitive configuration in environment variables or `.env` files
- For production deployment:
  - Set `DEBUG = False` in Django settings
  - Use strong passwords for admin accounts
  - Enable HTTPS/SSL
  - Use PostgreSQL instead of SQLite
  - Configure CORS properly to restrict API access

---

## Roadmap / Future Features

- [ ] Multi-user role management (Admin, Operator, Viewer)
- [ ] Real-time WebSocket notifications for anomalies
- [ ] Historical trend analysis with time-series prediction
- [ ] Email alerts for critical equipment failures
- [ ] Mobile app (React Native)
- [ ] Integration with industrial IoT sensors

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## Credits & Acknowledgments

- **Icons:** [Iconmonstr](https://iconmonstr.com/) (Public Domain)
- **Charts:** Powered by [Chart.js](https://www.chartjs.org/) and [Matplotlib](https://matplotlib.org/)
- **UI Framework:** [Tailwind CSS](https://tailwindcss.com/)
- **Backend:** [Django REST Framework](https://www.django-rest-framework.org/)

---

**If you find this project useful, please consider giving it a star!**
