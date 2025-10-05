FROM python:3.11-alpine

# Imposta variabili di ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Installa dipendenze di sistema per TA-Lib e MT5
RUN apk update && apk upgrade && apk add --no-cache \
    build-base \
    wget \
    curl \
    git \
    libffi-dev \
    openssl-dev \
    linux-headers

# Installa TA-Lib
RUN cd /tmp && \\
    wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \\
    tar -xzf ta-lib-0.4.0-src.tar.gz && \\
    cd ta-lib/ && \\
    ./configure --prefix=/usr && \\
    make && \\
    make install && \\
    cd .. && \\
    rm -rf ta-lib ta-lib-0.4.0-src.tar.gz

# Installa Poetry
RUN pip install poetry==1.7.1

# Crea directory di lavoro
WORKDIR /app

# Copia file di configurazione Poetry
COPY pyproject.toml poetry.lock* ./

# Configura Poetry per non creare virtual environment
RUN poetry config virtualenvs.create false

# Installa dipendenze
RUN poetry install --no-interaction --no-ansi --no-root

# Copia il codice dell'applicazione
COPY . .

# Crea directory per i log
RUN mkdir -p /app/logs

# Comando di default
CMD ["python", "src/main.py"]