FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install UV
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Copy project files
COPY pyproject.toml ./
COPY src ./src
COPY config ./config
COPY templates ./templates
COPY static ./static

# Install dependencies
RUN uv pip install --system -e .

# Create data directories
RUN mkdir -p data/papers data/images data/summaries

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "paper_review.web.app:app", "--host", "0.0.0.0", "--port", "8000"]
