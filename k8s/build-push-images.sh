#!/bin/bash

# Defina suas variáveis
ACR_NAME=qfieldcloudacr
RESOURCE_GROUP=qfieldcloud-rg

# Faça login no ACR
az acr login --name $ACR_NAME

# Construa e envie as imagens
# App
docker build -t $ACR_NAME.azurecr.io/qfieldcloud-app:latest -f ./docker-app/Dockerfile ./docker-app
docker push $ACR_NAME.azurecr.io/qfieldcloud-app:latest

# Nginx
docker build -t $ACR_NAME.azurecr.io/qfieldcloud-nginx:latest -f ./docker-nginx/Dockerfile ./docker-nginx
docker push $ACR_NAME.azurecr.io/qfieldcloud-nginx:latest

# QGIS
docker build -t $ACR_NAME.azurecr.io/qfieldcloud-qgis:latest -f ./docker-qgis/Dockerfile ./docker-qgis
docker push $ACR_NAME.azurecr.io/qfieldcloud-qgis:latest

# Worker Wrapper (usando a mesma imagem do app mas com target diferente)
docker build -t $ACR_NAME.azurecr.io/qfieldcloud-worker-wrapper:latest --target worker_wrapper_runtime -f ./docker-app/Dockerfile ./docker-app
docker push $ACR_NAME.azurecr.io/qfieldcloud-worker-wrapper:latest

echo "Todas as imagens foram construídas e enviadas para o ACR"
