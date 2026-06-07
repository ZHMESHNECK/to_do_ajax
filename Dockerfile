FROM jenkins/jenkins:lts

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-venv \
        docker.io \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Allow jenkins user to call docker CLI via the mounted socket
RUN groupadd -f docker && usermod -aG docker jenkins

USER jenkins