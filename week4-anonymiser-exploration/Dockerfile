FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copy project files
COPY pyproject.toml uv.lock ./
COPY anonymiser.py ./

# Install dependencies
RUN uv sync --frozen --no-cache

# Create data directory
RUN mkdir -p /app/data/mappings

# Expose port
EXPOSE 9000

# Run the application
CMD ["uv", "run", "uvicorn", "anonymiser:app", "--host", "0.0.0.0", "--port", "9000"]