FROM debian:bullseye

# Install pyenet from apt
RUN apt-get update && apt-get install -y \
    python3 \
    python3-enet \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

RUN pip install --no-cache-dir \
    redis

COPY . .
CMD [ "python3", "main.py" ]