FROM python:3.12-slim

WORKDIR /app

# Health check uses curl - install it
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
COPY server.py cli.py prompts.py benchmarks.py output.py conversation.py litellm_backend.py executor.py ./
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 9009

# Default command - leaderboard expects --host 0.0.0.0 --port 9009 --card-url http://<name>:9009
ENTRYPOINT ["python", "server.py"]
CMD ["--host", "0.0.0.0", "--port", "9009"]
