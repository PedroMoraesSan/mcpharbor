import { DocsArticle, DocsPageHeader, DocsSection } from "@/components/docs/docs-article";
import { DocsCode } from "@/components/docs/docs-code";

export function DocsArchitecturePage() {
  return (
    <DocsArticle>
      <DocsPageHeader
        eyebrow="Arquitetura"
        title="Gateway, SSE e roteamento"
        description="Como o Harbor gerencia e roteia conexões MCP."
      />

      <DocsSection title="Visão geral">
        <p>
          O Harbor utiliza uma arquitetura de gateway em duas camadas. Cada servidor
          MCP é executado em seu próprio processo Docker, com um proxy HTTP local
          (<em>Streamable HTTP Gateway</em>) em uma porta dedicada (18000-18999).
        </p>
        <p>
          O gateway unificado (<code>/api/v1/mcp</code>) agrega todas as ferramentas
          disponíveis e roteia chamadas para o servidor correto, aplicando políticas
          de acesso no processo.
        </p>
      </DocsSection>

      <DocsSection title="Fluxo de uma chamada">
        <ol>
          <li>
            <strong>Cliente</strong> envia JSON-RPC para <code>POST /api/v1/mcp</code>
            com token Bearer
          </li>
          <li>
            <strong>Auth Middleware</strong> valida o token e identifica o agente
          </li>
          <li>
            <strong>Unified Gateway</strong> recebe a requisição com o contexto do agente
          </li>
          <li>
            <strong>Policy Service</strong> verifica se o agente tem permissão para
            o servidor, ferramenta e argumentos
          </li>
          <li>
            <strong>Proxy HTTP</strong> encaminha a chamada ao gateway do servidor MCP
            específico
          </li>
          <li>
            <strong>Resposta</strong> é retornada ao cliente, possivelmente com erro
            GPARS se negado
          </li>
        </ol>
      </DocsSection>

      <DocsSection title="Suporte SSE">
        <p>
          Cada servidor MCP expõe um endpoint SSE nativo em
          <code>http://127.0.0.1:{'{port}'}/sse</code>. O Harbor faz proxy desses
          endpoints através do gateway unificado:
        </p>
        <DocsCode
          title="SSE endpoint"
          language="bash"
          code={`# Conectar via SSE a um servidor específico
GET http://localhost:8000/api/v1/mcp/{mcp_id}/sse
Authorization: Bearer harbour_sk_xxx`}
        />
        <p>
          O proxy SSE reescreve os URLs dos eventos <code>endpoint</code> para
          apontar de volta ao gateway, permitindo que o cliente envie mensagens
          via <code>POST /api/v1/mcp/{'{mcp_id}'}/sse/messages</code>.
        </p>
      </DocsSection>

      <DocsSection title="Códigos de erro GPARS">
        <p>
          Quando uma chamada é negada pela política ou o servidor está indisponível,
          o gateway retorna erros no formato GPARS (Google's Provider Access
          Restriction Standards):
        </p>
        <DocsCode
          title="Authorization denied"
          language="json"
          code={`{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -31001,
    "message": "Tool 'write_file' is not allowed for agent 'meu-agent'",
    "data": { "gpars_code": "AUTHORIZATION_DENIED" }
  }
}`}
        />
        <DocsCode
          title="Server unavailable"
          language="json"
          code={`{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -31002,
    "message": "Tool 'query' not found on any available server",
    "data": { "gpars_code": "SERVER_UNAVAILABLE" }
  }
}`}
        />
      </DocsSection>
    </DocsArticle>
  );
}
