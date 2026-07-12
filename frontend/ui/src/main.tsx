import * as React from "react";
import { createRoot, type Root } from "react-dom/client";
import { Toaster } from "sonner";
import "./styles.css";

type PillarRoute = "rca" | "compliance";
const roots = new Map<PillarRoute, Root>();
let pendingFailureId = "";
let pendingFamilyId = "";

function hashSelection(route: PillarRoute): string {
  const parts = window.location.hash.replace(/^#\//, "").split("/");
  return parts[0] === route && parts[1] ? decodeURIComponent(parts.slice(1).join("/")) : "";
}

export async function mount(route: PillarRoute) {
  const element = document.getElementById(`${route}-react-root`);
  if (!element) return;
  const Component = route === "rca"
    ? (await import("./RcaApp")).default
    : (await import("./ComplianceApp")).default;
  let root = roots.get(route);
  if (!root) {
    root = createRoot(element);
    roots.set(route, root);
  }
  const selection = hashSelection(route) || (route === "rca" ? pendingFailureId : pendingFamilyId);
  root.render(
    <React.StrictMode>
      <Toaster richColors position="top-right" closeButton />
      {route === "rca"
        ? <Component key={selection || "rca-list"} initialFailureId={selection || undefined} />
        : <Component key={selection || "compliance-list"} initialFamilyId={selection || undefined} />}
    </React.StrictMode>,
  );
  element.dataset.mounted = "true";
}

function openFailure(failureId: string) {
  pendingFailureId = failureId;
  window.location.hash = `#/rca/${encodeURIComponent(failureId)}`;
  void mount("rca").then(() => window.dispatchEvent(new CustomEvent("synapse-open-failure", { detail: failureId })));
}

function openStandard(familyId: string) {
  pendingFamilyId = familyId;
  window.location.hash = `#/compliance/${encodeURIComponent(familyId)}`;
  void mount("compliance");
}

window.SynapsePillars = { mount, openFailure, openStandard };

const route = window.location.hash.replace(/^#\//, "").split("/")[0];
if (route === "rca" || route === "compliance") void mount(route);
