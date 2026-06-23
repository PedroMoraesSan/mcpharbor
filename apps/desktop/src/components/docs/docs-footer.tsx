import { Link } from "react-router-dom";

export function DocsFooter() {
  return (
    <footer className="docs-footer">
      <p className="text-sm text-muted-foreground">
        MCP Harbor · Gateway e controle de acesso para MCP
      </p>
      <div className="flex flex-wrap gap-x-4 gap-y-1 text-sm">
        <Link to="/docs/api" className="text-muted-foreground transition-colors hover:text-foreground">
          API
        </Link>
        <Link to="/docs/architecture" className="text-muted-foreground transition-colors hover:text-foreground">
          Arquitetura
        </Link>
        <Link to="/" className="text-muted-foreground transition-colors hover:text-foreground">
          Console
        </Link>
      </div>
    </footer>
  );
}
