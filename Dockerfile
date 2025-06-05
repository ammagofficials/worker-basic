FROM python:3.10-slim

# Install espeak-ng (required by kokoro)
RUN apt-get update && \
    apt-get install -y espeak-ng && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

COPY rp_handler.py /

CMD ["python3", "-u", "rp_handler.py"]
