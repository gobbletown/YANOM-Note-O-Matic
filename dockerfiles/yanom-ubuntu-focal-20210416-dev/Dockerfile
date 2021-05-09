FROM ubuntu:focal-20210416
RUN apt update --yes && \
    apt install --yes curl  && \
    curl -OL https://github.com/jgm/pandoc/releases/download/2.13/pandoc-2.13-1-amd64.deb && \
    dpkg -i \pandoc-2.13-1-amd64.deb  && \
    rm -f pandoc-2.13-1-amd64.deb && \
    rm -rf /var/lib/apt/lists/*
RUN apt update && \
    apt -y install nano python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*
RUN adduser --disabled-password --gecos '' app
RUN mkdir -p /app/yanom && chown app /app/yanom && mkdir -p /app/yanom/data &&  chown app /app/yanom/data && \
    chown -R app /app
WORKDIR /app
RUN pip3 install --no-cache-dir pyinstaller
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt
COPY --chown=app:app . .
RUN python3 setup.py install && \
    pip3 install -e .
USER app
ENV PATH="/app/yanom:${PATH}"
COPY --chown=app:app dockerfiles/yanom-ubuntu-focal-20210416-dev/yanom.spec /app/src/
RUN cd src && \
    rm -rf /app/src/dist && rm -rf /app/src/build && \
    pyinstaller yanom.spec  && \
    cp /app/src/dist/yanom /app/yanom/ && \
    cp /app/src/data/config.ini /app/yanom/ && \
    cd /app && \
    tar -zcvf yanom1.0.0-ubuntu-focal-20.04.tar.gz yanom
WORKDIR /app/yanom
CMD bash
