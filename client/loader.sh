#!/usr/bin/env bash

# Assumes a virtual environment - all required packages - and the
# codebase are installed when we distributed the bespoke artefact.
cd $HOME/acr/ && source venv/bin/activate && python client.py