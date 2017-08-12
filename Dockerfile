FROM python:3.6-stretch
ADD Makefile /var/tbg/Makefile
ADD requirements.txt /var/tbg/requirements.txt
ADD app /var/tbg/app
WORKDIR "/var/tbg/"
RUN ["pip", "install", "-r", "/var/tbg/requirements.txt"]
EXPOSE 8080
ENTRYPOINT ["make", "run"]