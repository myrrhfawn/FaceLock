# set base image (host OS)
FROM python:3.10

# Avoid debconf prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies for dlib
RUN apt update && apt install -y --no-install-recommends \
    cmake \
    git \
    curl \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*

# Clone dlib repo
WORKDIR /opt
RUN git clone https://github.com/davisking/dlib.git
# Install python extension
RUN cd dlib && python3 setup.py install

# Optional: set working directory
WORKDIR /app

# Copy project folder
COPY . /app

# Install python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Set workdir and command
WORKDIR /app
EXPOSE 9000
CMD ["python", "run.py"]
