FROM  debian:buster-slim AS base
ARG APP_TAR
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
RUN apt-get update --yes && \
    apt-get install --yes curl  && \
    curl -OL https://github.com/jgm/pandoc/releases/download/2.13/pandoc-2.13-1-amd64.deb && \
    dpkg -i \pandoc-2.13-1-amd64.deb  && \
    rm -f pandoc-2.13-1-amd64.deb && \
    rm -rf /var/lib/apt/lists/*

FROM base as intermediate
RUN adduser --disabled-password --gecos '' app
WORKDIR /app
COPY --chown=app:app dist/$APP_TAR /app
RUN tar -xvf $APP_TAR  && rm -f $APP_TAR  && chown -R app /app/yanom


FROM base
RUN adduser --disabled-password --gecos '' app
WORKDIR /app/yanom
ENV PATH="/app/yanom:${PATH}"
COPY --from=intermediate /app/yanom /app/yanom
USER app
CMD bash