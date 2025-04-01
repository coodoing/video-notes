FROM python:3.9-slim

WORKDIR /app
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ffmpeg
#    apt-get clean && \
#    pip cache purge && \
#    rm -rf /var/lib/apt/lists/*
RUN useradd --create-home zhuyan

WORKDIR /home/zhuyan
USER zhuyan

COPY --chown=zhuyan:zhuyan requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt
#    pip cache purge
COPY --chown=zhuyan:zhuyan ./core ./app

WORKDIR /home/zhuyan/app
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]