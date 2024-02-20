# set base image (host OS)
FROM python:3.10

# set the working directory in the container
# set the working directory in the container
WORKDIR /

COPY server /server
COPY fl_utils /server/fl_utils

# copy the entire FaceLock directory into the container

# install dependencies
#RUN pip install -r requirements.txt
EXPOSE 9000
# command to run on container start
WORKDIR /server

CMD ["python", "server.py"]
