#!/bin/bash

# Obter o nome do primeiro pod da aplicação
APP_POD=$(kubectl get pods -n qfieldcloud -l app=qfieldcloud-app -o jsonpath="{.items[0].metadata.name}")

echo "Executando migrações do Django..."
kubectl exec -it $APP_POD -n qfieldcloud -- python manage.py migrate

echo "Coletando arquivos estáticos..."
kubectl exec -it $APP_POD -n qfieldcloud -- python manage.py collectstatic --noinput

echo "Criando superusuário (você precisará inserir as credenciais)..."
kubectl exec -it $APP_POD -n qfieldcloud -- python manage.py createsuperuser

echo "Inicialização da aplicação concluída!"
