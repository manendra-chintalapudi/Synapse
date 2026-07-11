import { createClient } from "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm";

const url = window.SYNAPSE_SUPABASE_URL;
const key = window.SYNAPSE_SUPABASE_PUBLISHABLE_KEY;
const supabase = url && key ? createClient(url, key, {
  auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true }
}) : null;

window.synapseSupabase = supabase;
window.synapseSignOut = async () => {
  if (supabase) await supabase.auth.signOut();
  location.replace("/login");
};

async function protectApp(){
  if (document.body.dataset.authRequired !== "true") return;
  if (!supabase) return location.replace("/login?error=config");
  const { data: { session } } = await supabase.auth.getSession();
  if (!session) return location.replace(`/login?next=${encodeURIComponent(location.pathname + location.hash)}`);
  document.body.classList.remove("auth-loading");
  const emailNode = document.getElementById("auth-email");
  if (emailNode) emailNode.textContent = session.user.email || "Signed in";
}

function setupAuthPage(){
  const form = document.getElementById("auth-form");
  if (!form || !supabase) return;
  const status = document.getElementById("auth-status");
  const submit = document.getElementById("auth-submit");
  const switcher = document.getElementById("auth-switch");
  let mode = "signin";
  const render = () => {
    document.getElementById("auth-title").textContent = mode === "signin" ? "Welcome back" : "Create your account";
    document.getElementById("auth-copy").textContent = mode === "signin" ? "Sign in to enter the Synapse plant console." : "Create a secure Synapse account for your plant.";
    submit.textContent = mode === "signin" ? "Sign in" : "Create account";
    switcher.textContent = mode === "signin" ? "New to Synapse? Create an account" : "Already have an account? Sign in";
  };
  switcher.onclick = () => { mode = mode === "signin" ? "signup" : "signin"; status.textContent = ""; render(); };
  form.onsubmit = async event => {
    event.preventDefault(); submit.disabled = true; status.textContent = "";
    const email = form.email.value.trim(); const password = form.password.value;
    const result = mode === "signin"
      ? await supabase.auth.signInWithPassword({ email, password })
      : await supabase.auth.signUp({ email, password, options: { emailRedirectTo: `${location.origin}/app` } });
    submit.disabled = false;
    if (result.error) { status.textContent = result.error.message; status.className = "status error"; return; }
    if (mode === "signup" && !result.data.session) {
      status.textContent = "Check your email to confirm your account, then sign in."; status.className = "status success"; return;
    }
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
