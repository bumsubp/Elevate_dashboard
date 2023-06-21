FROM python:3.8

ENV http_proxy http://internet.ford.com:83
ENV https_proxy http://internet.ford.com:83
ENV NO_PROXY=".ford.com,localhost,127.0.0.0"

WORKDIR /app
COPY app.py .
copy logo.png .
COPY requirements.txt .
COPY pkg/ ./pkg/
COPY OverviewFigures ./OverviewFigures/
RUN export PYTHONPATH=/app/

RUN pip3 install --no-cache-dir -r requirements.txt
#run ls -la /pages/*
RUN dir

EXPOSE 8000
ENV http_proxy=
ENV https_proxy=
ENV NO_PROXY=

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8000", "--server.address=0.0.0.0"]
