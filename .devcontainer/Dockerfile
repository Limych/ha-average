ARG BUILD_FROM BUILD_FROM_TAG
FROM python:3.11-slim

ENV DEVCONTAINER=true

COPY ./container /container
COPY ./install /install

ARG OS_VARIANT CONTAINER_TYPE
RUN \
    bash /install/init.sh \
    && bash /install/container.sh \
    && bash /install/integration.sh \
    && bash /install/cleanup.sh

CMD ["bash"]
