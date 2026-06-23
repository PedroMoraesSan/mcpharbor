import { DocsArticle, DocsPageHeader, DocsSection } from "@/components/docs/docs-article";
import { DocsCode } from "@/components/docs/docs-code";
import { DocsEndpoint, DocsEndpointList } from "@/components/docs/docs-code";

export function DocsApiPage() {
  return (
    <DocsArticle>
      <DocsPageHeader
        eyebrow="Referência"
        title="API HTTP"
        description="Endpoints REST do MCP Harbor."
      />

      <DocsSection title="Gateway MCP">
        <DocsEndpointList>
          <DocsEndpoint method="POST" path="/api/v1/mcp" description="Gateway unificado JSON-RPC. Requer token Bearer." />
          <DocsEndpoint method="GET" path="/api/v1/mcp/{mcp_id}/sse" description="SSE stream para um servidor MCP específico." />
          <DocsEndpoint method="POST" path="/api/v1/mcp/{mcp_id}/sse/messages?session_id=xxx" description="Envia mensagem para o SSE session." />
        </DocsEndpointList>

        <DocsCode
          title="Exemplo: tools/list"
          language="http"
          code={`POST /api/v1/mcp HTTP/1.1
Host: localhost:8000
Authorization: Bearer harbour_sk_xxx
Content-Type: application/json

{"method": "tools/list", "id": 1, "jsonrpc": "2.0"}`}
        />
      </DocsSection>

      <DocsSection title="Agentes">
        <DocsEndpointList>
          <DocsEndpoint method="GET" path="/api/v1/agents" description="Lista todos os agentes." />
          <DocsEndpoint method="POST" path="/api/v1/agents" description="Cria um novo agente. Retorna o token uma única vez." />
          <DocsEndpoint method="DELETE" path="/api/v1/agents/{agent_id}" description="Remove um agente." />
        </DocsEndpointList>

        <DocsCode
          title="Criar agente"
          language="bash"
          code={`curl -X POST http://localhost:8000/api/v1/agents \\
  -H "Content-Type: application/json" \\
  -d '{"name": "meu-agent"}'`}
        />
      </DocsSection>

      <DocsSection title="Políticas">
        <DocsEndpointList>
          <DocsEndpoint method="GET" path="/api/v1/agents/{agent_id}/policy" description="Obtém a política de um agente." />
          <DocsEndpoint method="PUT" path="/api/v1/agents/{agent_id}/policy" description="Atualiza a política de um agente." />
        </DocsEndpointList>

        <DocsCode
          title="Atualizar política"
          language="bash"
          code={`curl -X PUT http://localhost:8000/api/v1/agents/agent-id/policy \\
  -H "Content-Type: application/json" \\
  -d '{"allowed_servers": [{"server_id": "github", "allowed_tools": null}]}'`}
        />
      </DocsSection>

      <DocsSection title="Servidores MCP (Mcps)">
        <DocsEndpointList>
          <DocsEndpoint method="GET" path="/api/v1/mcps" description="Lista servidores instalados." />
          <DocsEndpoint method="GET" path="/api/v1/mcps/{mcp_id}" description="Detalhes de um servidor." />
          <DocsEndpoint method="POST" path="/api/v1/mcps/{mcp_id}/start" description="Inicia um servidor." />
          <DocsEndpoint method="POST" path="/api/v1/mcps/{mcp_id}/stop" description="Para um servidor." />
          <DocsEndpoint method="POST" path="/api/v1/mcps/{mcp_id}/restart" description="Reinicia um servidor." />
          <DocsEndpoint method="DELETE" path="/api/v1/mcps/{mcp_id}" description="Desinstala um servidor." />
          <DocsEndpoint method="GET" path="/api/v1/mcps/{mcp_id}/metrics" description="Métricas de CPU/memória." />
          <DocsEndpoint method="GET" path="/api/v1/mcps/{mcp_id}/logs" description="Logs do servidor (stream)." />
        </DocsEndpointList>
      </DocsSection>

      <DocsSection title="Catálogo">
        <DocsEndpointList>
          <DocsEndpoint method="GET" path="/api/v1/catalog" description="Lista servidores disponíveis no catálogo." />
          <DocsEndpoint method="POST" path="/api/v1/mcps/install" description="Instala um servidor do catálogo." />
        </DocsEndpointList>
      </DocsSection>

      <DocsSection title="Integrações">
        <DocsEndpointList>
          <DocsEndpoint method="GET" path="/api/v1/settings" description="Configurações do Harbor." />
          <DocsEndpoint method="GET" path="/api/v1/dashboard/stats" description="Estatísticas do dashboard." />
          <DocsEndpoint method="POST" path="/api/v1/integrations/cursor/connect" description="Conecta um servidor ao Cursor." />
        </DocsEndpointList>
      </DocsSection>
    </DocsArticle>
  );
}
