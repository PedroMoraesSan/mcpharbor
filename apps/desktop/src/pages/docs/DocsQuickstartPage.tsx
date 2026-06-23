import { DocsArticle, DocsPageHeader, DocsSection } from "@/components/docs/docs-article";
import { DocsCode } from "@/components/docs/docs-code";
import { DocsCallout } from "@/components/docs/docs-callout";

export function DocsQuickstartPage() {
  return (
    <DocsArticle>
      <DocsPageHeader
        title="Início rápido"
        description="Instale, crie um agente e conecte seu cliente MCP em 5 minutos."
      />

      <DocsSection title="1. Instale um servidor MCP">
        <p>
          Navegue até o catálogo no console do Harbor e instale os servidores MCP desejados
          (GitHub, Filesystem, PostgreSQL, etc.). Cada servidor será iniciado automaticamente
          como um gateway HTTP local.
        </p>
        <DocsCallout variant="tip" title="Docker obrigatório">
          O Harbor usa Docker para executar os servidores MCP. Certifique-se de que o Docker
          Desktop está em execução.
        </DocsCallout>
      </DocsSection>

      <DocsSection title="2. Crie um agente">
        <p>
          No painel Access Control, crie um agente. Um token <code>harbour_sk_</code> será
          gerado — guarde-o, ele não será exibido novamente.
        </p>
        <DocsCode
          title="Exemplo: curl"
          language="bash"
          code={`curl -X POST http://localhost:8000/api/v1/agents \\
  -H "Content-Type: application/json" \\
  -d '{"name": "meu-cursor"}'`}
        />
      </DocsSection>

      <DocsSection title="3. Conecte ao gateway">
        <p>
          Use o token para autenticar no gateway unificado. O endpoint MCP fica em:
        </p>
        <DocsCode
          title="Endpoint"
          language="bash"
          code={`POST http://localhost:8000/api/v1/mcp
Authorization: Bearer harbour_sk_xxx

{"method": "tools/list", "id": 1, "jsonrpc": "2.0"}`}
        />
      </DocsSection>

      <DocsSection title="4. Configure a política">
        <p>
          Defina quais servidores, ferramentas e argumentos o agente pode acessar.
          A política segue o modelo default-deny: sem política configurada, sem acesso.
        </p>
        <DocsCode
          title="Exemplo de política"
          language="json"
          code={`{
  "allowed_servers": [
    {
      "server_id": "github",
      "allowed_tools": [
        {
          "tool_name": "create_issue",
          "argument_rules": [
            {"arg_name": "title", "match_type": "glob", "pattern": "fix:*"}
          ]
        }
      ]
    }
  ]
}`}
        />
      </DocsSection>
    </DocsArticle>
  );
}
