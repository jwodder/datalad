FROM neurodebian:latest
MAINTAINER DataLad developers

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y --no-install-recommends eatmydata && \
    eatmydata apt-get install -y --no-install-recommends gnupg locales && \
    echo "en_US.UTF-8 UTF-8" >>/etc/locale.gen && locale-gen && \
    eatmydata apt-get install -y --no-install-recommends \
      git git-annex-standalone datalad p7zip rsync openssh-server && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN git config --system user.name "Docker Datalad" && \
    git config --system user.email "docker-datalad@example.com"

RUN sed -ri \
      -e 's/^#?PermitRootLogin\s+.*/PermitRootLogin yes/' \
      -e 's/UsePAM yes/#UsePAM yes/g' \
      /etc/ssh/sshd_config && \
    mkdir -p /var/run/sshd
EXPOSE 22
