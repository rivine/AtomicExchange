FROM ubuntu:16.04
#FROM ubuntu:16.04

RUN apt-get update && apt-get install -y \
 	curl \
 	apt-transport-https \
    software-properties-common \
    wget

RUN wget -qO - https://openresty.org/package/pubkey.gpg |  apt-key add -
RUN  add-apt-repository -y "deb http://openresty.org/package/ubuntu $(lsb_release -sc) main"
RUN apt-get update
RUN apt-get install -y openresty 


COPY Routes /usr/local/openresty/nginx/conf/Routes
COPY nginx.conf /usr/local/openresty/nginx/conf/nginx.conf
WORKDIR /home/app
CMD /usr/local/openresty/nginx/sbin/nginx -g "daemon off;"