#!/bin/bash
set -e
aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin 981814817456.dkr.ecr.eu-west-1.amazonaws.com
docker pull 981814817456.dkr.ecr.eu-west-1.amazonaws.com/bethuel-portfolio:latest
docker run -d --name bethuel-portfolio -p 8000:8000 981814817456.dkr.ecr.eu-west-1.amazonaws.com/bethuel-portfolio:latest
