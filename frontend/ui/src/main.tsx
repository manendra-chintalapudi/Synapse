import * as React from "react";
import { createRoot, type Root } from "react-dom/client";
import { Toaster } from "sonner";
import "./styles.css";

type PillarRoute = "rca" | "compliance" | "admin";
const roots = new Map<PillarRoute, Root>();
let toasterRoot: Root | null = null;

function ensureToaster() {
  if (toasterRoot) return;
  let element = document.getElementById("synapse-toast-root");
  if (!element) {
    element = document.createElement("div");
    element.id = "synapse-toast-root";
    document.body.appendChild(element);
  }
  toasterRoot = createRoot(element);
  toasterRoot.render(<Toaster richColors position="top-right" closeButton />);
}

function hashSelection(route: PillarRoute): string {
  const parts = window.location.hash.replace(/^#\//, "").split("/");
  return parts[0] === route && parts[1] ? decodeURIComponent(parts.slice(1).join("/")) : "";
}

export async function mount(route: PillarRoute) {
  const element = document.getElementById(`${route}-react-root`);
  if (!element) return;
  const selection = hashSelection(route);
  let content: React.ReactNode;
  if (route === "rca") {
    const Component = (await import("./RcaApp")).default;
    content = <Component key={selection || "rca-list"} initialFailureId={selection || undefined} />;
  } else if (route === "compliance") {
    const Component = (await import("./ComplianceApp")).default;
    content = <Component key={selection || "compliance-list"} initialFamilyId={selection || undefined} />;
  } else {
    const Component = (await import("./EvaluationApp")).default;
    content = <Component />;
  }
  let root = roots.get(route);
  if (!root) {
    root = createRoot(element);
    roots.set(route, root);
  }
  ensureToaster();
  root.render(
    <React.StrictMode>
      {content}
    </React.StrictMode>,
  );
  element.dataset.mounted = "true";
}

function openFailure(failureId: string) {
  window.location.hash = `#/rca/${encodeURIComponent(failureId)}`;
  window.setTimeout(() => window.dispatchEvent(new CustomEvent("synapse-open-failure", { detail: failureId })), 0);
}

function openStandard(familyId: string) {
  window.location.hash = `#/compliance/${encodeURIComponent(familyId)}`;
}

window.SynapsePillars = { mount, openFailure, openStandard };
