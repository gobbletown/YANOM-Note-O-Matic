FROM ubuntu:focal-20210416
RUN apt update && \
    apt -y install nano python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*
RUN adduser --disabled-password --gecos '' app
RUN mkdir -p /app/yanom && chown app /app/yanom && mkdir -p /app/yanom/data &&  chown app /app/yanom/data && \
    chown -R app /app
WORKDIR /app
RUN pip3 install --no-cache-dir pyinstaller
COPY requirements.txt setup.py ./
RUN pip3 install --no-cache-dir -r requirements.txt
COPY --chown=app:app . .
RUN python3 setup.py install
RUN pip3 install -e .
USER app
ENV PATH="/home/app/.local/bin:${PATH}"
COPY --chown=app:app dockerfiles/yanom-ubuntu-focal-20210416-dev/yanom.spec /app/src/
RUN cd src && \
    rm -rf /app/src/dist && rm -rf /app/src/build && \
    pyinstaller yanom.spec  && \
    cp /app/src/dist/yanom /app/yanom/ && \
    cp /app/src/data/config.ini /app/yanom/ && \
    cd /app && \
    tar -zcvf yanom1-ubuntu-focal-20.04.tar.gz yanom
CMD bash
