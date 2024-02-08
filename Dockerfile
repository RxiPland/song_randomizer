FROM python:3.11

WORKDIR /certs
WORKDIR /app

# Copy files
COPY templates ./templates/
COPY requirements.txt .
COPY main.py .

RUN pip install -r requirements.txt

EXPOSE 443

ENTRYPOINT ["python", "main.py"]
