#!/bin/bash
# Run on the box: ~/vallka/simply-blog/deploy/deploy.sh
set -e

export PATH=$HOME/.local/bin:$PATH
export UV_PROJECT_ENVIRONMENT=$HOME/vallka/venv UV_PYTHON_PREFERENCE=only-system

cd ~/vallka/simply-blog
git pull --ff-only
uv sync --frozen --no-dev
"$UV_PROJECT_ENVIRONMENT/bin/python" manage.py migrate --noinput
"$UV_PROJECT_ENVIRONMENT/bin/python" manage.py collectstatic --noinput
sudo systemctl restart vallka
systemctl is-active vallka
