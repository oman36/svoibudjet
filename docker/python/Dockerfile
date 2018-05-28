FROM debian:stretch-slim

RUN apt update
RUN apt install -yq vim
RUN apt install -yq python3
RUN apt install -yq python3-setuptools
RUN apt install -yq python3-pip

RUN pip3 install click==6.7
RUN pip3 install cryptography==1.7.1
RUN pip3 install Flask==1.0.2
RUN pip3 install idna==2.2
RUN pip3 install itsdangerous==0.24
RUN pip3 install Jinja2==2.10
RUN pip3 install keyring==10.1
RUN pip3 install keyrings.alt==1.3
RUN pip3 install MarkupSafe==1.0
RUN pip3 install pyasn1==0.1.9
RUN pip3 install pycrypto==2.6.1
RUN pip3 install pygobject==3.22.0
RUN pip3 install pyxdg==0.25
RUN pip3 install SecretStorage==2.3.1
RUN pip3 install six==1.10.0
RUN pip3 install Werkzeug==0.14.1

RUN  export LC_ALL=C.UTF-8  LANG=C.UTF-8

CMD bash