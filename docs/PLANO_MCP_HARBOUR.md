# Plano de Implementação — MCP Harbour v2

## Visão Geral

Adicionar ao MCP Harbor as funcionalidades de controle de acesso e identidade do MCP Harbour (mcpharbour.ai): **políticas por agente**, **autenticação via token**, **endpoint único `/mcp`** e **códigos de erro GPARS**.

---

## Fase 1 — Motor de Políticas (Policy Engine)

### O que muda

Hoje qualquer agente com acesso ao Harbor pode usar qualquer MCP. Precisamos de um sistema onde o usuário define **quem** pode acessar **o quê**.

### Novos arquivos

```
services/api/src/domain/entities/policy.py     # Policy, PolicyRule entidades
services/api/src/domain/repositories/policy_repository.py  # interface
services/api/src/domain/services/policy_service.py         # avaliação de políticas
```

### `domain/entities/policy.py`

```python
@dataclass(frozen=True)
class ToolRule:
    tool_name: str
    allowed_arguments: list[str] | None = None  # None = todos

@dataclass(frozen=True)
class ServerPolicy:
    server_id: str       # catalog_id do MCP
    allowed_tools: list[ToolRule] | None = None  # None = todas as tools

@dataclass(frozen=True)
class AgentPolicy:
    agent_id: str
    allowed_servers: list[ServerPolicy] | None = None  # None = todos servidores
```

### `domain/services/policy_service.py`

```python
class PolicyService(ABC):
    @abstractmethod
    async def get_policy(self, agent_id: str) -> AgentPolicy | None: ...

    @abstractmethod
    async def check_tool_allowed(
        self, agent_id: str, server_id: str, tool_name: str, arguments: dict
    ) -> bool: ...
```

### Banco de dados — migration `002_add_policies`

```python
# Novas tabelas:
#   agents (id, name, token_hash, created_at)
#   policies (id, agent_id FK, policy_json JSON)
```

### UI — nova página "Access Control"

`apps/desktop/src/pages/policies/`:
- Listar agents com suas policies
- Editor visual de regras (quais MCPs, quais tools, quais argumentos)
- Gerar token para novo agent

### Arquivos a modificar

| Arquivo | Mudança |
|---------|---------|
| `domain/entities/__init__.py` | Exportar novas entidades |
| `infrastructure/persistence/models.py` | Models `AgentModel`, `PolicyModel` |
| `infrastructure/persistence/repositories.py` | `SQLAlchemyPolicyRepository` |
| `infrastructure/persistence/database.py` | Nova dependência |
| `presentation/api/dependencies.py` | Novo container `PolicyService` |
| `presentation/api/v1/router.py` | Novas rotas `/api/v1/agents`, `/api/v1/policies` |
| `presentation/schemas/mcp_schemas.py` | Schemas Agent/Policy |
| `shared/result.py` | Código `authorization_denied` |
| `alembic/versions/002_add_policies.py` | Migration |
| `package.json` / scripts | Nenhuma mudança |

---

## Fase 2 — Identidade e Autenticação

### O que muda

Cada agente (Cursor, Claude, OpenCode) recebe um **token Bearer** tipo `harbour_sk_...`. O daemon deriva a identidade do token — o agente **não pode se autodeclarar**.

### Novos arquivos

```
services/api/src/domain/services/auth_service.py     # hash, verify
services/api/src/infrastructure/auth/token_service.py # geração/validação
services/api/src/presentation/api/middleware/auth.py  # FastAPI middleware
```

### Fluxo de autenticação

```
Agent → Bearer token → AuthMiddleware → resolve identity → request context
```

### `infrastructure/auth/token_service.py`

```python
class TokenService:
    @staticmethod
    def generate() -> tuple[str, str]:   # (raw_token, hashed_token)
        raw = f"harbour_sk_{secrets.token_urlsafe(32)}"
        hashed = hashlib.sha256(raw.encode()).hexdigest()
        return raw, hashed

    @staticmethod
    def verify(token: str, hashed: str) -> bool:
        return hashlib.sha256(token.encode()).hexdigest() == hashed
```

### Middleware de autenticação

```python
# presentation/api/middleware/auth.py
@dataclass
class AgentContext:
    agent_id: str
    agent_name: str

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        token = request.headers.get("Authorization", "").removeprefix("Bearer ")
        agent = await resolve_agent(token)
        request.state.agent = agent
        return await call_next(request)
```

### Arquivos a modificar

| Arquivo | Mudança |
|---------|---------|
| `infrastructure/auth/token_service.py` | Novo — geração/verificação |
| `presentation/api/middleware/auth.py` | Novo — middleware |
| `main.py` | Adicionar middleware (exceto nas rotas públicas /health) |
| `domain/services/auth_service.py` | Interface abstrata |
| `infrastructure/persistence/models.py` | Model `SessionModel` (opcional) |
| `presentation/api/v1/router.py` | Rotas `POST /api/v1/agents` (criar agent + token) |
| `presentation/api/dependencies.py` | Injetar `AgentContext` nos use cases |
| `presentation/schemas/mcp_schemas.py` | Schema `AgentResponse` |

---

## Fase 3 — Endpoint Único `/mcp`

### O que muda

Hoje cada MCP exposto vira `http://127.0.0.1:{porta}/mcp`. O agente precisa configurar cada um separadamente.

Com o endpoint único, o agente configura **um único endpoint** `http://127.0.0.1:8741/mcp` com seu token Bearer. O Harbour roteia cada `call_tool` para o servidor certo baseado na identidade + política.

### Novo gateway unificado

Substituir (ou complementar) o `gateway.py` atual por um **proxy MCP único** que:

1. Recebe `tools/list` → retorna tools de **todos** os servidores que o agente pode acessar (prefixadas ou com metadata)
2. Recebe `tools/call` → identifica qual servidor basedo no `tool_name` → encaminha
3. Bloqueia tools que não estão na policy do agente

### Novos arquivos

```
services/api/src/infrastructure/mcp/unified_gateway.py
```

### `unified_gateway.py` — esboço

```python
class UnifiedMcpGateway:
    def __init__(self, policy_service, ...):
        self._servers: dict[str, ServerConnection] = {}

    async def handle_list_tools(self, agent_id: str) -> list[Tool]:
        policy = await self._policy_service.get_policy(agent_id)
        tools = []
        for server_id, conn in self._servers.items():
            if not policy or any(s.server_id == server_id for s in policy.allowed_servers):
                server_tools = await conn.list_tools()
                tools.extend(server_tools)
        return tools

    async def handle_call_tool(self, agent_id: str, tool_name: str, args: dict):
        # encontrar qual servidor tem esse tool
        # verificar política
        # encaminhar
```

### Rotas

```python
# /api/v1/mcp — endpoints do protocolo MCP
POST /api/v1/mcp  → tools/list, tools/call, resources/list, etc.
GET  /api/v1/mcp/sse → SSE events
```

### Arquivos a modificar

| Arquivo | Mudança |
|---------|---------|
| `infrastructure/mcp/unified_gateway.py` | Novo — proxy MCP unificado |
| `infrastructure/mcp/gateway.py` | Refatorar `McpGatewayManager` para usar o novo gateway; manter compatibilidade |
| `presentation/api/v1/router.py` | Novas rotas `/api/v1/mcp` |
| `presentation/schemas/mcp_schemas.py` | Schemas MCP protocol |
| `application/use_cases/list_catalog.py` | Atualizar `_to_mcp_dto` |
| `application/dto/mcp_dto.py` | `harbor_endpoint` field |

---

## Fase 4 — GPARS Compliance

### O que muda

Implementar os error codes do padrão GPARS para compatibilidade com clientes que seguem o spec.

### Códigos

| Código | Significado | Quando retornar |
|--------|-------------|-----------------|
| `-31001` | `AUTHORIZATION_DENIED` | Tool não permitida pela policy |
| `-31002` | `SERVER_UNAVAILABLE` | MCP server não está rodando |

### Implementação

```python
# shared/errors.py
class GparsError(Exception):
    AUTHORIZATION_DENIED = -31001
    SERVER_UNAVAILABLE = -31002

class AuthorizationDenied(GparsError):
    code = -31001
    message = "AUTHORIZATION_DENIED"

class ServerUnavailable(GparsError):
    code = -31002
    message = "SERVER_UNAVAILABLE"
```

No unified gateway, capturar e retornar no formato JSON-RPC:

```json
{
    "jsonrpc": "2.0",
    "id": 1,
    "error": {
        "code": -31001,
        "message": "AUTHORIZATION_DENIED",
        "data": "Tool 'github_create_issue' is not allowed for agent 'cursor-1'"
    }
}
```

### Arquivos a modificar

| Arquivo | Mudança |
|---------|---------|
| `shared/errors.py` | Novo — classes de erro GPARS |
| `infrastructure/mcp/unified_gateway.py` | Retornar erros GPARS |
| `infrastructure/mcp/gateway.py` | Retornar erros GPARS |

---

## Fase 5 — Integração Desktop (UI)

### Novas páginas

```
apps/desktop/src/pages/agents/
  index.tsx        → listar agents
  new.tsx          → criar agent + mostrar token
  [id]/policies.tsx → editar políticas

apps/desktop/src/pages/settings/
  tokens.tsx       → gerenciar tokens
```

### Modificações no API client

```typescript
// apps/desktop/src/lib/api-client.ts
export interface Agent {
  id: string;
  name: string;
  created_at: string;
}

export interface Policy {
  agent_id: string;
  allowed_servers: {
    server_id: string;
    allowed_tools: { tool_name: string; allowed_arguments?: string[] }[] | null;
  }[] | null;
}

api.agents = {
  list: () => request<Agent[]>("/api/v1/agents"),
  create: (name: string) => request<Agent & { token: string }>("/api/v1/agents", {
    method: "POST", body: JSON.stringify({ name }),
  }),
  delete: (id: string) => request(`/api/v1/agents/${id}`, { method: "DELETE" }),
};

api.policies = {
  get: (agentId: string) => request<Policy>(`/api/v1/agents/${agentId}/policy`),
  update: (agentId: string, policy: Policy) =>
    request(`/api/v1/agents/${agentId}/policy`, {
      method: "PUT", body: JSON.stringify(policy),
    }),
};
```

---

## Roadmap de Implementação

| Fase | Esforço | Depende de | Descrição |
|------|---------|------------|-----------|
| **1 — Policy Engine** | 3-4 dias | Nenhuma | Entidades, repos, service, migration, rotas CRUD |
| **2 — Auth + Tokens** | 2-3 dias | Fase 1 | Token generation, middleware, rotas agents |
| **3 — Endpoint Único** | 4-5 dias | Fase 1 + 2 | Proxy MCP unificado, roteamento por policy |
| **4 — GPARS** | 1 dia | Fase 3 | Error codes padronizados |
| **5 — UI Desktop** | 3-4 dias | Fase 1 + 2 | Páginas Agents, Policies, Settings |

**Total estimado: 13-17 dias**

---

## Prioridade Sugerida

1. **Fase 1 (Policy Engine)** — base de tudo, pode ser feito sem quebrar nada existente
2. **Fase 2 (Auth)** — necessário para o endpoint único ser seguro
3. **Fase 3 (Endpoint Único)** — a feature mais visível para o usuário
4. **Fase 4 (GPARS)** — compatibilidade com spec
5. **Fase 5 (UI)** — visual, pode ser feito em paralelo com Fase 3-4

---

## Arquivos Finais (resumo do que será criado)

```
Novos:
  services/api/src/domain/entities/policy.py
  services/api/src/domain/repositories/policy_repository.py
  services/api/src/domain/services/policy_service.py
  services/api/src/domain/services/auth_service.py
  services/api/src/infrastructure/auth/token_service.py
  services/api/src/infrastructure/mcp/unified_gateway.py
  services/api/src/presentation/api/middleware/auth.py
  services/api/src/shared/errors.py
  services/api/alembic/versions/002_add_policies.py
  apps/desktop/src/pages/agents/
  apps/desktop/src/pages/settings/tokens.tsx

Modificados:
  services/api/src/main.py                    → middleware auth
  services/api/src/domain/entities/__init__.py
  services/api/src/infrastructure/persistence/models.py
  services/api/src/infrastructure/persistence/repositories.py
  services/api/src/infrastructure/persistence/database.py
  services/api/src/infrastructure/mcp/gateway.py
  services/api/src/presentation/api/dependencies.py
  services/api/src/presentation/api/v1/router.py
  services/api/src/presentation/schemas/mcp_schemas.py
  services/api/src/application/dto/mcp_dto.py
  services/api/src/shared/result.py
  apps/desktop/src/lib/api-client.ts
```
