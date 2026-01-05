#!/bin/bash
set -e
docker stop bethuel-portfolio || true
docker rm bethuel-portfolio || true
