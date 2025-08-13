FROM python:3.13.3

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install pip --upgrade \
    && pip install -r requirements.txt

COPY . .


EXPOSE 8000

CMD ["python", "project/manage.py", "runserver", "0.0.0.0:8000"]
