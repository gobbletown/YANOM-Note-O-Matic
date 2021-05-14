FROM python:3.9.4-slim-buster
ARG APP_TAR
RUN adduser --disabled-password --gecos '' app
RUN apt-get update --yes && apt-get install --yes binutils && apt-get install --yes nano && apt-get install
WORKDIR /app
RUN mkdir -p /app/yanom && chown app /app/yanom && mkdir -p /app/yanom/data &&  chown app /app/yanom/data
RUN pip install --no-cache-dir pyinstaller
COPY --chown=app:app . .
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=app:app dockerfiles/yanom-dev-deb10-slim-buster/yanom.spec /app/src/
RUN cd src && \
    rm -rf /app/src/dist && rm -rf /app/src/build && \
    pyinstaller yanom.spec  && \
    cp /app/src/dist/yanom /app/yanom/ && \
    cp /app/src/data/config.ini /app/yanom/data && \
    cd /app && \
    chown -R app yanom
RUN tar -zcvf $APP_TAR yanom
USER app
CMD bash
