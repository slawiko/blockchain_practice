FROM python:3.6-alpine

RUN apk --no-cache --update add gcc musl-dev make

ENV NODEUSER=nodeuser \
    NODEGROUP=nodegroup \
    NODE_DIR=/node

RUN addgroup -S ${NODEGROUP} && \
    adduser -S ${NODEUSER} -G ${NODEGROUP} && \
    mkdir $NODE_DIR && \
    chown ${NODEUSER}:${NODEGROUP} $NODE_DIR
USER ${NODEUSER}

WORKDIR $NODE_DIR

# docker layers caching usage
COPY ./requirements.txt ./
RUN pip install --user -r ./requirements.txt --no-cache-dir

COPY --chown=nodeuser:nodegroup ./ ./

EXPOSE 8081 8765
ENTRYPOINT ["./run-seed-node.sh"]
