FROM python:3.9
RUN apt update && apt install git iproute2 iptables curl unzip sudo -y
RUN pip install --upgrade pip
RUN pip install poetry pytest
WORKDIR /code
RUN mkdir vpnmd tests
COPY pyproject.toml .
COPY poetry.lock .
COPY vpnmd vpnmd
COPY tests tests
RUN rm -rf vpnm/__pycache__
RUN rm -rf tests/__pycache__
RUN poetry export -f requirements.txt --output requirements.txt
RUN pip install -r requirements.txt
RUN curl -L https://github.com/xjasonlyu/tun2socks/releases/latest/download/tun2socks-linux-amd64.zip --output tun2socks-linux-amd64.zip
RUN sudo unzip -d /usr/local/bin tun2socks-linux-amd64.zip
CMD ["pytest", "-v"]