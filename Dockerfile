FROM python:3.11-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip uv
RUN uv pip install --system --no-cache-dir -r requirements.txt
RUN python -m playwright install --with-deps chromium

COPY . .

CMD ["pytest", "-vs"]
