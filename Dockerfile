FROM python:3.8.10

COPY ./ /webapp/python_project
WORKDIR /webapp/python_project

RUN pip install -r requirements.txt

CMD ["python3", "/webapp/python_project/server.py"]
