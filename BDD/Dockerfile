FROM mysql:8.3.0

COPY ./init.sql /tmp

CMD [ "mysqld", "--init-file=/tmp/init.sql" ]