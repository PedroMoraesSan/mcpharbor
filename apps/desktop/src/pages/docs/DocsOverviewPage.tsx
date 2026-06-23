import { DocsArticle, DocsPageHeader, DocsSection } from "@/components/docs/docs-article";
import { DocsCardGrid, DocsCardLink } from "@/components/docs/docs-card-link";
import { DOCS_NAV } from "@/lib/docs-nav";

const quickLinks = DOCS_NAV.flatMap((s) => s.items).filter((item) => item.href !== "/docs");

export function DocsOverviewPage() {
  return (
    <DocsArticle>
      <DocsPageHeader
        title="MCP Harbor"
        description="Gateway unificado com controle de acesso granular para servidores MCP. Gerencie, proteja e conecte seus MCPs com segurança."
      />

      <DocsSection title="O que é o MCP Harbor?">
        <p>
          MCP Harbor é uma plataforma desktop que unifica o gerenciamento de servidores MCP
          (Model Context Protocol). Ele oferece um gateway centralizado com autenticação por token,
          controle de acesso baseado em políticas (allow/deny por servidor, ferramenta e argumento),
          e uma interface visual para administrar tudo.
        </p>
      </DocsSection>

      <DocsSection title="Começar rápido">
        <DocsCardGrid>
          {quickLinks.map((item) => (
            <DocsCardLink
              key={item.href}
              href={item.href}
              title={item.label}
              description={item.description ?? ""}
              icon={item.icon}
            />
          ))}
        </DocsCardGrid>
      </DocsSection>
    </DocsArticle>
  );
}
