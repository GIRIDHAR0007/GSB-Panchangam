# GSB Panchangam

This repository now contains a web-based Panchangam app with a Flask backend.

## Structure

- `api/index.py` — Vercel entry point for the Flask app
- `api/app.py` — Flask application logic
- `templates/index.html` — web page template
- `panchangam.py` — calculation logic used by the app
- `assets/` — required ephemeris files
- `requirements.txt` — Python dependencies
- `vercel.json` — Vercel deployment configuration

## Run locally

```bash
python -m pip install -r requirements.txt
python api/index.py
```

Then open `http://127.0.0.1:5000` in your browser.

## Deploy

This project is configured for Vercel deployment.

If you need APK packaging or legacy mobile builds later, I can help add a separate branch or folder for that.
