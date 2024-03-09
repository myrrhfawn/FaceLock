# set base image (host OS)
FROM python:3.10

# set the working directory in the container
# set the working directory in the container
WORKDIR /

COPY server /server
COPY fl_utils /fl_utils
COPY /docker/requirements.txt requirements.txt
RUN pip install -r requirements.txt

# copy the entire FaceLock directory into the container

# install dependencies
#RUN pip install -r requirements.txt
EXPOSE 9000
# command to run on container start
WORKDIR /server

CMD ["python", "run.py"]
