/* =====================================================
   AVA — INTERACTION CONTROLLER
   Django-backed conversation architecture
===================================================== */


/* =====================================================
   1. DOM REFERENCES
===================================================== */

const root = document.documentElement;

const messageForm = document.getElementById("messageForm");
const messageInput = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");

const messagesContainer = document.getElementById("messagesContainer");
const welcomeState = document.getElementById("welcomeState");

const conversationUUID = document.getElementById("conversationUUID");
const submissionStatus = document.getElementById("submissionStatus");

const conversationList = document.getElementById("conversationList");
const chatArea = document.getElementById("chatArea");

const characterCount = document.getElementById("characterCount");

const themeSlider = document.getElementById("themeSlider");
const themeDots = document.querySelectorAll(".theme-dot");
const themeDescription = document.getElementById("themeDescription");

const sidebar = document.getElementById("sidebar");
const openSidebar = document.getElementById("openSidebar");
const closeSidebar = document.getElementById("closeSidebar");
const sidebarOverlay = document.getElementById("sidebarOverlay");


/* =====================================================
   2. APPLICATION STATE
===================================================== */

let isSubmitting = false;


/* =====================================================
   3. THEME SYSTEM
===================================================== */

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


function setTheme(index) {

    const selectedTheme = themes[index];

    if (!selectedTheme) return;

    root.dataset.theme = selectedTheme.name;

    if (themeSlider) {
        themeSlider.value = index;
    }

    if (themeDescription) {
        themeDescription.textContent = selectedTheme.description;
    }

    themeDots.forEach((dot, dotIndex) => {
        dot.classList.toggle("active", dotIndex === index);
    });

    try {
        localStorage.setItem("ava-theme", selectedTheme.name);
    } catch (error) {
        console.warn("Ava could not save the selected theme:", error);
    }
}


function loadTheme() {

    let savedTheme = null;

    try {
        savedTheme = localStorage.getItem("ava-theme");
    } catch (error) {
        console.warn("Ava could not access local storage:", error);
    }

    const index = themes.findIndex(
        theme => theme.name === savedTheme
    );

    setTheme(index >= 0 ? index : 0);
}


if (themeSlider) {

    themeSlider.addEventListener("input", event => {
        setTheme(Number(event.target.value));
    });
}

loadTheme();


/* =====================================================
   4. MESSAGE RENDERING
===================================================== */


function renderMessage(message) {

    if (!messagesContainer || !message) {
        console.error("Cannot render message: missing container or data.");
        return;
    }

    // Avoid duplicate bubbles if a message has already been rendered.
    if (
        message.id !== undefined &&
        messagesContainer.querySelector(
            `[data-message-id="${String(message.id)}"]`
        )
    ) {
        return;
    }

    const article = document.createElement("article");

    article.className = `message message-${message.role}`;
    article.dataset.messageId = message.id;
    article.dataset.role = message.role;

    // Avatar
    const avatar = document.createElement("div");

    avatar.className = "message-avatar";

    const avatars = {
        user: "You",
        assistant: "✧",
        system: "⚙",
        tool: "◈"
    };

    avatar.textContent = avatars[message.role] || "◈";

    // Message body
    const body = document.createElement("div");

    body.className = "message-body";

    // Metadata
    const meta = document.createElement("div");

    meta.className = "message-meta";

    const author = document.createElement("span");

    const authorNames = {
        user: "You",
        assistant: "Ava",
        system: "System",
        tool: "Tool"
    };

    author.textContent = authorNames[message.role] || "Unknown";

    const time = document.createElement("time");

    const date = new Date(message.created_at);

    if (!Number.isNaN(date.getTime())) {

        time.dateTime = date.toISOString();

        time.textContent = date.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit"
        });

    } else {

        time.textContent = "";
    }

    // Content
    const content = document.createElement("div");

    content.className = "message-content";

    // Never interpret user content as HTML.
    content.textContent = message.content;

    meta.append(author, time);

    body.append(meta, content);

    article.append(avatar, body);

    messagesContainer.appendChild(article);

    scrollToLatest();
}


/* =====================================================
   5. CONVERSATION SIDEBAR
===================================================== */


function updateConversationList(conversation) {

    if (!conversationList || !conversation) return;

    const existing = Array.from(
        conversationList.querySelectorAll(".conversation-item")
    ).find(item => {
        return item.dataset.conversationId === conversation.uuid;
    });

    // Remove empty history message.
    const emptyMessage = conversationList.querySelector(".empty-history");

    if (emptyMessage) {
        emptyMessage.remove();
    }

    // Remove active state from other conversations.
    conversationList.querySelectorAll(".conversation-item").forEach(item => {
        item.classList.remove("active");
    });

    // Existing conversation.
    if (existing) {

        existing.classList.add("active");

        const title = existing.querySelector(".conversation-title");

        if (title) {
            title.textContent = conversation.title;
        }

        conversationList.prepend(existing);

        return;
    }

    // New conversation.
    const link = document.createElement("a");

    link.href = conversation.url;
    link.className = "conversation-item active";

    link.dataset.conversationId = conversation.uuid;

    const icon = document.createElement("span");

    icon.className = "conversation-icon";
    icon.textContent = "◈";

    const title = document.createElement("span");

    title.className = "conversation-title";
    title.textContent = conversation.title;

    link.append(icon, title);

    conversationList.prepend(link);
}


/* =====================================================
   6. COMPOSER MANAGEMENT
===================================================== */


function updateComposer() {

    if (!messageInput || !sendButton) return;

    const value = messageInput.value;

    // Optional character counter.
    if (characterCount) {
        characterCount.textContent = `${value.length}/8000`;
    }

    sendButton.disabled = (
        value.trim().length === 0 || isSubmitting
    );

    // Auto-resize textarea.
    messageInput.style.height = "auto";

    messageInput.style.height =
        `${messageInput.scrollHeight}px`;
}


function setSubmissionStatus(message, isError = false) {

    if (!submissionStatus) return;

    submissionStatus.textContent = message;

    submissionStatus.dataset.state = isError
        ? "error"
        : "normal";
}


/* =====================================================
   7. CSRF PROTECTION
===================================================== */


function getCSRFToken() {

    const csrfInput = messageForm
        ? messageForm.querySelector('[name="csrfmiddlewaretoken"]')
        : null;

    return csrfInput ? csrfInput.value : null;
}


/* =====================================================
   8. SERVER RESPONSE HANDLING
===================================================== */


async function parseResponse(response) {

    const contentType = response.headers.get("content-type") || "";

    if (!contentType.includes("application/json")) {

        const responseText = await response.text();

        console.error(
            "Unexpected server response:",
            response.status,
            responseText
        );

        throw new Error(
            response.status === 403
                ? "Request rejected. Check Django CSRF protection."
                : `Server returned an unexpected response (${response.status}).`
        );
    }

    const data = await response.json();

    if (!response.ok || !data.success) {

        const errors = data.errors
            ? Object.values(data.errors)
                .flat()
                .map(error => error.message)
                .join(" ")
            : data.error || data.message || "Message submission failed.";

        const error = new Error(errors);

        // Preserve partial data when the user's message was saved.
        error.payload = data;

        throw error;
    }

    if (
        !data.message ||
        !data.assistant_message ||
        !data.conversation
    ) {
        throw new Error(
            "The server returned incomplete conversation data."
        );
    }

    return data;
}


/* =====================================================
   9. MESSAGE SUBMISSION
===================================================== */


async function submitMessage(event) {

    event.preventDefault();

    if (
        !messageForm ||
        !messageInput ||
        !sendButton ||
        isSubmitting
    ) {
        return;
    }

    const content = messageInput.value.trim();

    if (!content) return;

    if (content.length > 8000) {
        setSubmissionStatus(
            "Your message exceeds the 8000-character limit.",
            true
        );
        return;
    }

    isSubmitting = true;

    updateComposer();

    setSubmissionStatus("Ava is thinking...");

    try {

        const formData = new FormData(messageForm);

        // Ensure the latest textarea value is submitted.
        formData.set("user_input", content);

        // Explicit CSRF header.
        const csrfToken = getCSRFToken();

        const headers = {
            "X-Requested-With": "XMLHttpRequest"
        };

        if (csrfToken) {
            headers["X-CSRFToken"] = csrfToken;
        }

        const response = await fetch(messageForm.action, {
            method: "POST",
            body: formData,
            headers: headers,
            credentials: "same-origin"
        });

        const data = await parseResponse(response);

        // Update the conversation UUID returned by Django.
        if (conversationUUID) {
            conversationUUID.value = data.conversation.uuid;
        }

        messageForm.dataset.conversationUuid =
            data.conversation.uuid;

        // Render both persisted messages immediately.
        renderMessage(data.message);
        renderMessage(data.assistant_message);

        // Update conversation history.
        updateConversationList(data.conversation);

        // Remove welcome screen.
        if (welcomeState) {
            welcomeState.remove();
        }

        // Update browser URL.
        if (data.conversation.url) {

            window.history.replaceState(
                {},
                "",
                data.conversation.url
            );
        }

        // Clear the composer after successful persistence.
        messageInput.value = "";

        setSubmissionStatus("");

    } catch (error) {

        console.error("Ava submission error:", error);

        // Handle cases where the user's message was saved
        // but Ava could not generate a response.
        const payload = error.payload;

        if (payload) {

            if (payload.conversation) {

                if (conversationUUID) {
                    conversationUUID.value = payload.conversation.uuid;
                }

                messageForm.dataset.conversationUuid =
                    payload.conversation.uuid;

                updateConversationList(payload.conversation);

                if (payload.conversation.url) {
                    window.history.replaceState(
                        {},
                        "",
                        payload.conversation.url
                    );
                }
            }

            if (payload.message && messagesContainer) {

                const alreadyRendered = Array.from(
                    messagesContainer.children
                ).some(element =>
                    element.dataset.messageId === String(payload.message.id)
                );

                if (!alreadyRendered) {
                    renderMessage(payload.message);
                }

                if (welcomeState) {
                    welcomeState.remove();
                }
            }
        }

        setSubmissionStatus(
            error.message || "An unexpected error occurred.",
            true
        );

    } finally {

        isSubmitting = false;

        updateComposer();

        messageInput.focus();
    }
}


/* =====================================================
   10. MESSAGE FORM EVENTS
===================================================== */


if (messageForm) {
    messageForm.addEventListener("submit", submitMessage);
}


if (messageInput) {

    messageInput.addEventListener("input", updateComposer);

    // Enter submits.
    // Shift + Enter inserts a new line.
    messageInput.addEventListener("keydown", event => {

        if (
            event.key === "Enter" &&
            !event.shiftKey &&
            !event.isComposing
        ) {

            event.preventDefault();

            if (!isSubmitting && sendButton && !sendButton.disabled) {

                if (messageForm.requestSubmit) {
                    messageForm.requestSubmit();
                } else {
                    // Fallback for older browsers.
                    messageForm.dispatchEvent(
                        new Event("submit", {
                            bubbles: true,
                            cancelable: true
                        })
                    );
                }
            }
        }
    });
}


/* =====================================================
   11. SUGGESTION PROMPTS
===================================================== */


const suggestionPrompts = {

    "Something on my mind":
        "There's something on my mind that I'd like to talk about.",

    "How I've been feeling":
        "I've been thinking about how I've been feeling lately.",

    "Just a little conversation":
        "I'd like to have a little conversation with you."
};


document.querySelectorAll(".suggestion-card").forEach(card => {

    card.addEventListener("click", () => {

        const heading = card.querySelector("strong");

        if (!heading || !messageInput) return;

        const prompt = heading.textContent.trim();

        messageInput.value =
            suggestionPrompts[prompt] || prompt;

        updateComposer();

        messageInput.focus();
    });
});


/* =====================================================
   12. SIDEBAR CONTROLS
===================================================== */


function closeSidebarPanel() {

    if (sidebar) {
        sidebar.classList.remove("open");
    }

    if (sidebarOverlay) {
        sidebarOverlay.classList.remove("active");
    }
}


if (openSidebar) {

    openSidebar.addEventListener("click", () => {

        if (sidebar) {
            sidebar.classList.add("open");
        }

        if (sidebarOverlay) {
            sidebarOverlay.classList.add("active");
        }
    });
}


if (closeSidebar) {
    closeSidebar.addEventListener("click", closeSidebarPanel);
}


if (sidebarOverlay) {
    sidebarOverlay.addEventListener("click", closeSidebarPanel);
}


/* =====================================================
   13. SCROLL MANAGEMENT
===================================================== */


function scrollToLatest() {

    if (!chatArea) return;

    requestAnimationFrame(() => {

        chatArea.scrollTo({
            top: chatArea.scrollHeight,
            behavior: "smooth"
        });
    });
}


/* =====================================================
   14. NAVIGATION CONTROLS
===================================================== */


const clearChatButton = document.getElementById("clearChat");
const newChatLink = document.getElementById("newChat");
const historyButton = document.getElementById("historyButton");


if (clearChatButton && newChatLink) {

    clearChatButton.addEventListener("click", () => {
        window.location.href = newChatLink.href;
    });
}


if (historyButton && conversationList) {

    historyButton.addEventListener("click", () => {

        if (
            window.matchMedia("(max-width: 768px)").matches &&
            sidebar &&
            !sidebar.classList.contains("open")
        ) {
            openSidebar?.click();
        }

        conversationList.scrollIntoView({
            behavior: "smooth",
            block: "nearest"
        });
    });
}


/* =====================================================
   15. INITIALIZATION
===================================================== */


updateComposer();

if (
    messagesContainer &&
    messagesContainer.children.length > 0
) {
    scrollToLatest();
}
