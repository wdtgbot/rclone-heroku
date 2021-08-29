FROM ubuntu
ADD src/ /src
WORKDIR /src

RUN apt-get update --fix-missing     && apt-get -y install wget  && apt-get -y install screen    && mkdir \src     && apt install -y python3 python3-pip
RUN pip3 install -r requirements.txt

CMD bash /src/start.sh
    