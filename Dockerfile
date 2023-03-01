# Start with a base image containing the JRE
FROM openjdk:11-jre-slim

# Install Python 3.9 + pip
RUN apt-get update && \
    apt-get install -y python3.9 && \
    apt-get install -y python3-pip && \
    apt-get install -y git && \
    apt-get install -y unzip && \
    apt-get clean
 

COPY requirements.txt ./
RUN python3 -m pip install -r requirements.txt

    
WORKDIR /app
COPY ./srcc ./srcc

RUN which python3

RUN cd srcc/ && git clone https://github.com/pablo-martin/SmartEmbed.git
RUN cd srcc/SmartEmbed/ && bash download_models.sh && cd ../..

# Set the command to run the Python script
CMD ["python3", "-u", "srcc/savior.py"]