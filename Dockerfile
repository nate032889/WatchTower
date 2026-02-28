FROM python
LABEL authors="Nate"

WORKDIR /app
COPY . .
RUN ls -lisa && pip install -r requirements.txt

EXPOSE 8000
ENTRYPOINT ["uvicorn", "watchtower.asgi:application", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "debug"]