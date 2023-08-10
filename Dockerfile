FROM python:3.9

EXPOSE 10000

WORKDIR /service

COPY . ./

RUN pip install -r dependences.txt

ENTRYPOINT ["uvicorn", "main_api:app", "--port", "10000", "--host", "0.0.0.0"]