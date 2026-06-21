# MCP Harbor

# Design System & Product Experience

Versão 0.1

---

# Objetivo

Este documento define a identidade visual, experiência do usuário, princípios de design e componentes utilizados no MCP Harbor.

Seu objetivo é garantir consistência visual, experiência de uso previsível e alinhamento com o posicionamento do produto.

---

# Filosofia de Produto

O MCP Harbor não é uma ferramenta corporativa.

O MCP Harbor é uma ferramenta para desenvolvedores.

A experiência deve transmitir:

* Controle
* Velocidade
* Simplicidade
* Transparência
* Poder

O usuário deve sentir que está utilizando:

> "Um Docker Desktop criado para a era dos agentes de IA."

---

# Referências Visuais

O design do MCP Harbor deve buscar inspiração em:

## Produtos

* Docker Desktop
* Raycast
* Warp
* Ghostty
* Cursor
* Claude Code
* GitHub Desktop
* Linear

---

# Conceito Visual

## Developer Retro Futurism

Mistura entre:

* Terminal retrô
* Ferramentas modernas para desenvolvedores
* Interfaces minimalistas
* Dashboards operacionais

O produto não deve parecer:

* ERP
* CRM
* Sistema corporativo
* Dashboard SaaS genérico

O produto deve parecer:

* Ferramenta de engenharia
* Ambiente operacional
* Console de controle

---

# Princípios de UX

## 1. Tudo deve ser descoberto visualmente

O usuário nunca deve precisar:

* Ler documentação
* Abrir terminal
* Procurar arquivos JSON

A interface deve conduzir a experiência.

---

## 2. Status sempre visível

Todo MCP deve apresentar:

* Status
* Porta
* Consumo de recursos
* Versão

Sem necessidade de abrir telas secundárias.

---

## 3. Ação rápida

Nenhuma ação principal deve exigir mais de:

* 2 cliques

Exemplos:

Instalar MCP

```text
Install
```

Executar MCP

```text
Start
```

Conectar ao Cursor

```text
Connect
```

---

## 4. Logs são produto

Logs não são recurso secundário.

Logs são parte central da experiência.

Sempre visíveis.

---

# Identidade Visual

## Tema

Dark Mode First

Não haverá Light Mode na V1.

---

# Paleta Principal

## Background

```css
#09090b
```

---

## Surface

```css
#111113
```

---

## Border

```css
#27272a
```

---

## Foreground

```css
#fafafa
```

---

## Muted

```css
#71717a
```

---

# Cores de Estado

## Success

```css
#00ff88
```

---

## Warning

```css
#ffb454
```

---

## Error

```css
#ff5f56
```

---

## Info

```css
#3b82f6
```

---

# Tipografia

## Interface

Fonte principal:

```text
Geist
```

Uso:

* Menus
* Botões
* Cards
* Navegação

---

## Código

Fonte secundária:

```text
JetBrains Mono
```

Uso:

* Logs
* JSON
* Configurações
* Código

---

# Layout

## Estrutura Principal

```text
┌──────────────────────────────┐
│ Sidebar                      │
├──────────────┬───────────────┤
│              │               │
│              │               │
│              │               │
│              │               │
│              │               │
│              │               │
└──────────────┴───────────────┘
```

---

## Sidebar

Largura:

```text
260px
```

Itens:

* Dashboard
* MCPs
* Catalog
* Logs
* Integrations
* Settings

---

# Dashboard

A tela inicial deve responder:

* Quantos MCPs estão ativos?
* Existe algum erro?
* Qual consumo atual?
* Existe atualização disponível?

---

# Componentes Selecionados

Todos os componentes devem ser implementados utilizando:

```text
shadcn/ui
+
21st.dev
```

---

# Componentes Obrigatórios

## Terminal Bento Grid

Origem:

21st.dev

Uso:

Dashboard principal.

Exibição:

* MCPs ativos
* CPU
* RAM
* Atualizações

---

## Agent Plan

Origem:

21st.dev

Uso:

Fluxo de instalação.

Exemplo:

```text
Install Github MCP

✓ Pull Image
✓ Configure Secrets
✓ Start Runtime
```

---

## Code Editor

Origem:

21st.dev

Uso:

Visualização de:

* Logs
* JSON
* Configurações

---

## File Tree

Origem:

21st.dev

Uso:

Estrutura dos MCPs instalados.

---

## Prompt Search

Origem:

21st.dev

Uso:

Busca global.

Exemplo:

```text
Search MCPs...
```

---

## Tubelight Navbar

Origem:

21st.dev

Uso:

Navegação principal.

---

# Estilo dos Cards

Os cards devem transmitir:

* Ferramenta técnica
* Sistema operacional
* Painel de controle

Evitar:

* Sombras excessivas
* Gradientes exagerados
* Glassmorphism

Preferir:

* Bordas discretas
* Alto contraste
* Aparência sólida

---

# Componentes de Status

## Running

```text
● Running
```

Verde.

---

## Stopped

```text
● Stopped
```

Cinza.

---

## Error

```text
● Error
```

Vermelho.

---

# Logs

Os logs devem lembrar um terminal moderno.

Referências:

* Warp
* Ghostty
* Claude Code

Características:

* Fonte monoespaçada
* Scroll infinito
* Busca integrada
* Destaque para erros

---

# Microinterações

## Hover

Transições rápidas.

Máximo:

```css
150ms
```

---

## Loading

Utilizar skeletons.

Evitar:

* Spinners longos

---

## Instalação

Sempre mostrar progresso.

Exemplo:

```text
Pulling image...

███████████░░░░░░
65%
```

---

# Ícones

Biblioteca oficial:

```text
Lucide React
```

---

# Biblioteca UI

## Base

```text
shadcn/ui
```

---

## Componentes avançados

```text
21st.dev
```

---

# Estrutura Visual das Telas

## Dashboard

* Terminal Bento Grid
* MCP Status
* Resource Usage
* Updates

---

## Catalog

* Busca
* Lista de MCPs
* Instalação

---

## MCP Details

* Informações
* Credenciais
* Logs
* Atualizações

---

## Integrations

* Cursor
* Claude Desktop
* OpenCode
* Cline

---

## Settings

* Docker
* Diretórios
* Registry

---

# O que NÃO Fazer

Nunca utilizar:

* Material UI
* Ant Design
* Bootstrap
* Aparência corporativa
* Visual de ERP
* Visual SaaS genérico

---

# Objetivo Final

Quando alguém abrir o MCP Harbor pela primeira vez deve pensar:

> "Parece uma mistura entre Docker Desktop, Raycast e Cursor."

E imediatamente entender que está utilizando uma ferramenta feita para desenvolvedores que trabalham com agentes de IA.
