# ── Base image ─────────────────────────────────────────────────────────────
FROM python:3.10-slim

# ── Variables d'environnement ───────────────────────────────────────────────
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=7860

# ── Dépendances système ─────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    wget \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ── Répertoire de travail ───────────────────────────────────────────────────
WORKDIR /app

# ── Installer les dépendances Python ───────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ── Copier le projet ────────────────────────────────────────────────────────
COPY . .

# ── Créer les dossiers nécessaires ─────────────────────────────────────────
RUN mkdir -p logs \
             static/uploads \
             models/yolo \
             results/videos \
             results/images \
             results/plots \
             data/raw_videos

# ── Permissions ─────────────────────────────────────────────────────────────
RUN chmod -R 777 logs static/uploads results

# ── Port HuggingFace (obligatoire) ─────────────────────────────────────────
EXPOSE 7860

# ── Lancer l'application ────────────────────────────────────────────────────
CMD ["python", "app.py"]