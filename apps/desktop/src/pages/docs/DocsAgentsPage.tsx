import { DocsArticle, DocsPageHeader, DocsSection } from "@/components/docs/docs-article";
import { DocsCode } from "@/components/docs/docs-code";
import { DocsCallout } from "@/components/docs/docs-callout";

export function DocsAgentsPage() {
  return (
    <DocsArticle>
      <DocsPageHeader
        eyebrow="Agentes e Policy"
        title="Controle de acesso granular"
        description="Defina políticas de allow/deny por servidor, ferramenta e argumento."
      />

      <DocsSection title="Estrutura da política">
        <p>
          A política é um JSON com três níveis hierárquicos. Cada nível pode ser
          <code>null</code> (allow all), <code>[]</code> (deny all), ou uma lista
          de regras.
        </p>
        <DocsCode
          title="Estrutura completa"
          language="json"
          code={`{
  "allowed_servers": [
    {
      "server_id": "github",
      "allowed_tools": [
        {
          "tool_name": "create_issue",
          "argument_rules": [
            { "arg_name": "title", "match_type": "glob", "pattern": "fix:*" },
            { "arg_name": "body", "match_type": "exact", "pattern": "auto-generated" }
          ]
        }
      ]
    }
  ]
}`}
        />
      </DocsSection>

      <DocsSection title="Tipos de match em argumentos">
        <p>Cada <code>ArgumentRule</code> suporta três tipos de correspondência:</p>
        <ul>
          <li>
            <strong>glob</strong> (padrão) — usa <code>fnmatch</code> para patterns
            tipo <code>/home/projects/**</code> ou <code>fix:*</code>
          </li>
          <li>
            <strong>regex</strong> — usa <code>re.match</code> para patterns tipo
            <code>^SELECT\s</code>
          </li>
          <li>
            <strong>exact</strong> — correspondência exata com o pattern
          </li>
        </ul>
        <DocsCallout variant="info">
          Se um argumento não tiver uma regra definida, ele é negado (default-deny).
          Use <code>match_type: "glob"</code> com <code>pattern: "*"</code> para
          permitir qualquer valor.
        </DocsCallout>
      </DocsSection>

      <DocsSection title="Exemplo: GitHub issues">
        <DocsCode
          title="Política"
          language="json"
          code={`{
  "allowed_servers": [
    {
      "server_id": "github",
      "allowed_tools": [
        {
          "tool_name": "create_issue",
          "argument_rules": [
            { "arg_name": "title", "match_type": "glob", "pattern": "fix:*" },
            { "arg_name": "body", "match_type": "glob", "pattern": "*" }
          ]
        }
      ]
    }
  ]
}`}
        />
        <p>
          Esta política permite ao agente chamar <code>create_issue</code> no GitHub,
          mas apenas com títulos começando com <code>fix:</code>.
        </p>
      </DocsSection>

      <DocsSection title="Exemplo: Filesystem restrito">
        <DocsCode
          title="Política"
          language="json"
          code={`{
  "allowed_servers": [
    {
      "server_id": "filesystem",
      "allowed_tools": [
        {
          "tool_name": "read_file",
          "argument_rules": [
            { "arg_name": "path", "match_type": "glob", "pattern": "/home/projects/**" }
          ]
        }
      ]
    }
  ]
}`}
        />
        <p>
          O agente só pode ler arquivos dentro de <code>/home/projects/</code>.
          Qualquer outro path é negado.
        </p>
      </DocsSection>

      <DocsSection title="Exemplo: PostgreSQL com regex">
        <DocsCode
          title="Política"
          language="json"
          code={`{
  "allowed_servers": [
    {
      "server_id": "postgres",
      "allowed_tools": [
        {
          "tool_name": "query",
          "argument_rules": [
            { "arg_name": "sql", "match_type": "regex", "pattern": "^SELECT\\\\s" }
          ]
        }
      ]
    }
  ]
}`}
        />
        <p>
          Apenas queries <code>SELECT</code> são permitidas. Comandos como
          <code>DROP</code>, <code>INSERT</code> ou <code>DELETE</code> são rejeitados.
        </p>
        <DocsCallout variant="warning">
          O pattern regex é testado com <code>re.match()</code>, que ancora no início
          da string. Use <code>^</code> para forçar o início.
        </DocsCallout>
      </DocsSection>
    </DocsArticle>
  );
}
