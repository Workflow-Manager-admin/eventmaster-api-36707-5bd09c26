#!/bin/bash
cd /home/kavia/workspace/code-generation/eventmaster-api-36707-5bd09c26/eventmaster_api
./venv/bin/flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi
