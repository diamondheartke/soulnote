
/* =========================================
   AVA — INTERACTION CONTROLLER
========================================= */

const root = document.documentElement;

const themeSlider = document.getElementById("themeSlider");
const themeDots = document.querySelectorAll(".theme-dot");
const themeDescription = document.getElementById("themeDescription");

const messageInput = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");
const messagesContainer = document.getElementById("messagesContainer");
const welcomeState = document.getElementById("welcomeState");

const newChatButton = document.getElementById("newChat");
const clearChatButton = document.getElementById("clearChat");

const sidebar = document.getElementById("sidebar");
const openSidebar = document.getElementById("openSidebar");
const closeSidebar = document.getElementById("closeSidebar");
const sidebarOverlay = document.getElementById("sidebarOverlay");

const conversationList = document.getElementById("conversationList");
const characterCount = document.getElementById("characterCount");

const themes = [
    {
        name: "twilight",
        description: "Quiet, atmospheric and reflective."
    },
    {
        name: "daylight",
        description: "Warm, bright and welcoming."
    },
    {
        name: "cyber",
        description: "Modern, expressive and futuristic."
    }
];

let conversations = [];
let currentConversation = [];
let conversationNumber = 0;


/* =========================================
   THEME SYSTEM
========================================= */

function setTheme(index) {

    const selectedTheme = themes[index];

    if (!selectedTheme) return;

    root.dataset.theme = selectedTheme.name;

    themeSlider.value = index;
    themeDescription.textContent = selectedTheme.description;

    themeDots.forEach((dot, dotIndex) => {
        dot.classList.toggle("active", dotIndex === index);
    });

    localStorage.setItem("ava-theme", selectedTheme.name);
}

function loadTheme() {

    const savedTheme = localStorage.getItem("ava-theme");

    const index = themes.findIndex(
        theme => theme.name === savedTheme
    );

    setTheme(index >= 0 ? index : 0);
}

themeSlider.addEventListener("input", event => {
    setTheme(Number(event.target.value));
});

loadTheme();


/* =========================================
   MESSAGE UTILITIES
========================================= */

function getCurrentTime() {

    return new Intl.DateTimeFormat([], {
        hour: "2-digit",
        minute: "2-digit"
    }).format(new Date());
}


function createMessage(role, content) {

    const row = document.createElement("div");

    row.className = `message-row ${role}`;

    if (role === "assistant") {

        const avatar = document.createElement("div");

        avatar.className = "message-avatar";
        avatar.textContent = "✧";

        row.appendChild(avatar);
    }

    const messageContent = document.createElement("div");
    messageContent.className = "message-content";

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";

    // textContent prevents user messages from being interpreted as HTML.
    bubble.textContent = content;

    const time = document.createElement("span");
    time.className = "message-time";
    time.textContent = getCurrentTime();

    messageContent.appendChild(bubble);
    messageContent.appendChild(time);

    row.appendChild(messageContent);

    messagesContainer.appendChild(row);

    return row;
}


/* =========================================
   CONVERSATION MANAGEMENT
========================================= */

function updateConversationList() {

    conversationList.innerHTML = "";

    if (!conversations.length) {

        const empty = document.createElement("p");

        empty.className = "empty-history";
        empty.textContent =
            "Your conversations will appear here.";

        conversationList.appendChild(empty);
        return;
    }

    conversations.forEach(conversation => {

        const button = document.createElement("button");

        button.className = "conversation-item";
        button.textContent = conversation.title;
        button.title = conversation.title;

        button.addEventListener("click", () => {
            loadConversation(conversation.id);
        });

        conversationList.appendChild(button);
    });
}


function saveCurrentConversation() {

    if (!currentConversation.length) return;

    let existing = conversations.find(
        item => item.id === conversationNumber
    );

    const firstUserMessage = currentConversation.find(
        message => message.role === "user"
    );

    const title = firstUserMessage
        ? firstUserMessage.content.slice(0, 35)
        : "New conversation";

    if (!existing) {

        conversations.unshift({
            id: conversationNumber,
            title: title,
            messages: [...currentConversation]
        });

    } else {

        existing.title = title;
        existing.messages = [...currentConversation];
    }

    updateConversationList();
}


function loadConversation(id) {

    const selected = conversations.find(
        conversation => conversation.id === id
    );

    if (!selected) return;

    conversationNumber = selected.id;
    currentConversation = [...selected.messages];

    messagesContainer.innerHTML = "";
    welcomeState.style.display = "none";

    currentConversation.forEach(message => {
        createMessage(message.role, message.content);
    });

    closeSidebarPanel();
    scrollToLatest();
}


function startNewConversation() {

    saveCurrentConversation();

    conversationNumber++;

    currentConversation = [];

    messagesContainer.innerHTML = "";

    welcomeState.style.display = "flex";

    messageInput.value = "";
    updateComposer();

    saveCurrentConversation();

    closeSidebarPanel();
}


function clearConversation() {

    currentConversation = [];

    messagesContainer.innerHTML = "";

    welcomeState.style.display = "flex";

    saveCurrentConversation();

    messageInput.value = "";
    updateComposer();
}


/* =========================================
   CHAT COMPOSITION
========================================= */

function updateComposer() {

    const length = messageInput.value.length;

    characterCount.textContent = `${length} / 8000`;

    sendButton.disabled = !messageInput.value.trim();

    messageInput.style.height = "auto";

    messageInput.style.height =
        Math.min(messageInput.scrollHeight, 150) + "px";
}


messageInput.addEventListener("input", updateComposer);


messageInput.addEventListener("keydown", event => {

    if (event.key === "Enter" && !event.shiftKey) {

        event.preventDefault();

        sendMessage();
    }
});


function sendMessage() {

    const content = messageInput.value.trim();

    if (!content) return;

    welcomeState.style.display = "none";

    currentConversation.push({
        role: "user",
        content: content
    });

    createMessage("user", content);

    messageInput.value = "";

    updateComposer();

    /*
       PREVIEW MODE

       This is where we will later call Ava's inference API.

       The UI does not yet communicate with the model.
       Replace this preview response with the real API response
       when the Colab server and ngrok tunnel are configured.
    */

    const previewResponse =
        "This is the interface preview. Ava's model connection " +
        "has not been configured yet. Your message has been " +
        "added to this temporary conversation.";

    currentConversation.push({
        role: "assistant",
        content: previewResponse
    });

    createMessage("assistant", previewResponse);

    saveCurrentConversation();

    scrollToLatest();
}


function scrollToLatest() {

    const chatArea = document.getElementById("chatArea");

    requestAnimationFrame(() => {
        chatArea.scrollTop = chatArea.scrollHeight;
    });
}


/* =========================================
   SUGGESTION PROMPTS
========================================= */

document.querySelectorAll(".suggestion-card").forEach(card => {

    card.addEventListener("click", () => {

        const prompt = card.querySelector("strong").textContent;

        const prompts = {
            "Something on my mind":
                "There's something on my mind that I'd like to talk about.",

            "How I've been feeling":
                "I've been thinking about how I've been feeling lately.",

            "Just a little conversation":
                "I'd like to have a little conversation with you."
        };

        messageInput.value =
            prompts[prompt] || prompt;

        updateComposer();

        messageInput.focus();
    });
});


/* =========================================
   SIDEBAR CONTROLS
========================================= */

function closeSidebarPanel() {

    sidebar.classList.remove("open");
    sidebarOverlay.classList.remove("active");
}

openSidebar.addEventListener("click", () => {

    sidebar.classList.add("open");
    sidebarOverlay.classList.add("active");
});

closeSidebar.addEventListener("click", closeSidebarPanel);

sidebarOverlay.addEventListener("click", closeSidebarPanel);


newChatButton.addEventListener("click", startNewConversation);

clearChatButton.addEventListener("click", clearConversation);


/* =========================================
   INITIALIZATION
========================================= */

updateConversationList();

updateComposer();
