FROM python:3.10

# Cài thư viện hệ thống
RUN apt-get update && apt-get install -y \
    curl \
    gnupg2 \
    apt-transport-https \
    unixodbc-dev \
    gcc \
    g++ \
    libgssapi-krb5-2

# Thêm Microsoft APT repo để cài driver ODBC 17
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Cài SQL Server ODBC Driver 17
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y \
    msodbcsql17

WORKDIR /app

COPY app /app
COPY app/config /app/config
COPY app/routes /app/routes

RUN touch .env

COPY app/controller /app/controller

RUN pip install -r requirements.txt

EXPOSE 8000

#CMD ["python", "app.py"]

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]