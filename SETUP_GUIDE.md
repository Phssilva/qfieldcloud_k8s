# QField Cloud - Guia de Configuração

Este guia fornece instruções detalhadas para configurar o QField Cloud, garantindo que todas as funcionalidades, incluindo o download de projetos QGIS no aplicativo QField mobile, funcionem corretamente.

## Pré-requisitos

- Docker e Docker Compose instalados
- Git
- Acesso à internet para baixar imagens Docker
- Um editor de texto para modificar arquivos de configuração

## Passos para Configuração

### 1. Clone o Repositório

```bash
git clone --recurse-submodules git@github.com:opengisch/QFieldCloud.git
cd QFieldCloud
```

### 2. Configure o Arquivo .env

Copie o arquivo de exemplo para criar seu próprio arquivo de configuração:

```bash
cp .env.example .env
```

Edite o arquivo `.env` para configurar as variáveis de ambiente necessárias:

```bash
# Configurações básicas
ENVIRONMENT=development
QFIELDCLOUD_HOST=localhost
DJANGO_SETTINGS_MODULE=qfieldcloud.settings

# Configurações de banco de dados
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=qfieldcloud

# Configurações de e-mail
EMAIL_HOST=smtp4dev
EMAIL_PORT=25
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_USE_TLS=False
DEFAULT_FROM_EMAIL=info@qfield.cloud

# Configurações de armazenamento
STORAGE_ACCESS_KEY_ID=minioadmin
STORAGE_SECRET_ACCESS_KEY=minioadmin
STORAGE_BUCKET_NAME=qfieldcloud
STORAGE_REGION_NAME=
STORAGE_ENDPOINT_URL=http://minio:9000

# Configurações críticas para o funcionamento do worker
WORKER_QGIS_MEMORY_LIMIT=1g
QFIELDCLOUD_DEFAULT_NETWORK=qfieldcloud_default
QFIELDCLOUD_TRANSFORMATION_GRIDS_VOLUME_NAME=transformation_grids
QFIELDCLOUD_QGIS_IMAGE_NAME=qfieldcloud_qgis
```

### 3. Inicie os Serviços

```bash
docker-compose up -d
```

### 4. Verifique se Todos os Serviços Estão Rodando

```bash
docker-compose ps
```

Todos os serviços devem estar no estado "Up".

### 5. Crie um Superusuário (Administrador)

```bash
docker-compose exec app python manage.py createsuperuser
```

### 6. Acesse o Painel Administrativo

Abra seu navegador e acesse:

```
https://localhost:8002/admin/
```

Faça login com as credenciais do superusuário criado anteriormente.

## Solução de Problemas Comuns

### Problema: Falha no Download de Projetos no QField Mobile

Se você estiver enfrentando problemas ao baixar projetos no aplicativo QField mobile, verifique as seguintes configurações:

1. **Verifique a imagem QGIS**:
   ```bash
   docker images | grep qgis
   ```
   
   Certifique-se de que a imagem `qfieldcloud_qgis` existe. Se existir uma imagem com um nome diferente (por exemplo, com hífen em vez de underscore), atualize a variável `QFIELDCLOUD_QGIS_IMAGE_NAME` no arquivo `docker-compose.yml`:
   
   ```yaml
   QFIELDCLOUD_QGIS_IMAGE_NAME: ${QFIELDCLOUD_QGIS_IMAGE_NAME:-qfieldcloud_qgis}
   ```

2. **Verifique a configuração de rede**:
   Certifique-se de que a variável `QFIELDCLOUD_DEFAULT_NETWORK` está definida corretamente:
   
   ```bash
   QFIELDCLOUD_DEFAULT_NETWORK=qfieldcloud_default docker-compose up -d
   ```
   
   Ou adicione esta variável ao seu arquivo `.env`:
   
   ```
   QFIELDCLOUD_DEFAULT_NETWORK=qfieldcloud_default
   ```

3. **Verifique o limite de memória do worker QGIS**:
   Certifique-se de que a variável `WORKER_QGIS_MEMORY_LIMIT` está definida com um valor adequado:
   
   ```
   WORKER_QGIS_MEMORY_LIMIT=1g
   ```

4. **Verifique o volume de grades de transformação**:
   Certifique-se de que a variável `QFIELDCLOUD_TRANSFORMATION_GRIDS_VOLUME_NAME` está definida:
   
   ```
   QFIELDCLOUD_TRANSFORMATION_GRIDS_VOLUME_NAME=transformation_grids
   ```

### Problema: Erros nos Logs do Worker Wrapper

Se você estiver vendo erros nos logs do worker_wrapper, verifique-os com:

```bash
docker-compose logs worker_wrapper
```

Procure por mensagens de erro específicas e consulte a seção de solução de problemas acima para resolvê-las.

## Monitoramento e Logs

Para monitorar os logs dos serviços, use os seguintes comandos:

- **Worker Wrapper (processa downloads)**:
  ```bash
  docker-compose logs -f worker_wrapper
  ```

- **Aplicação Django**:
  ```bash
  docker-compose logs -f app
  ```

- **Banco de Dados**:
  ```bash
  docker-compose logs -f db
  ```

## Atualização

Para atualizar sua instalação do QField Cloud:

1. Pare os serviços:
   ```bash
   docker-compose down
   ```

2. Atualize o código-fonte:
   ```bash
   git pull --recurse-submodules && git submodule update --recursive
   ```

3. Reconstrua e inicie os serviços:
   ```bash
   docker-compose up -d --build
   ```

4. Execute migrações de banco de dados, se necessário:
   ```bash
   docker-compose exec app python manage.py migrate
   ```

## Gerenciamento de Usuários e Permissões de Projetos

O QField Cloud permite configurar permissões granulares para usuários, limitando o acesso a projetos específicos. Aqui está como fazer isso através da interface web:

### Criação de Usuários

1. Acesse o painel administrativo em `https://localhost:8002/admin/` (ou o endereço do seu servidor)
2. Faça login com as credenciais de administrador
3. Vá para `Usuários` na seção `AUTHENTICATION AND AUTHORIZATION`
4. Clique em `ADD USER` para criar um novo usuário
5. Preencha o nome de usuário e senha, depois clique em `SAVE`
6. Na próxima tela, preencha informações adicionais como e-mail, nome e sobrenome
7. Clique em `SAVE` novamente

### Criação de um Projeto

1. Acesse a interface principal do QField Cloud em `https://localhost:8002/`
2. Faça login com as credenciais de administrador
3. Clique em `New Project` para criar um novo projeto
4. Preencha as informações do projeto (nome, descrição, etc.)
5. Clique em `Create` para criar o projeto

### Configuração de Permissões de Projeto

1. Na página principal, localize o projeto que você deseja compartilhar
2. Clique no nome do projeto para abrir a página de detalhes
3. Clique na aba `Collaborators` (Colaboradores)
4. Clique em `Add collaborator` (Adicionar colaborador)
5. Digite o nome de usuário da pessoa que você deseja adicionar
6. Selecione o nível de permissão desejado:
   - `Reader`: Pode apenas visualizar e baixar o projeto
   - `Editor`: Pode editar o projeto, mas não pode gerenciar colaboradores
   - `Manager`: Pode editar o projeto e gerenciar colaboradores
   - `Owner`: Tem controle total sobre o projeto
7. Clique em `Add` para adicionar o usuário com as permissões especificadas

### Verificação de Acesso

1. Faça logout da conta de administrador
2. Faça login com as credenciais do usuário que você acabou de adicionar ao projeto
3. Verifique se o usuário pode ver apenas o projeto específico ao qual foi concedido acesso
4. Teste as permissões para garantir que o usuário tenha apenas os privilégios que você concedeu

Com essas configurações, você pode garantir que cada usuário tenha acesso apenas aos projetos específicos que precisam, mantendo os outros projetos privados e inacessíveis para eles.

## Recursos Adicionais

- [Documentação oficial do QField e QFieldCloud](https://docs.qfield.org)
- [Plataforma de ideias do QField](https://ideas.qfield.org)
- [Suporte para QField Cloud hospedado](https://tickets.qfield.cloud)
- [Problemas do GitHub para instalações auto-hospedadas](https://github.com/opengisch/qfieldcloud/issues)

## Conclusão

Seguindo este guia, você deve ter uma instalação funcional do QField Cloud que permite o download de projetos QGIS no aplicativo QField mobile, com gerenciamento adequado de usuários e permissões. Se você encontrar problemas adicionais, consulte os logs dos serviços relevantes e a documentação oficial.
