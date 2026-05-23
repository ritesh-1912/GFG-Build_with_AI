FROM python:3.12-slim

WORKDIR /app

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uv/bin/
ENV PATH="/uv/bin:${PATH}"

# Install dependencies
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# Copy source code
COPY . .

# Ensure static directories exist
RUN mkdir -p static/cards

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
