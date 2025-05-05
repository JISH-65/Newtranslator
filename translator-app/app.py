"""Flask backend for the Language Translator UI
------------------------------------------------
Features
~~~~~~~~
* Wraps AWS Translate via boto3.
* Persists the user‑selected source & target language
  codes so the form stays populated after each request.
* Clean separation of GET (page load) and POST (translation) routes.
* Adds a lightweight /health endpoint for container health checks.
* All defaults and ports are environment‑overrideable for flexibility.
"""

from __future__ import annotations

import os

from flask import Flask, jsonify, render_template, request
import boto3

# ----------------------------------------------------------------------------
# Flask App Setup
# ----------------------------------------------------------------------------

app = Flask(__name__)

# (Optional) auto‑reload templates in dev without restarting.
if app.env == "development":
    app.config["TEMPLATES_AUTO_RELOAD"] = True

# ----------------------------------------------------------------------------
# AWS Translate Client (assumes IAM role / env credentials are set up)
# ----------------------------------------------------------------------------

translate = boto3.client(
    "translate", region_name=os.getenv("AWS_REGION", "us-east-1")
)

# ----------------------------------------------------------------------------
# Routes
# ----------------------------------------------------------------------------


@app.route("/", methods=["GET"])
def index():
    """Initial page load with blank form."""
    return render_template(
        "index.html",
        source_text="",
        translated_text="",
        source_lang="en",
        target_lang="es",
    )


@app.route("/translate", methods=["POST"])
def translate_text():
    """Translate the submitted text via AWS Translate and return the page."""

    source_text: str = request.form.get("sourceText", "")
    source_lang: str = request.form.get("sourceLang", "en")
    target_lang: str = request.form.get("targetLang", "es")
    translated_text: str = ""

    if source_text:
        try:
            response = translate.translate_text(
                Text=source_text,
                SourceLanguageCode=source_lang,
                TargetLanguageCode=target_lang,
            )
            translated_text = response.get("TranslatedText", "")
        except Exception as exc:  # broad except is fine for UI surface
            translated_text = f"Error: {exc}"

    return render_template(
        "index.html",
        source_text=source_text,
        translated_text=translated_text,
        source_lang=source_lang,
        target_lang=target_lang,
    )


@app.route("/health", methods=["GET"])
def health() -> tuple[str, int]:
    """Lightweight endpoint for container orchestrators / uptime checks."""

    return jsonify(status="ok"), 200


# ----------------------------------------------------------------------------
# Entry Point (only used when running directly, eg. `python app.py`)
# ----------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        debug=app.env == "development",
    )
