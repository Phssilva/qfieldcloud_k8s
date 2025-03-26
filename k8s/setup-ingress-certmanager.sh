#!/bin/bash

# Definir variáveis
RESOURCE_GROUP=qfieldcloud-rg
CLUSTER_NAME=qfieldcloud-aks

# Instalar o Application Gateway Ingress Controller (AGIC)
echo "Instalando o AGIC..."
az aks enable-addons \
    --resource-group $RESOURCE_GROUP \
    --name $CLUSTER_NAME \
    --addons ingress-appgw \
    --appgw-name qfieldcloud-appgw \
    --appgw-subnet-cidr "10.225.0.0/16"

# Instalar o Cert-Manager via Helm
echo "Instalando o Cert-Manager..."
kubectl create namespace cert-manager
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm install cert-manager jetstack/cert-manager \
    --namespace cert-manager \
    --version v1.11.0 \
    --set installCRDs=true

# Aguardar a instalação do Cert-Manager
echo "Aguardando a instalação do Cert-Manager..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=cert-manager -n cert-manager --timeout=300s

# Criar um ClusterIssuer para Let's Encrypt
echo "Criando ClusterIssuer para Let's Encrypt..."
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: seu-email@exemplo.com  # Substitua pelo seu e-mail
    privateKeySecretRef:
      name: letsencrypt-key
    solvers:
    - http01:
        ingress:
          class: azure/application-gateway
EOF

echo "Configuração do Ingress Controller e Cert-Manager concluída!"
