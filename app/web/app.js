const form = document.getElementById("chatForm");
const messages = document.getElementById("messages");
const input = document.getElementById("messageInput");
const sendBtn = form?.querySelector(".send-btn");
const newChat = document.getElementById("newChat");
const deleteChat = document.getElementById("deleteChat");
const chatList = document.getElementById("chatList");
const loadMemory = document.getElementById("loadMemory");
const clearChat = document.getElementById("clearChat");
const exportChat = document.getElementById("exportChat");
const memoryList = document.getElementById("memoryList");
const addDocuments = document.getElementById("addDocuments");
const documentsInput = document.getElementById("documentsInput");
const documentsStatus = document.getElementById("documentsStatus");
const autoScroll = document.getElementById("autoScroll");
const showSteps = document.getElementById("showSteps");
const statusText = document.getElementById("statusText");
const errorBanner = document.getElementById("errorBanner");
const quickHello = document.getElementById("quickHello");
const quickRag = document.getElementById("quickRag");
const quickTool = document.getElementById("quickTool");

const STORAGE_KEY = "modular-ai-chat";
const CHAT_LIST_KEY = "modular-ai-chat-list";
const ACTIVE_CHAT_KEY = "modular-ai-active-chat";

function getUserId() {
  return getActiveChat() || "default_user";
}

function saveActiveChat(chatId) {
  localStorage.setItem(ACTIVE_CHAT_KEY, chatId);
}

function getActiveChat() {
  return localStorage.getItem(ACTIVE_CHAT_KEY);
}

function loadChatList() {
  return JSON.parse(localStorage.getItem(CHAT_LIST_KEY) || "[]");
}

function saveChatList(list) {
  localStorage.setItem(CHAT_LIST_KEY, JSON.stringify(list));
}

function renderChatList(activeId) {
  const chats = loadChatList();
  chatList.innerHTML = "";
  if (!chats.length) {
    chatList.innerHTML = "<div class='chat-item'>Sem chats.</div>";
    return;
  }
  chats.forEach((chat) => {
    const item = document.createElement("div");
    item.className = `chat-item ${chat.id === activeId ? "active" : ""}`;
    item.textContent = chat.title || "Novo chat";
    item.addEventListener("click", () => {
      if (item.classList.contains("editing")) return;
      saveActiveChat(chat.id);
      loadChat(chat.id);
      chatList.querySelectorAll(".chat-item").forEach((el) => el.classList.remove("active"));
      item.classList.add("active");
    });
    item.addEventListener("dblclick", (event) => {
      event.stopPropagation();
      item.classList.add("editing");
      const input = document.createElement("input");
      input.type = "text";
      input.value = chat.title || "Novo chat";
      item.innerHTML = "";
      item.appendChild(input);
      input.focus();
      input.select();

      const commit = () => {
        const newTitle = input.value.trim().slice(0, 40) || "Novo chat";
        chat.title = newTitle;
        saveChatList(chats);
        renderChatList(chat.id);
      };

      input.addEventListener("keydown", (keyEvent) => {
        if (keyEvent.key === "Enter") {
          keyEvent.preventDefault();
          commit();
        }
        if (keyEvent.key === "Escape") {
          keyEvent.preventDefault();
          renderChatList(getActiveChat());
        }
      });
      input.addEventListener("click", (clickEvent) => clickEvent.stopPropagation());
      input.addEventListener("dblclick", (clickEvent) => clickEvent.stopPropagation());
      input.addEventListener("blur", commit);
    });
    chatList.appendChild(item);
  });
}

function ensureChat() {
  const chats = loadChatList();
  if (!chats.length) {
    const id = `chat_${Date.now()}`;
    chats.push({ id, title: "Novo chat" });
    saveChatList(chats);
    saveActiveChat(id);
  }
  const active = getActiveChat() || chats[0].id;
  renderChatList(active);
  loadChat(active);
}

function setStatus(text, isError = false) {
  statusText.textContent = text;
  statusText.parentElement.querySelector(".dot").style.background = isError
    ? "#e53e3e"
    : "#38a169";
}

function showError(text) {
  errorBanner.textContent = text;
  errorBanner.classList.remove("hidden");
}

function clearError() {
  errorBanner.classList.add("hidden");
  errorBanner.textContent = "";
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

const userAvatarSvg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 4-6 8-6s8 2 8 6"/></svg>';
const agentAvatarSvg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="6" width="16" height="12" rx="2"/><circle cx="9" cy="13" r="1.5" fill="currentColor"/><circle cx="15" cy="13" r="1.5" fill="currentColor"/><path d="M9 6V4a3 3 0 0 1 6 0v2"/></svg>';

function appendMessage(text, role, meta = "") {
  const row = document.createElement("div");
  row.className = `message-row ${role}`;

  const avatar = document.createElement("div");
  avatar.className = "message-avatar";
  avatar.innerHTML = role === "user" ? userAvatarSvg : agentAvatarSvg;

  const content = document.createElement("div");
  content.className = "message-content";

  const bubble = document.createElement("div");
  bubble.className = "message-bubble message " + role;
  if (role === "agent" && typeof marked !== "undefined") {
    const html = marked.parse(escapeHtml(text), { breaks: true, gfm: true });
    bubble.innerHTML = html;
  } else {
    bubble.textContent = text;
  }
  if (meta) {
    const metaEl = document.createElement("span");
    metaEl.className = "meta";
    metaEl.textContent = meta;
    bubble.appendChild(metaEl);
  }

  content.appendChild(bubble);
  row.appendChild(avatar);
  row.appendChild(content);
  messages.appendChild(row);

  if (autoScroll.checked) {
    messages.scrollTop = messages.scrollHeight;
  }
}

function persistChat(userId, role, text, meta) {
  const stored = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
  if (!stored[userId]) stored[userId] = [];
  stored[userId].push({ role, text, meta, timestamp: Date.now() });
  localStorage.setItem(STORAGE_KEY, JSON.stringify(stored));
}

function loadChat(userId) {
  messages.innerHTML = "";
  const stored = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
  const history = stored[userId] || [];
  history.forEach((item) => {
    const time = new Date(item.timestamp).toLocaleTimeString();
    appendMessage(item.text, item.role, `${item.meta || ""} ${time}`.trim());
  });
}

async function sendMessage(message, userId) {
  const response = await fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, message }),
  });
  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || "Falha na requisição");
  }
  return response.json();
}

async function fetchMemory(userId) {
  const response = await fetch(`/memory/${encodeURIComponent(userId)}`);
  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || "Falha ao carregar memória");
  }
  return response.json();
}

async function addDocumentsToRag(documents) {
  const response = await fetch("/documents", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ documents }),
  });
  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || "Falha ao adicionar documentos");
  }
  return response.json();
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = input.value.trim();
  const userId = getUserId();
  if (!message) return;

  clearError();
  appendMessage(message, "user");
  persistChat(userId, "user", message, "Você");
  input.value = "";
  if (sendBtn) sendBtn.disabled = true;

  try {
    const data = await sendMessage(message, userId);
    const meta = showSteps.checked ? `Passos: ${data.steps}` : "";
    appendMessage(data.reply, "agent", meta);
    persistChat(userId, "agent", data.reply, meta);
    const chats = loadChatList();
    const current = chats.find((chat) => chat.id === userId);
    if (current && (current.title === "Novo chat" || !current.title)) {
      current.title = message.slice(0, 32);
      saveChatList(chats);
      renderChatList(userId);
    }
  } catch (err) {
    showError(err.message);
    appendMessage(`Erro: ${err.message}`, "agent");
  } finally {
    if (sendBtn) sendBtn.disabled = false;
    input.focus();
  }
});

newChat.addEventListener("click", () => {
  const chats = loadChatList();
  const id = `chat_${Date.now()}`;
  chats.push({ id, title: "Novo chat" });
  saveChatList(chats);
  saveActiveChat(id);
  loadChat(id);
  renderChatList(id);
});

deleteChat.addEventListener("click", () => {
  const userId = getUserId();
  const chats = loadChatList().filter((chat) => chat.id !== userId);
  saveChatList(chats);
  const stored = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
  delete stored[userId];
  localStorage.setItem(STORAGE_KEY, JSON.stringify(stored));
  const nextId = chats[0]?.id || "default_user";
  saveActiveChat(nextId);
  loadChat(nextId);
  renderChatList(nextId);
});

loadMemory.addEventListener("click", async () => {
  const userId = getUserId();
  memoryList.innerHTML = "";
  clearError();
  try {
    const data = await fetchMemory(userId);
    if (!data.memories.length) {
      memoryList.innerHTML = "<div class='memory-item'>Sem memórias.</div>";
      return;
    }
    data.memories.forEach((mem) => {
      const item = document.createElement("div");
      item.className = "memory-item";
      item.textContent = mem;
      memoryList.appendChild(item);
    });
  } catch (err) {
    showError(err.message);
  }
});

clearChat.addEventListener("click", () => {
  const userId = getUserId();
  const stored = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
  stored[userId] = [];
  localStorage.setItem(STORAGE_KEY, JSON.stringify(stored));
  loadChat(userId);
});

exportChat.addEventListener("click", () => {
  const userId = getUserId();
  const stored = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
  const history = stored[userId] || [];
  const content = history
    .map((item) => `[${new Date(item.timestamp).toISOString()}] ${item.role}: ${item.text}`)
    .join("\n");
  const blob = new Blob([content], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `chat_${userId}.txt`;
  link.click();
  URL.revokeObjectURL(url);
});

addDocuments.addEventListener("click", async () => {
  const raw = documentsInput.value.trim();
  if (!raw) {
    documentsStatus.textContent = "Nenhum documento para enviar.";
    return;
  }
  const documents = raw
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
  documentsStatus.textContent = "Enviando...";
  clearError();
  try {
    const data = await addDocumentsToRag(documents);
    documentsStatus.textContent = `Indexados: ${data.count}`;
    documentsInput.value = "";
  } catch (err) {
    documentsStatus.textContent = "Erro ao indexar documentos.";
    showError(err.message);
  }
});

quickHello.addEventListener("click", () => {
  input.value = "Olá! O que você pode fazer?";
  input.focus();
});

quickRag.addEventListener("click", () => {
  input.value = "Busque informações relevantes na base vetorial.";
  input.focus();
});

quickTool.addEventListener("click", () => {
  input.value = 'USE_TOOL:external_api_mock {"resource":"status"}';
  input.focus();
});

window.addEventListener("load", () => {
  ensureChat();
  setStatus("Conectado ao backend");
});
