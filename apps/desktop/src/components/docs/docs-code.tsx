import { useState } from "react";
import { Check, Copy } from "lucide-react";
import { cn } from "@/lib/utils";

type DocsCodeProps = {
  title?: string;
  code: string;
  language?: "python" | "typescript" | "bash" | "json" | "http";
};

function highlight(code: string, language: DocsCodeProps["language"]) {
  const escaped = code.replace(/&/g, "&amp;").replace(/</g, "&lt;");

  const pyKeywords =
    /\b(async|await|import|from|def|class|return|raise|if|else|elif|for|while|with|as|None|True|False|pass)\b/g;
  const tsKeywords =
    /\b(import|from|const|let|await|async|function|return|export|new|type|interface)\b/g;
  const bashKeywords = /\b(curl|pip|bun|export|cd|make)\b/g;
  const httpKeywords = /\b(GET|POST|PUT|PATCH|DELETE|Authorization|Content-Type|Bearer)\b/g;

  const keywords =
    language === "python"
      ? pyKeywords
      : language === "bash"
        ? bashKeywords
        : language === "http"
          ? httpKeywords
          : tsKeywords;

  const strings = /(".*?"|'.*?'|`.*?`)/g;
  const comments = /(#.*$|\/\/.*$)/gm;
  const numbers = /\b(\d+\.?\d*)\b/g;
  const fn = /\b([a-zA-Z_]\w*)(?=\()/g;

  return escaped
    .replace(comments, '<span class="docs-hl-comment">$1</span>')
    .replace(strings, '<span class="docs-hl-string">$1</span>')
    .replace(keywords, '<span class="docs-hl-keyword">$1</span>')
    .replace(numbers, '<span class="docs-hl-number">$1</span>')
    .replace(fn, '<span class="docs-hl-fn">$1</span>');
}

export function DocsCode({ title, code, language = "python" }: DocsCodeProps) {
  const [copied, setCopied] = useState(false);
  const label = title ?? language;

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code.trim());
    setCopied(true);
    window.setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="docs-code">
      <div className="docs-code-header">
        <span className="docs-code-label">{label}</span>
        <button
          type="button"
          onClick={() => void handleCopy()}
          className="docs-code-copy"
          aria-label={copied ? "Copiado" : "Copiar código"}
        >
          {copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
        </button>
      </div>
      <pre className="docs-code-pre">
        <code
          className="docs-code-content"
          dangerouslySetInnerHTML={{ __html: highlight(code.trim(), language) }}
        />
      </pre>
    </div>
  );
}

export function DocsEndpoint({
  method,
  path,
  description,
}: {
  method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  path: string;
  description: string;
}) {
  const methodClass: Record<typeof method, string> = {
    GET: "docs-method-get",
    POST: "docs-method-post",
    PUT: "docs-method-put",
    PATCH: "docs-method-patch",
    DELETE: "docs-method-delete",
  };

  return (
    <div className="docs-endpoint">
      <span className={cn("docs-method", methodClass[method])}>{method}</span>
      <div className="min-w-0 flex-1">
        <code className="docs-endpoint-path">{path}</code>
        <p className="docs-endpoint-desc">{description}</p>
      </div>
    </div>
  );
}

export function DocsEndpointList({ children }: { children: React.ReactNode }) {
  return <div className="docs-endpoint-list">{children}</div>;
}
