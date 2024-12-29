#!/usr/bin/env bash

set -e

GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}Generating coverage report...${NC}"
pytest --cov --cov-report=html --cov-report=term-missing