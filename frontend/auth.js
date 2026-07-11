import { createClient } from "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm";

const url = window.SYNAPSE_SUPABASE_URL;
const key = window.SYNAPSE_SUPABASE_PUBLISHABLE_KEY;
const supabase = url && key ? createClient(url, key, { auth: {
  persistSession: true, autoRefreshToken: true, detectSessionInUrl: true
}}) : null;

window.synapseSupabase = supabase;
window.synapseGetAccessToken = async () => {
  if (!supabase) return "";
  const { data: { session } } = await supabase.auth.getSession();
  return session?.access_token || "";
};
window.synapseSignOut = async () => {
  if (supabase) await supabase.auth.signOut();
  location.replace("/login");
};

async function getIdentity(session){
  const metadata = session.user.user_metadata || {};
  let identity = { email: session.user.email || "", name: metadata.full_name || session.user.email?.split("@")[0] || "User", role: metadata.requested_role || "maintenance" };
  try {
    const { data } = await supabase.from("profiles").select("full_name,role,approved").eq("id",session.user.id).maybeSingle();
    if (data) identity = { ...identity, name: data.full_name || identity.name, role: data.role || identity.role, approved: data.approved };
  } catch (_) {}
  return identity;
}

async function protectApp(){
  if (document.body.dataset.authRequired !== "true") return;
  if (!supabase) return location.replace("/login?error=config");
  const { data: { session } } = await supabase.auth.getSession();
  if (!session) return location.replace(`/login?next=${encodeURIComponent(location.pathname + location.hash)}`);
  const identity = await getIdentity(session);
  window.synapseAuth = { session, ...identity };
  document.body.classList.remove("auth-loading");
  const emailNode = document.getElementById("auth-email");
  if (emailNode) emailNode.textContent = identity.email;
  window.dispatchEvent(new CustomEvent("synapse-auth-ready", { detail: window.synapseAuth }));
}

function setupAuthPage(){
  const form = document.getElementById("auth-form");
  if (!form || !supabase) return;
  const shell = document.getElementById("auth-shell"), status = document.getElementById("auth-status");
  const submit = document.getElementById("auth-submit"), loginTab = document.getElementById("auth-tab-login"), registerTab = document.getElementById("auth-tab-register");
  let mode = new URLSearchParams(location.search).get("mode") === "register" ? "signup" : "signin";
  const render = () => {
    const signup = mode === "signup"; shell.classList.toggle("signup", signup);
    document.getElementById("auth-title").textContent = signup ? "Create account" : "Sign in";
    document.getElementById("auth-copy").textContent = signup ? "Set up your profile and choose your demo plant role." : "Use your Synapse credentials to continue.";
    document.getElementById("visual-title").textContent = signup ? "Let’s set up your workspace." : "Welcome back.";
    document.getElementById("visual-copy").textContent = signup ? "Your Synapse assistant is taking note of your role and access." : "Continue your traceable plant investigations securely.";
    submit.textContent = signup ? "Create Synapse account" : "Log in to Synapse";
    loginTab.classList.toggle("active", !signup); registerTab.classList.toggle("active", signup);
    loginTab.setAttribute("aria-selected", String(!signup)); registerTab.setAttribute("aria-selected", String(signup));
    form.full_name.required = signup; form.confirm_password.required = signup; form.password.autocomplete = signup ? "new-password" : "current-password";
  };
  render();
  loginTab.onclick = () => { mode = "signin"; status.textContent = ""; render(); };
  registerTab.onclick = () => { mode = "signup"; status.textContent = ""; render(); };
  document.getElementById("forgot-password").onclick = async () => {
    const email = form.email.value.trim();
    if (!email) { status.textContent = "Enter your email first, then choose Forgot password."; status.className = "status error"; return; }
    const { error } = await supabase.auth.resetPasswordForEmail(email, { redirectTo: `${location.origin}/login` });
    status.textContent = error ? error.message : "Password reset instructions have been sent to your email.";
    status.className = error ? "status error" : "status success";
  };
  form.onsubmit = async event => {
    event.preventDefault(); submit.disabled = true; status.textContent = ""; status.className = "status";
    const email = form.email.value.trim(), password = form.password.value;
    if (mode === "signup" && password !== form.confirm_password.value) { submit.disabled = false; status.textContent = "Passwords do not match."; status.className = "status error"; return; }
    const result = mode === "signin" ? await supabase.auth.signInWithPassword({ email, password }) : await supabase.auth.signUp({
      email, password, options: { emailRedirectTo: `${location.origin}/app`, data: { full_name: form.full_name.value.trim(), requested_role: form.role.value } }
    });
    submit.disabled = false;
    if (result.error) { status.textContent = result.error.message; status.className = "status error"; return; }
    if (mode === "signup" && !result.data.session) { status.textContent = "Account created. Check your email to confirm it, then sign in."; status.className = "status success"; return; }
    const next = new URLSearchParams(location.search).get("next") || "/app";
    location.replace(next.startsWith("/") ? next : "/app");
  };
}

document.addEventListener("DOMContentLoaded", async () => {
  setupAuthPage();
  if (document.body.dataset.authRequired === "true") await protectApp();
  if (document.body.dataset.authPage === "true" && supabase) {
    const { data: { session } } = await supabase.auth.getSession();
    if (session) location.replace("/app");
  }
});
