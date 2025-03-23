# Backend of AI based recruitment management system. 

# Project Setup Guide

## Prerequisites
Ensure you have Python installed on your system. You can download it from [python.org](https://www.python.org/).

## Setup Instructions

### 1. Create and Activate a Virtual Environment
```sh
python -m venv venv
```

#### Windows (PowerShell)
```sh
venv\Scripts\Activate.ps1
```

#### macOS/Linux
```sh
source venv/bin/activate
```

### 2. Install Dependencies
```sh
pip install -r requirements.txt
```

### 3. Install Browsers for Playwright
```sh
playwright install
```

### 4. Run the FastAPI Application
```sh
fastapi dev app.py
```

### 5. Access API Documentation
Once the server is running, open your browser and go to:
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

