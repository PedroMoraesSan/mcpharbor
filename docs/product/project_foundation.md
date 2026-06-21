# MCP Harbor

## Docker Desktop para MCPs

### Versão 0.1

### Documento Mestre do Projeto

**Autoria Técnica:** Pedro Moraes

---

# Visão do Produto

## O que é o MCP Harbor?

O MCP Harbor é uma plataforma desktop open source para gerenciamento, execução e integração de MCP Servers (Model Context Protocol).

Seu objetivo é transformar a experiência atual de utilização de MCPs em algo tão simples quanto instalar uma extensão do VSCode ou executar um container pelo Docker Desktop.

O usuário não deve precisar:

* Editar arquivos JSON
* Instalar dependências manualmente
* Configurar Docker manualmente
* Gerenciar processos localmente
* Descobrir caminhos de configuração de cada cliente

Toda a experiência deve ser guiada por interface gráfica.

---

# Visão de Longo Prazo

O MCP Harbor pretende se tornar a camada operacional padrão para o ecossistema MCP.

Assim como o Docker Desktop tornou containers acessíveis para milhões de desenvolvedores, o MCP Harbor pretende tornar MCPs acessíveis para qualquer usuário de IA.

---

# Missão

Permitir que qualquer pessoa instale, configure e utilize MCPs em menos de 2 minutos.

---

# Problema

Hoje o ecossistema MCP apresenta diversos problemas:

* Instalação complexa
* Dependência de terminal
* Configuração manual
* Falta de observabilidade
* Falta de gerenciamento centralizado
* Baixa acessibilidade para usuários não técnicos

---

# Solução

O MCP Harbor fornece:

* Catálogo de MCPs
* Instalação em um clique
* Gerenciamento de credenciais
* Gerenciamento de containers
* Integração automática com clientes MCP
* Monitoramento
* Logs
* Atualizações

---

# MVP

O MVP será considerado concluído quando o usuário conseguir:

Instalar um Github MCP

↓

Configurar credenciais

↓

Executar o MCP

↓

Conectar ao Cursor

↓

Utilizar o MCP

Sem abrir terminal.

Tempo máximo esperado:

Menos de 2 minutos.

---

# Público-Alvo

## Desenvolvedores

Utilizam:

* Cursor
* Claude Desktop
* OpenCode
* Cline

Necessitam:

* Instalação rápida
* Menos configuração
* Mais produtividade

---

## Usuários de IA

Necessitam:

* Conectar ferramentas
* Não aprender Docker
* Não editar JSON

---

# Requisitos Funcionais

## Catálogo de MCPs

### RF01

O sistema deve exibir um catálogo de MCPs disponíveis.

### RF02

Cada MCP deve apresentar:

* Nome
* Descrição
* Autor
* Versão
* Docker Image

### RF03

O sistema deve permitir instalação com um clique.

### RF04

O sistema deve impedir instalações duplicadas.

---

## Runtime

### RF05

O sistema deve executar MCPs através de containers Docker.

### RF06

O sistema deve permitir:

* Start
* Stop
* Restart

### RF07

O sistema deve exibir status em tempo real.

### RF08

O sistema deve permitir atualização do MCP.

---

## Credenciais

### RF09

O sistema deve permitir cadastro de credenciais.

### RF10

As credenciais devem ser armazenadas de forma segura.

### RF11

O sistema deve validar credenciais antes da execução.

---

## Logs

### RF12

O sistema deve exibir logs em tempo real.

### RF13

O sistema deve exibir:

* CPU
* RAM
* Status

### RF14

O sistema deve indicar falhas visualmente.

---

## Integrações

### RF15

Integração com Cursor.

### RF16

Integração com Claude Desktop.

### RF17

Integração com OpenCode.

### RF18

Integração com Cline.

---

# Requisitos Não Funcionais

### RNF01

Compatível com:

* Windows
* Linux
* MacOS

### RNF02

Inicialização inferior a 3 segundos.

### RNF03

Suportar pelo menos 20 MCPs simultaneamente.

### RNF04

Credenciais nunca podem ser armazenadas em texto plano.

---

# Decisão Arquitetural

## Estilo Arquitetural

Clean Architecture

Baseada em:

* Domain Driven Design
* SOLID
* CQRS leve
* Dependency Inversion

---

# Princípios

## Regra Principal

Dependências sempre apontam para dentro.

```text
Infrastructure
      ↓
Application
      ↓
Domain
```

O domínio não conhece:

* FastAPI
* Banco de dados
* Docker
* Interface gráfica

---

# Camadas

## Domain

Responsável por:

* Entidades
* Regras de negócio
* Value Objects
* Contratos

Não possui dependências externas.

---

## Application

Responsável por:

* Casos de uso
* Orquestração
* Regras de aplicação

Exemplos:

* InstallMCP
* StartMCP
* StopMCP
* UpdateMCP

---

## Infrastructure

Responsável por:

* PostgreSQL
* Docker
* Keyring
* Sistema Operacional
* Arquivos

---

## Presentation

Responsável por:

* FastAPI
* Controllers
* DTOs
* APIs

---

# Estrutura do Projeto

```text
backend/

src/

├── domain/
│
├── application/
│
├── infrastructure/
│
├── presentation/
│
├── shared/
│
└── main.py
```

---

# Stack Tecnológica

## Frontend

### React

Framework principal.

---

### Typescript

Tipagem completa.

---

### Vite

Build system.

---

### TailwindCSS

Estilização.

---

### shadcn/ui

Design System.

---

### TanStack Query

Gerenciamento de estado servidor.

---

### Zustand

Estado local.

---

# Desktop

## Tauri

Responsável por:

* Empacotamento
* Distribuição
* Comunicação Desktop

---

# Backend

## Python

Versão:

```text
Python 3.13+
```

---

## FastAPI

Framework principal.

---

## Pydantic

Validação.

---

## SQLAlchemy

ORM.

---

## Alembic

Migrations.

---

## Docker SDK

Gerenciamento de containers.

---

## Keyring

Gerenciamento seguro de credenciais.

---

# Banco de Dados

## PostgreSQL

Banco principal.

Motivos:

* Escalável
* Futuro MCP Harbor Cloud
* Excelente integração com SQLAlchemy

---

# Comunicação

Frontend

↓

REST API

↓

FastAPI

↓

Application Layer

↓

Infrastructure

---

# Padrões Obrigatórios

## SOLID

Todos os serviços devem respeitar SOLID.

---

## Repository Pattern

Todo acesso a dados deve passar por repositories.

Proibido:

```python
session.query(...)
```

diretamente dentro de use cases.

---

## Dependency Injection

Utilizar:

```python
Depends()
```

e container de dependências.

---

## DTO Pattern

Nunca retornar entidades do domínio diretamente.

Sempre utilizar DTOs.

---

## Result Pattern

Evitar Exceptions para fluxo de negócio.

Utilizar:

```python
Success()
Failure()
```

ou equivalente.

---

# Convenções

## Nome de Casos de Uso

```text
InstallMCPUseCase
StartMCPUseCase
StopMCPUseCase
```

---

## Nome de Repositories

```text
MCPRepository
CredentialRepository
```

---

## Nome de Services

```text
DockerService
RegistryService
SecretService
```

---

# Segurança

## Credenciais

Nunca armazenar:

* API Keys
* Tokens

em banco de dados.

Sempre utilizar:

* MacOS Keychain
* Windows Credential Manager
* Linux Secret Service

via Keyring.

---

## Logs

Nunca registrar:

* Tokens
* Segredos
* Credenciais

---

# Arquitetura de Runtime

```text
Frontend

React + Tauri

        ↓

FastAPI

        ↓

Application Layer

        ↓

Docker Manager

        ↓

Containers MCP
```

---

# Roadmap

## V1

* Catálogo
* Instalação
* Docker Runtime
* Credenciais
* Logs
* Integrações

---

## V2

* Gateway MCP Único
* Marketplace
* Publicação de MCPs
* MCP Composer

---

## V3

* MCP Harbor Cloud
* Sync entre dispositivos
* Telemetria
* Gestão remota

---

# Critério de Sucesso

Um usuário sem conhecimento de Docker deve conseguir:

1. Instalar um MCP
2. Configurar credenciais
3. Executar o MCP
4. Conectar ao Cursor

Em menos de 2 minutos.

Se isso acontecer, o produto cumpriu seu objetivo principal.
