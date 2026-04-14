# OER Agent

An AI-powered agent that helps students find open educational resources (OER) for their courses. It uses Claude to map a course name to search keywords, then queries ALG, OER Commons, and LibreTexts to return openly licensed materials.

## Prerequisites

- Python 3.10+
- Node.js and npm
- An [Anthropic API key](https://console.anthropic.com/)

### Install Node.js (if not installed)

**Fedora/RHEL:**
```bash

sudo dnf install nodejs -y
```

**Ubuntu/Debian:**
```bash
sudo apt install nodejs npm -y
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/KeysToRealities/Oer-Agent.git
cd Oer-Agent
```

### 2. Backend

```bash
cd backend
pip install -r requirements.txt
```

Copy the example env file and add your API key:

```bash
cp .env.example .env
```

Open `.env` and replace `your_api_key_here` with your actual Anthropic API key:

```
ANTHROPIC_API_KEY=your_api_key_here
```

Start the Flask server:

```bash
python app.py
```

The backend runs on `http://localhost:5000`.

### 3. Frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend runs on `http://localhost:5173`. Open that URL in your browser.

## Usage

1. Enter a course name or number (e.g. `ENGL 1101`, `Introduction to Psychology`)
2. The agent maps it to search keywords using Claude
3. Results are streamed in from ALG and OER Commons
4. If fewer than 3 results are found, LibreTexts is searched as a fallback
5. Only openly licensed resources are returned

## Project Structure

```
Oer-Agent/
├── backend/
│   ├── app.py                  # Flask API + SSE streaming
│   ├── requirements.txt
│   ├── .env.example
│   ├── services/
│   │   └── claude_service.py   # Claude keyword mapping
│   └── tools/
│       ├── alg_scraper.py      # Affordable Learning Georgia API
│       ├── oer_commons.py      # OER Commons API
│       ├── libretexts_scraper.py
│       └── license_checker.py
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   └── components/
    │       ├── SearchBar.jsx
    │       ├── ProgressLog.jsx
    │       └── ResourceCard.jsx
    └── package.json
```
