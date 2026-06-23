import { cn } from "@/lib/utils";

function slugify(title: string): string {
  return title
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
}

export function DocsArticle({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return <article className={cn("docs-article", className)}>{children}</article>;
}

export function DocsPageHeader({
  eyebrow,
  title,
  description,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
}) {
  return (
    <header className="docs-page-header">
      {eyebrow ? <p className="docs-eyebrow">{eyebrow}</p> : null}
      <h1 className="docs-title">{title}</h1>
      {description ? <p className="docs-description">{description}</p> : null}
    </header>
  );
}

export function DocsSection({
  id,
  title,
  children,
}: {
  id?: string;
  title: string;
  children: React.ReactNode;
}) {
  const sectionId = id ?? slugify(title);

  return (
    <section id={sectionId} className="docs-section scroll-mt-24">
      <h2 className="docs-section-title">{title}</h2>
      <div className="docs-section-body">{children}</div>
    </section>
  );
}
