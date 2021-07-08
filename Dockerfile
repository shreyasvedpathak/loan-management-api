FROM python:alpine3.8 
WORKDIR /app
ADD . /app
EXPOSE 5000
RUN pip install -r requirements.txt
CMD [ "python", "run.py" ]