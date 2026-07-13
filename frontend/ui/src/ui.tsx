import * as React from "react";
import * as SelectPrimitive from "@radix-ui/react-select";
import * as TooltipPrimitive from "@radix-ui/react-tooltip";
import { cva, type VariantProps } from "class-variance-authority";
import { Check, ChevronDown, Database, LoaderCircle, TriangleAlert } from "lucide-react";
import { motion } from "motion/react";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

declare global {
  interface Window {
    SYNAPSE_API_URL?: string;
    synapseGetAccessToken?: () => Promise<string>;
    synapseRefreshAccessToken?: () => Promise<string>;
    SynapsePillars?: {
      mount: (route: "rca" | "compliance" | "admin") => Promise<void>;
      openFailure: (failureId: string) => void;
      openStandard: (familyId: string) => void;
    };
  }
}

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

async function accessToken(timeoutMs = 10_000): Promise<string> {
  if (window.synapseGetAccessToken) {
    const token = await window.synapseGetAccessToken();
    if (token) return token;
  }
  await new Promise<void>((resolve) => {
    let finished = false;
    const done = () => {
      if (finished) return;
      finished = true;
      window.clearTimeout(timer);
      resolve();
    };
    const timer = window.setTimeout(done, timeoutMs);
    window.addEventListener("synapse-auth-ready", done, { once: true });
  });
  return window.synapseGetAccessToken ? window.synapseGetAccessToken() : "";
}

export async function apiFetch<T>(path: string): Promise<T> {
  let token = await accessToken();
  if (!token) throw new Error("Your signed-in session is not ready. Refresh or sign in again.");
  const base = (window.SYNAPSE_API_URL || window.location.origin).replace(/\/+$/, "");
  const request = (value: string) => fetch(`${base}${path}`, { headers: { Authorization: `Bearer ${value}` } });
  let response = await request(token);
  if (response.status === 401 && window.synapseRefreshAccessToken) {
    token = await window.synapseRefreshAccessToken();
    if (token) response = await request(token);
  }
  let payload: unknown;
  try {
    payload = await response.json();
  } catch {
    throw new Error(`Invalid server response (${response.status})`);
  }
  if (!response.ok) {
    const detail = payload && typeof payload === "object" && "detail" in payload
      ? String((payload as { detail: unknown }).detail)
      : `HTTP ${response.status}`;
    throw new Error(detail);
  }
  return payload as T;
}

const buttonVariants = cva("sp-button", {
  variants: {
    variant: {
      default: "sp-button--default",
      secondary: "sp-button--secondary",
      outline: "sp-button--outline",
      ghost: "sp-button--ghost",
      danger: "sp-button--danger",
    },
    size: { default: "sp-button--md", sm: "sp-button--sm", icon: "sp-button--icon" },
  },
  defaultVariants: { variant: "default", size: "default" },
});

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement>, VariantProps<typeof buttonVariants> {}
export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(({ className, variant, size, ...props }, ref) => (
  <button ref={ref} className={cn(buttonVariants({ variant, size }), className)} {...props} />
));
Button.displayName = "Button";

const badgeVariants = cva("sp-badge", {
  variants: {
    tone: {
      neutral: "sp-badge--neutral", indigo: "sp-badge--indigo", green: "sp-badge--green",
      amber: "sp-badge--amber", red: "sp-badge--red", violet: "sp-badge--violet", cyan: "sp-badge--cyan",
    },
  },
  defaultVariants: { tone: "neutral" },
});
export function Badge({ className, tone, children }: React.HTMLAttributes<HTMLSpanElement> & VariantProps<typeof badgeVariants>) {
  return <span className={cn(badgeVariants({ tone }), className)}>{children}</span>;
}

export function Card({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <section className={cn("sp-card", className)} {...props} />;
}
export function CardHeader({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("sp-card__header", className)} {...props} />;
}
export function CardTitle({ className, ...props }: React.HTMLAttributes<HTMLHeadingElement>) {
  return <h2 className={cn("sp-card__title", className)} {...props} />;
}
export function CardDescription({ className, ...props }: React.HTMLAttributes<HTMLParagraphElement>) {
  return <p className={cn("sp-card__description", className)} {...props} />;
}
export function CardContent({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("sp-card__content", className)} {...props} />;
}

export function SourcePill({ children = "Direct Neo4j · no LLM" }: { children?: React.ReactNode }) {
  return <div className="sp-source-pill"><Database size={14} aria-hidden="true" /><span>{children}</span><i /></div>;
}

export function PillarHeader({ eyebrow, title, description, children }: {
  eyebrow: string; title: string; description: string; children?: React.ReactNode;
}) {
  return <header className="sp-page-header">
    <div><span className="sp-eyebrow">{eyebrow}</span><h1 tabIndex={-1}>{title}</h1><p>{description}</p></div>
    <div className="sp-page-header__actions">{children || <SourcePill />}</div>
  </header>;
}

export function MetricCard({ label, value, detail, icon: Icon, featured = false, index = 0 }: {
  label: string; value: React.ReactNode; detail?: React.ReactNode; icon: React.ComponentType<{ size?: number; "aria-hidden"?: React.AriaAttributes["aria-hidden"] }>; featured?: boolean; index?: number;
}) {
  return <motion.div className={cn("sp-metric", featured && "sp-metric--featured")}
    initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * .045, duration: .2 }}>
    <div className="sp-metric__top"><span>{label}</span><Icon size={17} aria-hidden={true} /></div>
    <strong>{value}</strong>{detail && <small>{detail}</small>}
  </motion.div>;
}

export function Skeleton({ className }: { className?: string }) { return <div className={cn("sp-skeleton", className)} aria-hidden="true" />; }
export function LoadingState({ label = "Loading evidence…" }: { label?: string }) {
  return <div className="sp-state" role="status" aria-live="polite"><LoaderCircle className="sp-spin" size={22} /><strong>{label}</strong><div className="sp-skeleton-grid"><Skeleton /><Skeleton /><Skeleton /><Skeleton /></div></div>;
}
export function ErrorState({ error, retry }: { error: string; retry?: () => void }) {
  return <div className="sp-state sp-state--error" role="alert"><TriangleAlert size={24} /><strong>Evidence could not be loaded</strong><p>{error}</p>{retry && <Button variant="outline" onClick={retry}>Try again</Button>}</div>;
}
export function EmptyState({ title, detail }: { title: string; detail?: string }) {
  return <div className="sp-empty"><strong>{title}</strong>{detail && <p>{detail}</p>}</div>;
}

export function TooltipButton({ label, children, ...props }: ButtonProps & { label: string }) {
  return <TooltipPrimitive.Provider delayDuration={250}><TooltipPrimitive.Root><TooltipPrimitive.Trigger asChild>
    <Button aria-label={label} {...props}>{children}</Button>
  </TooltipPrimitive.Trigger><TooltipPrimitive.Portal><TooltipPrimitive.Content className="sp-tooltip" sideOffset={7}>{label}<TooltipPrimitive.Arrow className="sp-tooltip__arrow" /></TooltipPrimitive.Content></TooltipPrimitive.Portal></TooltipPrimitive.Root></TooltipPrimitive.Provider>;
}

export interface SelectOption { value: string; label: string; }
export function SelectControl({ value, onValueChange, options, label, placeholder }: {
  value: string; onValueChange: (value: string) => void; options: SelectOption[]; label: string; placeholder?: string;
}) {
  return <label className="sp-field"><span>{label}</span><SelectPrimitive.Root value={value || "__all"} onValueChange={(next) => onValueChange(next === "__all" ? "" : next)}>
    <SelectPrimitive.Trigger className="sp-select" aria-label={label}><SelectPrimitive.Value placeholder={placeholder} /><SelectPrimitive.Icon><ChevronDown size={14} /></SelectPrimitive.Icon></SelectPrimitive.Trigger>
    <SelectPrimitive.Portal><SelectPrimitive.Content className="sp-select-content" position="popper" sideOffset={5}><SelectPrimitive.Viewport>
      <SelectPrimitive.Item className="sp-select-item" value="__all"><SelectPrimitive.ItemText>{placeholder || "All"}</SelectPrimitive.ItemText><SelectPrimitive.ItemIndicator><Check size={13} /></SelectPrimitive.ItemIndicator></SelectPrimitive.Item>
      {options.map((option) => <SelectPrimitive.Item className="sp-select-item" value={option.value} key={option.value}><SelectPrimitive.ItemText>{option.label}</SelectPrimitive.ItemText><SelectPrimitive.ItemIndicator><Check size={13} /></SelectPrimitive.ItemIndicator></SelectPrimitive.Item>)}
    </SelectPrimitive.Viewport></SelectPrimitive.Content></SelectPrimitive.Portal>
  </SelectPrimitive.Root></label>;
}

export function labelize(value: unknown): string {
  return String(value || "—").replace(/_/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
}
export function shortDate(value: unknown): string { const text = String(value || ""); return text ? text.slice(0, 10) : "—"; }
export function number(value: unknown): string { return Number(value || 0).toLocaleString(); }
