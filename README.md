# 🔐 PyCyberTools API

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0+-000000?style=for-the-badge&logo=flask&logoColor=white)
![Render](https://img.shields.io/badge/Deployed_on-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)

**RESTful backend API for the PyCyberTools ethical hacking toolkit.**
Built with Python & Flask. Powers 7 real security tools accessible from any browser.

[🌐 Live Demo](https://pycybertools.vercel.app) · [🖥️ Frontend Repo](https://github.com/PrasadCyberPerfect/pycybertools) · [📬 API Base URL](https://pycybertools-api.onrender.com)

</div>

---

## ⚠️ Disclaimer

> **This project is strictly for educational purposes.**
> All tools must only be used on systems you **own** or have **explicit written permission** to test.
> Unauthorized scanning, cracking, or probing of systems you don't own is **illegal** and unethical.
> The author holds no responsibility for any misuse of this software.

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Tools & Endpoints](#-tools--endpoints)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [API Reference](#-api-reference)
- [Local Setup](#-local-setup)
- [Deploy on Render](#-deploy-on-render)
- [Environment Variables](#-environment-variables)
- [Legal Testing Environments](#-legal-testing-environments)
- [Roadmap](#-roadmap)
- [Author](#-author)
- [License](#-license)

---

## 🔍 Overview

**PyCyberTools API** is the Python backend that powers the [PyCyberTools](https://pycybertools.vercel.app) web application — a browser-based ethical hacking toolkit built for learning and practice.

The frontend (hosted on Vercel) sends requests to this Flask API, which runs the actual security tools on the server and returns real results in JSON format.

```
User (Browser)
     │
     ▼
┌─────────────────────┐        ┌──────────────────────────┐
│  Frontend (Vercel)  │──────▶│  Backend API (Render)    │
│  HTML + CSS + JS    │  POST  │  Flask + Python          │
│  pycybertools.vercel│◀──────│  Real tool execution     │
│  .app               │  JSON  │  pycybertools-api.onrender│
└─────────────────────┘        └──────────────────────────┘
```

---

## 🛠️ Tools & Endpoints

| # | Tool | Endpoint | Method | Description |
|---|------|----------|--------|-------------|
| 1 | 🔍 **Port Scanner** | `/api/port-scan` | POST | Multi-threaded TCP connect scan |
| 2 | 📡 **Banner Grabber** | `/api/banner-grab` | POST | Reads service banners from open ports |
| 3 | 🔓 **Hash Cracker** | `/api/hash-crack` | POST | Dictionary attack on MD5/SHA hashes |
| 4 | 🌐 **Subdomain Finder** | `/api/subdomain` | POST | DNS brute-force subdomain discovery |
| 5 | 🔑 **Password Generator** | `/api/passgen` | POST | Cryptographically secure passwords |
| 6 | 🔎 **WHOIS Lookup** | `/api/whois` | POST | Domain/IP registration information |
| 7 | 🌍 **DNS Lookup** | `/api/dns` | POST | A record + reverse PTR resolution |
| - | ❤️ **Health Check** | `/api/health` | GET | API status check |

---

## 💻 Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Language | Python 3.10+ | Core backend logic |
| Framework | Flask 3.0 | REST API server |
| CORS | Flask-CORS | Allow cross-origin requests from Vercel |
| Concurrency | `threading` | Multi-threaded port scanning |
| Crypto | `hashlib`, `secrets` | Hash cracking & password generation |
| Networking | `socket` | Port scanning, banner grabbing, WHOIS |
| Server | Gunicorn | Production WSGI server on Render |
| Deployment | Render.com | Free cloud hosting |

---

## 📁 Project Structure

```
pycybertools-api/
│
├── app.py                  ← Flask app, all API routes
│
├── tools/
│   ├── __init__.py
│   └── engine.py           ← All tool logic (scanner, cracker, etc.)
│
├── requirements.txt        ← Python dependencies
├── Procfile                ← Render/Gunicorn startup command
├── render.yaml             ← Render deployment config
├── .gitignore
└── README.md
```

---

## 📬 API Reference

All endpoints accept `Content-Type: application/json` and return JSON.

---

### `GET /api/health`
Check if the API is online.

**Response:**
```json
{
  "status": "ok"
}
```

---

### `POST /api/port-scan`
Scan open TCP ports on a target.

**Request Body:**
```json
{
  "target": "scanme.nmap.org",
  "start": 1,
  "end": 1024,
  "threads": 150
}
```

**Response:**
```json
{
  "ip": "45.33.32.156",
  "target": "scanme.nmap.org",
  "count": 3,
  "open_ports": [
    { "port": 22,  "service": "ssh"   },
    { "port": 80,  "service": "http"  },
    { "port": 443, "service": "https" }
  ]
}
```

---

### `POST /api/banner-grab`
Grab service banners from open ports.

**Request Body:**
```json
{
  "target": "127.0.0.1",
  "ports": "22,80,443,3306",
  "timeout": 3.0
}
```

**Response:**
```json
{
  "ip": "127.0.0.1",
  "grabbed": 2,
  "total": 4,
  "results": [
    { "port": 22,  "status": "open",   "banner": "SSH-2.0-OpenSSH_8.9p1 Ubuntu" },
    { "port": 80,  "status": "open",   "banner": "HTTP/1.1 200 OK" },
    { "port": 443, "status": "closed", "banner": "" },
    { "port": 3306,"status": "closed", "banner": "" }
  ]
}
```

---

### `POST /api/hash-crack`
Dictionary attack on a password hash.

**Request Body:**
```json
{
  "hash": "5f4dcc3b5aa765d61d8327deb882cf99",
  "algo": "auto"
}
```

**Supported algorithms:** `auto`, `md5`, `sha1`, `sha256`, `sha512`

**Response (found):**
```json
{
  "found": true,
  "password": "password",
  "algo": "MD5",
  "attempts": 1,
  "time": 0.001,
  "identified": "MD5",
  "source": "built-in list"
}
```

**Response (not found):**
```json
{
  "found": false,
  "algo": "MD5",
  "attempts": 35,
  "time": 0.002,
  "identified": "MD5",
  "note": "Not found in built-in list. Provide a wordlist for full cracking."
}
```

---

### `POST /api/subdomain`
Brute-force subdomains via DNS resolution.

**Request Body:**
```json
{
  "domain": "example.com"
}
```

**Response:**
```json
{
  "domain": "example.com",
  "count": 3,
  "tried": 55,
  "found": [
    { "subdomain": "api.example.com",  "ip": "93.184.216.60" },
    { "subdomain": "mail.example.com", "ip": "93.184.216.50" },
    { "subdomain": "www.example.com",  "ip": "93.184.216.34" }
  ]
}
```

---

### `POST /api/passgen`
Generate cryptographically secure passwords.

**Request Body:**
```json
{
  "length": 16,
  "count": 5,
  "upper": true,
  "digits": true,
  "symbols": true,
  "noAmbiguous": false
}
```

**Response:**
```json
{
  "passwords": [
    { "password": "xK9#mP2@nL5$vQ8!", "entropy": 104.8, "strength": "Very Strong" },
    { "password": "Rt7&wN3^hJ6*cF1@", "entropy": 104.8, "strength": "Very Strong" }
  ]
}
```

---

### `POST /api/whois`
Look up domain registration information.

**Request Body:**
```json
{
  "target": "google.com"
}
```

**Response:**
```json
{
  "server": "whois.verisign-grs.com",
  "parsed": {
    "Domain Name": "GOOGLE.COM",
    "Registrar": "MarkMonitor Inc.",
    "Creation Date": "1997-09-15T04:00:00Z",
    "Registry Expiry Date": "2028-09-14T04:00:00Z",
    "Name Server": "NS1.GOOGLE.COM"
  },
  "raw": "..."
}
```

---

### `POST /api/dns`
Resolve DNS records for a domain.

**Request Body:**
```json
{
  "target": "github.com"
}
```

**Response:**
```json
{
  "target": "github.com",
  "records": {
    "A":   ["140.82.121.3"],
    "PTR": ["lb-140-82-121-3-iad.github.com"]
  }
}
```

---

### Error Response Format
All errors return a consistent JSON structure:
```json
{
  "error": "Description of what went wrong"
}
```

---

## ⚙️ Local Setup

### Prerequisites
- Python 3.10 or higher
- pip

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/PrasadCyberPerfect/pycybertools-api.git
cd pycybertools-api

# 2. (Optional) Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate      # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the server
python app.py

# API is now running at http://localhost:5000
```

### Test it
```bash
# Health check
curl http://localhost:5000/api/health

# Generate passwords
curl -X POST http://localhost:5000/api/passgen \
  -H "Content-Type: application/json" \
  -d "{\"length\": 16, \"count\": 3}"
```

---

## 🚀 Deploy on Render

This project is configured for **one-click deployment** on [Render.com](https://render.com) (free tier).

### Steps

1. **Fork or push** this repo to your GitHub account

2. **Go to** [render.com](https://render.com) → Sign up free

3. **New Web Service** → Connect GitHub → Select this repo

4. Render auto-detects settings from `render.yaml`:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Python Version:** 3.11

5. Click **Deploy** — takes ~2 minutes

6. Your API is live at:
   ```
   https://pycybertools-api.onrender.com
   ```

7. **Update the frontend** — open `frontend/index.html` and change:
   ```js
   const API = "https://pycybertools-api.onrender.com";
   ```

> **Note:** Render free tier sleeps after 15 minutes of inactivity. First request after sleep takes ~30 seconds to wake up.

---

## 🔑 Environment Variables

No environment variables required for basic deployment.

| Variable | Default | Description |
|---|---|---|
| `PORT` | `5000` | Server port (auto-set by Render) |

---

## 🧪 Legal Testing Environments

**Only use these tools on authorized targets:**

| Resource | URL | Use For |
|---|---|---|
| Nmap test server | `scanme.nmap.org` | Port scanning (publicly authorized) |
| TryHackMe | [tryhackme.com](https://tryhackme.com) | Legal CTF practice rooms |
| HackTheBox | [hackthebox.com](https://hackthebox.com) | Legal CTF machines |
| DVWA | [github.com/digininja/DVWA](https://github.com/digininja/DVWA) | Vulnerable web app (run locally) |
| Your own VM | localhost / 127.0.0.1 | Any testing |

---

## 🛣️ Roadmap

- [x] Port Scanner
- [x] Banner Grabber
- [x] Hash Cracker (MD5, SHA1, SHA256, SHA512)
- [x] Subdomain Finder
- [x] Password Generator
- [x] WHOIS Lookup
- [x] DNS Lookup
- [ ] HTTP Header Inspector
- [ ] SSL/TLS Certificate Inspector
- [ ] Open Redirect Checker
- [ ] Rate limiting & API key authentication
- [ ] Result export (JSON / CSV download)
- [ ] Scan history log

---

## 👨‍💻 Author

**Prasad Madole** — [PrasadCyberPerfect](https://github.com/PrasadCyberPerfect)

- 🎓 Engineering Student
- 🔐 Cybersecurity Learner
- 💻 Web & Android Developer
- 📍 Maharashtra, India

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

```
MIT License — Use responsibly. Stay ethical. 🔐
```

---

## 🌟 Support

If this project helped you, please consider giving it a ⭐ on GitHub — it helps others discover it!

---

<div align="center">
  Made with ❤️ by <a href="https://github.com/PrasadCyberPerfect">PrasadCyberPerfect</a>
  <br/>
  <sub>Stay ethical. Learn. Build. 🔐</sub>
</div>
