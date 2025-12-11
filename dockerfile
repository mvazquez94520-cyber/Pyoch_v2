FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip
RUN [ -f requirements.txt ] && pip install -r requirements.txt || echo "Pas de requirements.txt trouvé"

EXPOSE 8000

CMD ["python", "pyoch_prototype.py"]
