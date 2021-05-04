FROM python:3.9.4-slim-buster
RUN adduser --disabled-password --gecos '' app
RUN apt-get update --yes && apt-get install --yes binutils
WORKDIR /app
COPY --chown=app:app . .
USER app
RUN pip install --no-cache-dir -r requirements.txt && \ 
	export PATH="/home/app/.local/bin:$PATH"
CMD bash