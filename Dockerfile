FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*
COPY . .
RUN pip3 install -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "main.py"]

