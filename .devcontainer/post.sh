#!/usr/bin/env bash
set -e

pip --disable-pip-version-check --no-cache-dir install --user poetry
poetry install --no-root
