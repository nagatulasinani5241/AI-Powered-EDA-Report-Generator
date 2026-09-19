"""
Project Configuration File
--------------------------
Stores application-wide settings.


Change AI_PROVIDER to switch between different AI backends
without modifying the rest of the application.
"""


# ==========================
# AI Configuration
# ==========================


# AI_PROVIDER = "ollama"          # Options: "ollama", "gemini"


# OLLAMA_MODEL = "llama3.2:3b"
AI_PROVIDER = "gemini"


GEMINI_MODEL = "gemini-3.5-flash"


GEMINI_API_KEY = ""








# ==========================
# File Paths
# ==========================


# DATA_FOLDER = "data"
from pathlib import Path


DEFAULT_DATASET = Path("data") / "titanic.csv"


OUTPUT_FOLDER = "output"


PLOTS_FOLDER = "output/plots"


SUMMARY_JSON = "output/summary.json"


REPORT_FILE = "output/eda_report.txt"


# ==========================
# Visualization Settings
# ==========================


FIG_SIZE = (8, 5)


DPI = 100


# ==========================
# Outlier Detection
# ==========================


IQR_MULTIPLIER = 1.5

