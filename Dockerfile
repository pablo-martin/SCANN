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
COPY ./src ./src
# set up embedding repo and download models
RUN cd src/ && git clone https://github.com/pablo-martin/SmartEmbed.git
RUN cd src/SmartEmbed/ && bash download_models.sh

RUN cd src/ && gdown https://drive.google.com/uc?id=1t6l_6OyYjYFw84CLXrx6SYft7FDdNYfy
RUN cd src/ && mkdir tables/ && cd tables/ && gdown  https://drive.google.com/uc?id=1IXO2Xz4wBG9S-eCmYdvkrKVYY01rR_C-

EXPOSE 5000
CMD ["python3", "-u", "src/app.py"]