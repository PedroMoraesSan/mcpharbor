import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";

type TocItem = {
  id: string;
  title: string;
};

export function DocsToc() {
  const { pathname } = useLocation();
  const [items, setItems] = useState<TocItem[]>([]);
  const [activeId, setActiveId] = useState<string>("");

  useEffect(() => {
    let observer: IntersectionObserver | null = null;

    const timer = window.setTimeout(() => {
      const sections = Array.from(
        document.querySelectorAll<HTMLElement>(".docs-article .docs-section[id]"),
      );

      const parsed = sections
        .map((section) => {
          const heading = section.querySelector(".docs-section-title");
          const title = heading?.textContent?.trim();
          const id = section.id;
          if (!title || !id) return null;
          return { id, title };
        })
        .filter((item): item is TocItem => item !== null);

      setItems(parsed);
      if (parsed.length > 0) setActiveId(parsed[0].id);

      if (parsed.length === 0) return;

      observer = new IntersectionObserver(
        (entries) => {
          const visible = entries
            .filter((e) => e.isIntersecting)
            .sort((a, b) => b.intersectionRatio - a.intersectionRatio);
          if (visible[0]?.target.id) {
            setActiveId(visible[0].target.id);
          }
        },
        {
          rootMargin: "-20% 0px -55% 0px",
          threshold: [0, 0.25, 0.5, 1],
        },
      );

      sections.forEach((section) => observer?.observe(section));
    }, 0);

    return () => {
      window.clearTimeout(timer);
      observer?.disconnect();
    };
  }, [pathname]);

  if (items.length < 2) return null;

  return (
    <aside className="docs-toc" aria-label="Nesta página">
      <p className="docs-toc-label">Nesta página</p>
      <nav>
        <ul className="docs-toc-list">
          {items.map((item) => (
            <li key={item.id}>
              <a
                href={`#${item.id}`}
                className={cn("docs-toc-link", activeId === item.id && "docs-toc-link-active")}
                onClick={(e) => {
                  e.preventDefault();
                  document.getElementById(item.id)?.scrollIntoView({ behavior: "smooth", block: "start" });
                  setActiveId(item.id);
                }}
              >
                {item.title}
              </a>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
}
