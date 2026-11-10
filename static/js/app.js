const $ = (id) => document.getElementById(id);

let authMode = "login";
let isAuthenticated = false;
let hasGeminiKey = false;
let documents = [];
let selectedDocumentId = null;

function toast(message) {
  const el = $("toast");
  el.textContent = message;
  el.classList.remove("hidden");
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => el.classList.add("hidden"), 3200);
}

async function api(url, options = {}) {
  const response = await fetch(url, {
    credentials: "same-origin",
    ...options,
    headers: { ...(options.headers || {}) }
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || `Request failed (${response.status})`);
  return data;
}

function openModal(id) {
  $(id).classList.remove("hidden");
  $(id).classList.add("flex");
}
function closeModal(id) {
  $(id).classList.add("hidden");
  $(id).classList.remove("flex");
}
document.querySelectorAll("[data-close]").forEach(btn =>
  btn.addEventListener("click", () => closeModal(btn.dataset.close))
);

function setAuthMode(mode) {
  authMode = mode;
  $("loginTab").className = mode === "login"
    ? "rounded-lg bg-white py-2 text-xs font-bold shadow-sm"
    : "rounded-lg py-2 text-xs font-semibold text-slate-500";
  $("registerTab").className = mode === "register"
    ? "rounded-lg bg-white py-2 text-xs font-bold shadow-sm"
    : "rounded-lg py-2 text-xs font-semibold text-slate-500";
  $("authPassword").placeholder = mode === "register"
    ? "Password (at least 8 characters)" : "Password";
  $("authError").textContent = "";
}
$("loginTab").addEventListener("click", () => setAuthMode("login"));
$("registerTab").addEventListener("click", () => setAuthMode("register"));

$("authForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  $("authError").textContent = "";
  const endpoint = authMode === "login" ? "/api/auth/login" : "/api/auth/register";
  try {
    await api(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: $("authEmail").value.trim(),
        password: $("authPassword").value
      })
    });
    isAuthenticated = true;
    closeModal("authModal");
    $("accountLabel").textContent = $("authEmail").value.trim();
    $("logoutBtn").classList.remove("hidden");
    toast(authMode === "login" ? "Signed in successfully." : "Account created.");
    openModal("settingsModal");
    await refreshState();
  } catch (error) {
    $("authError").textContent = error.message;
  }
});

async function checkSession() {
  try {
    const data = await api("/api/auth/me");
    isAuthenticated = true;
    $("accountLabel").textContent = "Signed in";
    $("logoutBtn").classList.remove("hidden");
    return data;
  } catch {
    isAuthenticated = false;
    openModal("authModal");
    return null;
  }
}

$("logoutBtn").addEventListener("click", async () => {
  try { await api("/api/auth/logout", { method: "POST" }); } catch {}
  isAuthenticated = false;
  hasGeminiKey = false;
  documents = [];
  renderDocuments();
  $("accountLabel").textContent = "Not signed in";
  $("logoutBtn").classList.add("hidden");
  $("questionInput").disabled = true;
  $("sendBtn").disabled = true;
  $("chatHint").textContent = "Sign in to continue.";
  openModal("authModal");
});

function openSettings() {
  if (!isAuthenticated) return openModal("authModal");
  openModal("settingsModal");
}
$("settingsOpen").addEventListener("click", openSettings);
$("mobileSettings").addEventListener("click", openSettings);
$("configureKeyBtn").addEventListener("click", openSettings);

$("keyForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  $("keyStatus").textContent = "Validating API key...";
  $("keyStatus").className = "text-xs text-slate-500";
  try {
    const result = await api("/api/settings/gemini-key", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ api_key: $("apiKey").value.trim() })
    });
    hasGeminiKey = true;
    $("apiKey").value = "";
    $("keyStatus").textContent = result.message || "API key validated.";
    $("keyStatus").className = "text-xs text-emerald-600";
    $("questionInput").disabled = documents.length === 0;
    $("sendBtn").disabled = documents.length === 0;
    $("chatHint").textContent = documents.length
      ? "Ask a question about your indexed documents."
      : "Now upload a PDF to start chatting.";
    toast("Gemini API key connected.");
    setTimeout(() => closeModal("settingsModal"), 900);
  } catch (error) {
    $("keyStatus").textContent = error.message;
    $("keyStatus").className = "text-xs text-rose-600";
  }
});

$("pdfInput").addEventListener("change", async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  if (!isAuthenticated) {
    openModal("authModal");
    event.target.value = "";
    return;
  }
  if (!hasGeminiKey) {
    openModal("settingsModal");
    $("uploadStatus").textContent = "Configure your Gemini API key first.";
    event.target.value = "";
    return;
  }
  const form = new FormData();
  form.append("file", file);
  $("uploadStatus").textContent = "Uploading and indexing PDF...";
  try {
    const result = await api("/api/upload", { method: "POST", body: form });
    documents.unshift(result);
    selectedDocumentId = result.document_id;
    renderDocuments();
    $("uploadStatus").textContent = `${result.filename} indexed · ${result.chunk_count} chunks`;
    $("welcomePanel").classList.add("hidden");
    $("chatPanel").classList.remove("hidden");
    $("chatPanel").classList.add("flex");
    $("questionInput").disabled = false;
    $("sendBtn").disabled = false;
    $("chatHint").textContent = "Ask a question about your indexed documents.";
    toast("PDF indexed successfully.");
  } catch (error) {
    $("uploadStatus").textContent = error.message;
    toast(error.message);
  } finally {
    event.target.value = "";
  }
});

function renderDocuments() {
  $("docCount").textContent = documents.length;
  const list = $("documentList");
  list.innerHTML = "";
  if (!documents.length) {
    list.innerHTML = '<p class="px-3 py-3 text-xs leading-5 text-slate-400">Your uploaded PDFs will appear here.</p>';
    return;
  }
  documents.forEach(doc => {
    const button = document.createElement("button");
    button.className = "flex w-full items-start gap-3 rounded-xl px-3 py-3 text-left hover:bg-slate-50";
    button.innerHTML = '<span class="mt-0.5 text-lg">📄</span><span class="min-w-0"><span class="block truncate text-xs font-semibold text-slate-700"></span><span class="mt-1 block text-[10px] text-slate-400"></span></span>';
    button.querySelector("span span").textContent = doc.filename;
    button.querySelector("span span + span").textContent = `${doc.chunk_count || 0} chunks · ${doc.page_count || 0} pages`;
    button.addEventListener("click", () => {
      selectedDocumentId = doc.document_id;
      toast(`Chat scoped to ${doc.filename}`);
    });
    list.appendChild(button);
  });
}

function addMessage(role, text, sources = []) {
  $("welcomePanel").classList.add("hidden");
  $("chatPanel").classList.remove("hidden");
  $("chatPanel").classList.add("flex");

  const wrapper = document.createElement("div");
  wrapper.className = role === "user" ? "flex justify-end" : "flex justify-start";
  const bubble = document.createElement("div");
  bubble.className = role === "user"
    ? "max-w-[85%] rounded-2xl rounded-br-md bg-violet-600 px-4 py-3 text-sm leading-6 text-white"
    : "max-w-[90%] rounded-2xl rounded-bl-md border border-line bg-white px-4 py-4 text-sm leading-6 text-slate-700 shadow-panel";
  bubble.textContent = text;
  wrapper.appendChild(bubble);

  if (role !== "user" && sources.length) {
    const sourceBox = document.createElement("div");
    sourceBox.className = "mt-3 border-t border-slate-100 pt-3";
    const heading = document.createElement("p");
    heading.className = "mb-2 text-[10px] font-bold uppercase tracking-wider text-slate-400";
    heading.textContent = "Sources";
    sourceBox.appendChild(heading);
    sources.forEach(source => {
      const line = document.createElement("p");
      line.className = "mb-1 text-[11px] text-slate-500";
      line.textContent = `${source.filename || "Document"} · Page ${source.page_number ?? "—"} · Score ${Number(source.score || 0).toFixed(3)}`;
      sourceBox.appendChild(line);
    });
    bubble.appendChild(sourceBox);
  }
  $("messages").appendChild(wrapper);
  wrapper.scrollIntoView({ behavior: "smooth", block: "end" });
}

async function sendQuestion() {
  const question = $("questionInput").value.trim();
  if (!question) return;
  if (!isAuthenticated) return openModal("authModal");
  if (!hasGeminiKey) return openModal("settingsModal");
  if (!documents.length) return toast("Upload a PDF first.");

  $("questionInput").value = "";
  addMessage("user", question);
  $("sendBtn").disabled = true;
  $("sendBtn").textContent = "Thinking...";
  try {
    const result = await api("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question,
        document_id: selectedDocumentId || undefined,
        limit: 5
      })
    });
    addMessage("assistant", result.answer || "No answer returned.", result.sources || []);
  } catch (error) {
    addMessage("assistant", `I couldn't complete that request: ${error.message}`);
  } finally {
    $("sendBtn").disabled = false;
    $("sendBtn").innerHTML = 'Send <span>↑</span>';
  }
}
$("sendBtn").addEventListener("click", sendQuestion);
$("questionInput").addEventListener("keydown", event => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendQuestion();
  }
});
$("newChatBtn").addEventListener("click", () => {
  $("messages").innerHTML = "";
  $("chatPanel").classList.add("hidden");
  $("chatPanel").classList.remove("flex");
  $("welcomePanel").classList.remove("hidden");
});

async function refreshState() {
  const session = await checkSession();
  if (!session) return;
  // The starter backend does not yet expose a documents-list endpoint.
  $("questionInput").disabled = !hasGeminiKey || documents.length === 0;
  $("sendBtn").disabled = !hasGeminiKey || documents.length === 0;
}

(async function init() {
  await checkSession();
})();
