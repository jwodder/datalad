#!/bin/bash

mkdir -p "$HOME/.ssh"

cat >>"$HOME/.ssh/config" <<'EOF'

Host datalad-test
HostName localhost
Port 42241
User dl
StrictHostKeyChecking no
IdentityFile /tmp/dl-test-ssh-id
EOF

cat >>"$HOME/.ssh/config" <<'EOF'

Host datalad-test2
HostName localhost
Port 42242
User dl
StrictHostKeyChecking no
IdentityFile /tmp/dl-test-ssh-id
EOF

ssh-keygen -f /tmp/dl-test-ssh-id -N ""

# TODO: Once the base image is hosted somewhere, change this to
#
#   ./setup --key=/tmp/dl-test-ssh-id.pub -2 --from=BASE-IMAGE-NAME
(
    cd tools/ci/docker-ssh
    ./setup --key=/tmp/dl-test-ssh-id.pub -2
)

# FIXME: This is hacky and likely too long, but we need to sleep at least a
# little.
sleep 8
ssh -v datalad-test exit
ssh -v datalad-test2 exit
