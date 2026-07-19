FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "-m", "gunicorn", "-b", "0.0.0.0:10000", "main:app"]
