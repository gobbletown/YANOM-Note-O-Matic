FROM  debian:buster-slim AS base
RUN apt-get update --yes && \
    apt-get install --yes curl  && \
    curl -OL https://github.com/jgm/pandoc/releases/download/2.13/pandoc-2.13-1-amd64.deb && \
    dpkg -i \pandoc-2.13-1-amd64.deb  && \
    rm -f pandoc-2.13-1-amd64.deb && \
    rm -rf /var/lib/apt/lists/*

FROM base as intermediate
RUN adduser --disabled-password --gecos '' app
WORKDIR /app
COPY --chown=app:app dist/yanom1.0.0-debian10-slim-buster.tar.gz /app
RUN tar -xvf yanom1.0.0-debian10-slim-buster.tar.gz && rm -f yanom1.0.0-debian10-slim-buster.tar.gz  && chown -R app /app/yanom


FROM base
RUN adduser --disabled-password --gecos '' app
WORKDIR /app/yanom
ENV PATH="/app/yanom:${PATH}"
COPY --from=intermediate /app/yanom /app/yanom
USER app
CMD bash