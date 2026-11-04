FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV PYTHONPATH=/app

COPY agent/requirements.txt agent/requirements.txt
RUN pip install --no-cache-dir -r agent/requirements.txt

# Guardrails AI turns on "hub telemetry" by default, which ships OpenTelemetry
# spans to a third-party AWS endpoint on every validation. This project is
# local-only, so it's disabled at the image level (read on import).
RUN printf 'enable_metrics=false\nuse_remote_inferencing=false\n' > /root/.guardrailsrc

CMD ["uvicorn", "agent.main:app", "--host", "0.0.0.0", "--port", "8000"]
