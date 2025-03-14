# base image
FROM 192.168.31.6:7001/python:3.10-slim-bookworm AS base

# Install the necessary system packages
FROM base AS packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        libc-dev \
        libffi-dev \
        libgmp-dev \
        libmpfr-dev \
        libmpc-dev \
        curl \
        wget \
        vim \
        nodejs \
        ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements.txt file into the container
COPY requirements.txt /requirements.txt

# Leverage the cache to install Python packages
RUN pip install --no-cache-dir -r /requirements.txt --prefix=/pkg

FROM base AS production

ENV EDITION SELF_HOSTED
ENV DEPLOY_ENV PRODUCTION
ENV TZ UTC

# Set the time zone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Expose the port
EXPOSE 9999

ENTRYPOINT ["python", "run.py"]
