# MCP Harbor — Roadmap de Implementação

Implementação completa das funcionalidades de controle de acesso e identidade,
inspiradas pelo [MCP Harbour (mcpharbour.ai)](https://mcpharbour.ai).

---

## Fase 1 — Motor de Políticas (Policy Engine) ✅

## O que foi feito

Sistema de **default-deny** onde o usuário define quem (qual agente) pode
acessar o quê (qual MCP, qual tool, quais argumentos).

### Novos arquivos

| Arquivo | Descrição |
|---------|-----------|
| `domain/entities/policy.py` | `Agent`, `AgentPolicy`, `ServerPolicy`, `ToolRule` |
| `domain/repositories/policy_repository.py` | Interfaces `AgentRepository`, `PolicyRepository` |
| `domain/services/policy_service.py` | ABC `PolicyService` com `check_tool_allowed()` |
| `infrastructure/policy/policy_service.py` | `PolicyEvaluationService` — avaliação em 3 níveis (server → tool → argument) |
| `infrastructure/persistence/models.py` | `AgentModel`, `PolicyModel` (SQLAlchemy) |
| `infrastructure/persistence/repositories.py` | `SQLAlchemyAgentRepository` (inclui `get_by_token_hash`), `SQLAlchemyPolicyRepository` |
| `alembic/versions/002_add_policies.py` | Migration com tabelas `agents` + `policies` |
| `application/use_cases/agents.py` | `ListAgentsUseCase`, `CreateAgentUseCase`, `DeleteAgentUseCase` |
| `application/use_cases/policies.py` | `GetPolicyUseCase`, `UpdatePolicyUseCase` |
| `application/dto/agent_dto.py` | `AgentDTO`, `AgentWithTokenDTO` |
| `presentation/api/v1/router.py` | Rotas `GET/POST/DELETE /api/v1/agents`, `GET/PUT /api/v1/agents/{id}/policy` |
| `presentation/schemas/mcp_schemas.py` | Schemas Pydantic para Agent/Policy |
| `presentation/api/dependencies.py` | DI container com novos repos + use cases |
| `apps/desktop/src/pages/agents/AgentsPage.tsx` | UI: listar, criar, deletar agents |
| `apps/desktop/src/pages/agents/AgentPolicyPage.tsx` | UI: editor visual de políticas |
| `apps/desktop/src/app/router.tsx` | Rotas `/agents` e `/agents/:agentId/policy` |
| `apps/desktop/src/layouts/AppLayout/Sidebar.tsx` | Nav link "Access Control" |
| `apps/desktop/src/lib/api-client.ts` | `requestRaw()` exportado |

### Decisões técnicas

- **Policy como JSON column** (`rules_json`) na tabela `policies` — flexível para
  novos tipos de regra sem schema migration.
- **`None` = permitir todos** vs **lista vazia = permitir nenhum** nos 3 níveis
  (servers, tools, arguments).
- **Token gerado com `harbour_sk_` + SHA-256** — mostrado uma única vez no
  create; apenas o hash é persistido.
- **Agente e Policy em tabelas separadas** — permite versionamento independente
  da policy.

### Bug corrigido (loading loop)

O PyInstaller sidecar (DMG) entrava em loop de loading porque os novos módulos
(`application.use_cases.agents`, `application.use_cases.policies`,
`infrastructure.policy.policy_service`) não estavam em `hiddenimports` no
`fastapi-server.spec`. A correção foi adicionar os imports manualmente —
necessário porque o auto-detect do PyInstaller nem sempre encontra módulos
importados dinamicamente.

---

## Fase 2 — Identidade e Autenticação ✅

### O que foi feito

Cada agente recebe um **token Bearer** (`harbour_sk_...`). O daemon deriva a
identidade do token — o agente **não pode se autodeclarar**.

### Novos arquivos

| Arquivo | Descrição |
|---------|-----------|
| `domain/services/auth_service.py` | `AgentContext` dataclass + `AuthService` ABC |
| `infrastructure/auth/token_service.py` | `generate_token()`, `hash_token()`, `TokenAuthService` |
| `presentation/api/middleware/auth.py` | `AuthMiddleware` — extrai Bearer, valida, seta `request.state.agent` |

### Arquivos modificados

| Arquivo | Mudança |
|---------|---------|
| `main.py` | Registra `AuthMiddleware` no app |
| `application/use_cases/agents.py` | Refatorado para usar `generate_token()` do token_service (removido hashlib/secrets inline) |
| `fastapi-server.spec` | `hiddenimports` para `infrastructure.auth.token_service` e `presentation.api.middleware.auth` |
| `tests/test_middleware_auth.py` | 6 testes novos (rota pública, admin sem token, token ausente, inválido, malformado, válido) |

### Fluxo de autenticação

```
Agent → Authorization: Bearer harbour_sk_... → AuthMiddleware
  → SHA-256(token) → AgentRepository.get_by_token_hash()
  → se válido → request.state.agent = AgentContext(agent_id, agent_name)
  → se inválido → 401
```

### Rotas protegidas vs públicas

| Rota | Protegida? | Motivo |
|------|-----------|--------|
| `/health` | ❌ | Health check do Tauri |
| `/docs`, `/openapi.json` | ❌ | Documentação |
| `/api/v1/agents` (POST) | ❌ | Criar primeiro agent |
| `/api/v1/mcps/*`, `/api/v1/catalog`, etc | ❌ | Admin desktop |
| `/api/v1/mcp` (Fase 3) | ✅ | Agent-facing |

### Dívida técnica sanada

- `TokenAuthService` implementa `AuthService` ABC e é usado pelo middleware
- `request.state.agent` armazena `AgentContext` objeto tipado (pronto p/ Fase 3)
- 6 testes de middleware garantem o comportamento

---

## Fase 3 — Unified MCP Gateway ✅

### O que foi feito

Endpoint único `/api/v1/mcp` que agrega todos os MCPs rodando. O agente
configura **um único endpoint** com seu token e o Harbor roteia cada
`call_tool` para o servidor certo, respeitando a política.

### Novos arquivos

| Arquivo | Descrição |
|---------|-----------|
| `infrastructure/mcp/unified_gateway.py` | `UnifiedMcpGateway` — proxy MCP unificado |

### Arquivos modificados

| Arquivo | Mudança |
|---------|---------|
| `infrastructure/mcp/gateway.py` | `GatewaySession` ganhou `catalog_id` + `name`; `start()` aceita novos params; nova prop `sessions` |
| `application/use_cases/expose_mcp.py` | Passa `catalog_id` + `name` ao `gateway_manager.start()` |
| `presentation/api/v1/router.py` | Nova rota `POST /api/v1/mcp` |
| `presentation/api/dependencies.py` | `UnifiedMcpGateway` no `UseCaseContainer` |
| `fastapi-server.spec` | `hiddenimports` para `infrastructure.mcp.unified_gateway` |

### Como funciona

Requisição `POST /api/v1/mcp` com JSON-RPC body:

**`tools/list`**:
1. Itera todos MCPs rodando (`gateway_manager.sessions`)
2. Para cada MCP, faz `POST :{port}/mcp` com `tools/list`
3. Se agente autenticado: filtra tools pela política (`PolicyService.check_tool_allowed`)
4. Retorna JSON-RPC com lista combinada

**`tools/call`**:
1. Busca tool name no `_tool_map` (tool_name → catalog_id + mcp_id)
2. Se agente autenticado: checa política (`check_tool_allowed`)
3. Encaminha chamada para o MCP dono da tool
4. Retorna resposta do MCP

**`resources/list`**: agrega resources de todos MCPs.

### Tool Map

Mapeamento `tool_name → (catalog_id, mcp_id)` construído durante `tools/list`
e usado em `tools/call` para rotear para o servidor correto.

---

## Fase 4 — GPARS Error Codes ✅

### O que foi feito

Implementação dos error codes do padrão GPARS para compatibilidade com clientes
que seguem o spec.

### Novos arquivos

| Arquivo | Descrição |
|---------|-----------|
| `shared/errors.py` | Constantes `AUTHORIZATION_DENIED_CODE (-31001)`, `SERVER_UNAVAILABLE_CODE (-31002)` |
| `infrastructure/mcp/gpars.py` | Helpers `authorization_denied()`, `server_unavailable()` |
| `tests/test_gpars.py` | 7 testes (4 helpers, 3 integração gateway) |

### Arquivos modificados

| Arquivo | Mudança |
|---------|---------|
| `infrastructure/mcp/unified_gateway.py` | Usa helpers GPARS em vez de `isError` content text |
| `fastapi-server.spec` | `hiddenimports` para `infrastructure.mcp.gpars` |

### Códigos implementados

| Código | Nome | Quando retornar |
|--------|------|----------------|
| `-31001` | `AUTHORIZATION_DENIED` | Tool não permitida pela política do agente |
| `-31002` | `SERVER_UNAVAILABLE` | Tool não encontrada, servidor caiu ou não respondeu |

### Formato JSON-RPC

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -31001,
    "message": "Tool 'write_file' is not allowed for agent 'cursor-1'",
    "data": { "gpars_code": "AUTHORIZATION_DENIED" }
  }
}
```

---

## Fase 5 — UI Desktop ✅

### O que foi feito

Refinamentos na interface desktop: informações de conexão do endpoint unificado,
mini-lista de agents nas configurações, e client API tipado.

### Arquivos modificados

| Arquivo | Mudança |
|---------|---------|
| `apps/desktop/src/lib/api-client.ts` | Interfaces `Agent`, `AgentPolicy`, `ToolRule`, `ServerPolicy` + métodos `api.agents.*` e `api.policies.*` |
| `apps/desktop/src/pages/settings/SettingsPage.tsx` | Cards "MCP Endpoint" (URL + config snippet) e "Agents" (mini-lista + link policy) |

### Settings Page

- Endpoint URL copiável: `http://127.0.0.1:8741/api/v1/mcp`
- Template JSON para configurar MCP clients (Cursor, Claude Code, VS Code, OpenCode)
- Lista de agents com link direto para policy de cada um

---

## Resumo Final

| Fase | Esforço | Feature | Arquivos novos | Arquivos modificados |
|------|---------|---------|----------------|---------------------|
| **1** | ~4 dias | Policy Engine | 12 | 8 |
| **2** | ~2 dias | Identity & Auth | 4 | 3 + 1 teste |
| **3** | ~3 dias | Unified Gateway | 1 | 5 |
| **4** | ~1 dia | GPARS Errors | 3 | 2 + 1 teste |
| **5** | ~1 dia | UI Desktop | 0 | 2 |
| **Total** | ~11 dias | — | 20 | 20+ |

### Estado atual

- **Backend**: 41/43 testes passando (2 pre-existing em `test_use_cases.py`)
- **Frontend**: TypeScript build limpo
- **DMG**: Bug de loading loop corrigido (hiddenimports)

### Comparação com mcpharbour.ai

| Funcionalidade | mcpharbour.ai | MCP Harbor |
|---------------|---------------|------------|
| Políticas por agente (server → tool → argument) | ✅ | ✅ |
| Token Bearer (`harbour_sk_...` + SHA-256) | ✅ | ✅ |
| Middleware de autenticação | ✅ | ✅ |
| Endpoint MCP único | ✅ | ✅ |
| Códigos de erro GPARS (-31001, -31002) | ✅ | ✅ |
| UI Desktop (Tauri + React) | ❌ (CLI-only) | ✅ |
| Docker para isolar MCPs | ❌ (stdio nativo) | ✅ |
| Globs/regex em argument policies | ✅ | ❌ (exato apenas) |
| CLI admin (`harbour` command) | ✅ | ❌ (UI desktop) |

### Próximos passos possíveis

1. **Glob/regex em argument policies** — substituir match exato por
   `fnmatch`/`re` no `PolicyEvaluationService`
2. **SSE no `/api/v1/mcp`** — suporte a eventos SSE no gateway unificado
3. **Token refresh/revoke** — expiração e renovação de tokens
4. **Audit logging** — registro de todas as chamadas de tool por agente
5. **CLI `harbour`** — CLI administrativo independente
