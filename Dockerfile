FROM python:3.12.3
WORKDIR /usr/src/app
COPY requirements.txt  ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD [ "uvicorn", "Server:manager.connect", "--host", "0.0.0.0", "--port", "8000" ]
