#!/bin/bash

# Definir variáveis
RESOURCE_GROUP=qfieldcloud-rg
LOCATION=eastus
CLUSTER_NAME=qfieldcloud-aks
ACR_NAME=qfieldcloudacr
NODE_COUNT=3
VM_SIZE=Standard_DS3_v2

# Criar cluster AKS
az aks create \
    --resource-group $RESOURCE_GROUP \
    --name $CLUSTER_NAME \
    --node-count $NODE_COUNT \
    --node-vm-size $VM_SIZE \
    --enable-addons monitoring \
    --generate-ssh-keys \
    --network-plugin azure \
    --enable-managed-identity

# Anexar o ACR ao AKS para permitir acesso às imagens
az aks update \
    --resource-group $RESOURCE_GROUP \
    --name $CLUSTER_NAME \
    --attach-acr $ACR_NAME

# Obter credenciais para o kubectl
az aks get-credentials \
    --resource-group $RESOURCE_GROUP \
    --name $CLUSTER_NAME

echo "Cluster AKS criado e configurado com sucesso!"
