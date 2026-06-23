import { DocsArticle, DocsPageHeader, DocsSection } from "@/components/docs/docs-article";
import { DocsCode } from "@/components/docs/docs-code";
import { DocsCallout } from "@/components/docs/docs-callout";

export function DocsAuthPage() {
  return (
    <DocsArticle>
      <DocsPageHeader
        eyebrow="Autenticação"
        title="Tokens e controle de acesso"
        description="Autentique clientes MCP com tokens harbour_sk_ e políticas granulares."
      />

      <DocsSection title="Formato do token">
        <p>
          Os tokens seguem o formato <code>harbour_sk_</code> seguido de uma string
          hex aleatória de 32 bytes. O hash SHA-256 do token é armazenado no banco de
          dados — o token bruto é exibido apenas uma vez, na criação do agente.
        </p>
        <DocsCode
          title="Exemplo de token"
          language="bash"
          code={`harbour_sk_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2`}
        />
      </DocsSection>

      <DocsSection title="Autenticação no gateway">
        <p>
          Inclua o token no header <code>Authorization</code> de todas as requisições
          ao gateway unificado:
        </p>
        <DocsCode
          title="Request"
          language="http"
          code={`POST /api/v1/mcp HTTP/1.1
Host: localhost:8000
Authorization: Bearer harbour_sk_a1b2c3...
Content-Type: application/json

{"method": "tools/list", "id": 1, "jsonrpc": "2.0"}`}
        />
        <DocsCallout variant="warning">
          Rotas administrativas (agentes, catálogo, etc.) não exigem token.
          Apenas o endpoint <code>/api/v1/mcp</code> é protegido.
        </DocsCallout>
      </DocsSection>

      <DocsSection title="Criar agente via API">
        <DocsCode
          title="curl"
          language="bash"
          code={`curl -s -X POST http://localhost:8000/api/v1/agents \\
  -H "Content-Type: application/json" \\
  -d '{"name": "meu-agent"}' | jq`}
        />
        <p>
          Resposta (token exibido uma única vez):
        </p>
        <DocsCode
          title="Resposta"
          language="json"
          code={`{
  "id": "uuid-do-agente",
  "name": "meu-agent",
  "token": "harbour_sk_a1b2...",
  "created_at": "2026-06-22T00:00:00"
}`}
        />
      </DocsSection>

      <DocsSection title="Modelo de segurança">
        <p>
          O Harbor adota <strong>default-deny</strong>: um agente sem política configurada
          não tem acesso a nenhum servidor. As políticas são definidas em três níveis:
        </p>
        <ul>
          <li><strong>Servidor</strong> — quais servidores MCP o agente pode acessar</li>
          <li><strong>Ferramenta</strong> — quais ferramentas dentro de cada servidor</li>
          <li><strong>Argumento</strong> — quais valores de argumento são permitidos, com suporte a glob e regex</li>
        </ul>
      </DocsSection>
    </DocsArticle>
  );
}
