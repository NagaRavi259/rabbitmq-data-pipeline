FROM rabbitmq:3-management

RUN rabbitmq-plugins enable rabbitmq_management

RUN rabbitmq-plugins enable rabbitmq_mqtt

COPY rabbitmq.conf /etc/rabbitmq/