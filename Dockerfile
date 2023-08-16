FROM python:3.8
ENV PROJECT_ROOT /app
ENV IS_DOCKER 1

RUN addgroup --gid 9999 maniaplanet && \
    adduser -u 9999 --group maniaplanet --system

RUN apt-get -q update \
&& apt-get install -y build-essential libssl-dev libffi-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Create project root.
RUN mkdir -p $PROJECT_ROOT
WORKDIR $PROJECT_ROOT
ADD ./ $PROJECT_ROOT/
COPY docs/docker/root/base.py $PROJECT_ROOT/base.py
RUN chown -R maniaplanet:maniaplanet $PROJECT_ROOT

# Install PyPlanet.
RUN pip install -r requirements.txt
RUN pip install -r require_docker.txt
RUN chmod +x cli.py

USER maniaplanet

# Init project.

RUN ./cli.py init_project server
WORKDIR $PROJECT_ROOT/server/
RUN cp ../base.py $PROJECT_ROOT/server/settings/base.py
RUN chmod +x $PROJECT_ROOT/server/manage.py

VOLUME $PROJECT_ROOT/server/
ENV PYTHONPATH="/app:/app/server"

ENTRYPOINT [ "python", "manage.py" ]
CMD [ "start", "--pool=default", "--settings=settings" ]
