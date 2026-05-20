FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir pyfunda pypararius

COPY utils.py .
COPY funda_script.py .
COPY pararius_script.py .
COPY main.py .

# Seen-listings files are stored here; mount a volume to persist between runs
VOLUME ["/data"]

CMD ["python", "main.py"]
