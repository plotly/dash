# The swarm agent: headless Chromium users driven by Playwright.
#   docker build -t dash-swarm-agent benchmarks/swarm
#   docker run --rm --init --ipc=host dash-swarm-agent --target http://app:8050 --users 50
# The playwright version must match the image tag.
FROM mcr.microsoft.com/playwright/python:v1.63.0-noble

RUN python3 -m pip install --no-cache-dir --break-system-packages "psutil>=7"
COPY agent.py histogram.py /swarm/
ENTRYPOINT ["python3", "/swarm/agent.py"]
