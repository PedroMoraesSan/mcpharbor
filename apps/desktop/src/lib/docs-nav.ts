import type { LucideIcon } from "lucide-react";
import {
  BookOpen,
  KeyRound,
  Rocket,
  Braces,
  Shield,
  Network,
} from "lucide-react";

export type DocsNavItem = {
  href: string;
  label: string;
  icon: LucideIcon;
  description?: string;
};

export type DocsNavSection = {
  title: string;
  items: DocsNavItem[];
};

export const DOCS_NAV: DocsNavSection[] = [
  {
    title: "Começar",
    items: [
      {
        href: "/docs",
        label: "Visão geral",
        icon: BookOpen,
        description: "Arquitetura e conceitos",
      },
      {
        href: "/docs/quickstart",
        label: "Início rápido",
        icon: Rocket,
        description: "Instalar e conectar em 5 min",
      },
      {
        href: "/docs/authentication",
        label: "Autenticação",
        icon: KeyRound,
        description: "Tokens harbour_sk_ e policy",
      },
    ],
  },
  {
    title: "Plataforma",
    items: [
      {
        href: "/docs/agents",
        label: "Agentes e Policy",
        icon: Shield,
        description: "Controle de acesso granular",
      },
      {
        href: "/docs/architecture",
        label: "Arquitetura",
        icon: Network,
        description: "Gateway, SSE e roteamento",
      },
    ],
  },
  {
    title: "Referência",
    items: [
      {
        href: "/docs/api",
        label: "API HTTP",
        icon: Braces,
        description: "Endpoints REST",
      },
    ],
  },
];

export const DOCS_VERSION = "0.1";
