#!/bin/bash

# Definir variáveis
ACR_NAME=qfieldcloudacr  # Substitua pelo nome do seu ACR

# Substituir a variável ACR_NAME nos arquivos YAML
for file in ./k8s/*.yaml; do
  if grep -q "\${ACR_NAME}" "$file"; then
    sed -i "s/\${ACR_NAME}/$ACR_NAME/g" "$file"
    echo "Substituído ACR_NAME em $file"
  fi
done

# Aplicar os manifestos Kubernetes na ordem correta
echo "Criando namespace..."
kubectl apply -f ./k8s/namespace.yaml

echo "Aplicando ConfigMap e Secrets..."
kubectl apply -f ./k8s/configmap.yaml
kubectl apply -f ./k8s/secrets.yaml

echo "Criando recursos de armazenamento..."
kubectl apply -f ./k8s/storage.yaml

echo "Implantando banco de dados PostgreSQL..."
kubectl apply -f ./k8s/postgres.yaml

# Esperar o PostgreSQL ficar pronto
echo "Aguardando o PostgreSQL ficar pronto..."
kubectl wait --for=condition=ready pod -l app=qfieldcloud-postgres -n qfieldcloud --timeout=300s

echo "Implantando aplicação principal..."
kubectl apply -f ./k8s/app.yaml

echo "Implantando QGIS..."
kubectl apply -f ./k8s/qgis.yaml

echo "Implantando worker wrapper..."
kubectl apply -f ./k8s/worker-wrapper.yaml

echo "Implantando NGINX e Ingress..."
kubectl apply -f ./k8s/nginx.yaml

echo "Implantação concluída com sucesso!"
echo "Para verificar o status dos pods, execute: kubectl get pods -n qfieldcloud"
