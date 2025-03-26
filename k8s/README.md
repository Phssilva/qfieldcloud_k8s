# QField Cloud no Azure Kubernetes Service (AKS)

Este guia descreve como implantar o QField Cloud em um cluster Kubernetes no Azure (AKS).

## Pré-requisitos

- Azure CLI instalado e configurado
- kubectl instalado
- Docker instalado
- Helm instalado (para o Cert-Manager)
- Uma assinatura ativa do Azure

## Estrutura de Arquivos

```
k8s/
├── namespace.yaml            # Define o namespace Kubernetes
├── configmap.yaml            # Configurações não-sensíveis
├── secrets.yaml              # Informações sensíveis (senhas, chaves)
├── storage.yaml              # Persistent Volume Claims
├── postgres.yaml             # Banco de dados PostgreSQL
├── app.yaml                  # Aplicação Django principal
├── worker-wrapper.yaml       # Serviço de processamento de tarefas
├── qgis.yaml                 # Serviço QGIS
├── nginx.yaml                # Servidor web e Ingress
├── build-push-images.sh      # Script para construir e enviar imagens
├── create-aks-cluster.sh     # Script para criar o cluster AKS
├── setup-ingress-certmanager.sh # Configuração de Ingress e certificados
├── deploy.sh                 # Script de implantação
└── initialize-app.sh         # Inicialização da aplicação
```

## Passos para Implantação

### 1. Preparar o Ambiente Azure

Execute o script para criar o cluster AKS e o Azure Container Registry:

```bash
chmod +x k8s/create-aks-cluster.sh
./k8s/create-aks-cluster.sh
```

### 2. Construir e Enviar as Imagens Docker

Execute o script para construir e enviar as imagens Docker para o ACR:

```bash
chmod +x k8s/build-push-images.sh
./k8s/build-push-images.sh
```

### 3. Configurar o Ingress Controller e o Cert-Manager

Execute o script para configurar o Application Gateway Ingress Controller e o Cert-Manager:

```bash
chmod +x k8s/setup-ingress-certmanager.sh
./k8s/setup-ingress-certmanager.sh
```

### 4. Implantar a Aplicação

Execute o script de implantação para aplicar todos os manifestos Kubernetes:

```bash
chmod +x k8s/deploy.sh
./k8s/deploy.sh
```

### 5. Inicializar a Aplicação

Execute o script de inicialização para configurar o banco de dados e criar um superusuário:

```bash
chmod +x k8s/initialize-app.sh
./k8s/initialize-app.sh
```

## Verificação da Implantação

Verifique se todos os pods estão em execução:

```bash
kubectl get pods -n qfieldcloud
```

Verifique os serviços:

```bash
kubectl get services -n qfieldcloud
```

Verifique o Ingress:

```bash
kubectl get ingress -n qfieldcloud
```

## Acessando a Aplicação

Após a implantação bem-sucedida, você pode acessar a aplicação através do domínio configurado no Ingress (por padrão, `qfieldcloud.example.com`). Certifique-se de configurar o DNS para apontar para o endereço IP do Application Gateway.

## Solução de Problemas

### Verificando Logs

Para verificar os logs de um pod específico:

```bash
kubectl logs -f <nome-do-pod> -n qfieldcloud
```

### Reiniciando um Serviço

Para reiniciar um deployment:

```bash
kubectl rollout restart deployment <nome-do-deployment> -n qfieldcloud
```

### Acessando um Pod

Para acessar um shell em um pod:

```bash
kubectl exec -it <nome-do-pod> -n qfieldcloud -- /bin/bash
```

## Manutenção

### Atualizando a Aplicação

Para atualizar a aplicação, reconstrua as imagens Docker com novas tags, envie-as para o ACR e atualize os deployments:

```bash
# Exemplo para atualizar a aplicação principal
docker build -t qfieldcloudacr.azurecr.io/qfieldcloud-app:v2 -f ./docker-app/Dockerfile ./docker-app
docker push qfieldcloudacr.azurecr.io/qfieldcloud-app:v2

kubectl set image deployment/qfieldcloud-app app=qfieldcloudacr.azurecr.io/qfieldcloud-app:v2 -n qfieldcloud
```

### Escalando a Aplicação

Para escalar horizontalmente um serviço:

```bash
kubectl scale deployment qfieldcloud-app --replicas=4 -n qfieldcloud
```
