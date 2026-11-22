# SoulNote
### A little space for your thoughts and perhaps a better understanding of yourself.

I've always found it interesting how much goes on inside our minds that we never really get to express. Sometimes we write things down just to get them out of our heads. Other times, we write because we're trying to understand something we can't quite put into words.

That's partly where **SoulNote** comes from.

SoulNote is a personal project I'm building with Python and Django. At its core, it's an emotional diary, but I don't necessarily want it to remain just another journaling application.

I'm exploring the possibility of bringing Large Language Models (LLMs) into the experience, allowing the application to do more than store entries. Ideally, it could understand some of the context behind what someone writes, connect thoughts across different days and offer reflections that might help them see things from another perspective.

I'm still figuring out exactly how far I can take this idea, but I think there's something interesting here.

---

## 🌱 What I'm Trying to Build

I don't want SoulNote to be a place where people simply write something, press save and forget about it.

I'd like it to become a space where people can gradually make sense of their own experiences.

Some things I'm exploring include:

- **Personal Journaling:** A private space where I can write freely, preserve experiences and revisit thoughts whenever I want.
- **Emotional Understanding:** Exploring how NLP and LLMs can identify emotions, intentions and themes within written entries.
- **AI Reflections:** I'd like the AI to respond thoughtfully to entries, not just classify them as happy, sad, or angry.
- **Contextual Memory:** What if the AI could remember relevant things from previous entries and use them to understand something I'm writing today?
- **Personal Insights:** Perhaps, over time, it could help reveal recurring thoughts, emotional patterns and changes in perspective.
- **A Personal History:** A way to look back at who I was, what I was thinking and how some of those thoughts have changed.

These are ideas I'm working towards, not promises that everything is already implemented.

## 🛠️ Technology Stack

I'm building the foundation with technologies I'm comfortable working with and others I want to explore further.

| Component | Technology |
|---|---|
| Language | Python 3.8+ |
| Backend | Django 4.2 LTS |
| Database | SQLite / MariaDB |
| Frontend | HTML, Tailwind CSS |
| Templating | Django Template Language |
| Authentication | Django Authentication System |
| AI Integration | Large Language Models (planned) |
| Contextual Memory | RAG (planned) |

### Why Django?

I chose Django because I wanted a structured backend with authentication, database management, session handling and security mechanisms already available.

I could probably build the application with Flask, but Django gives me a more integrated foundation, especially as I start thinking about user accounts, private entries and eventually AI-related services.

---

## 🔐 Privacy Matters

There's something different about storing someone's personal thoughts compared to storing ordinary application data.

Diary entries can contain things people might never be comfortable sharing elsewhere. I don't think privacy should be an afterthought in a project like this.

For now, I'm relying on Django's built-in security mechanisms and gradually improving the application's security architecture.

Some of the things I've implemented or am working with include:

- **Authentication:** User registration, login and logout.
- **Password Security:** Django's password hashing mechanisms.
- **Session Management:** Session-based authentication.
- **CSRF Protection:** Protection against Cross-Site Request Forgery.
- **User Isolation:** Ensuring users can only access their own diary entries.
- **Form Validation:** Django ModelForms for validating submitted information.
- **Audit Metadata:** Recording client IP metadata during entry submissions.

I also want to be particularly careful about how diary content is eventually passed to external AI services. Just because an AI model can process personal information doesn't necessarily mean it should receive everything.

There's still more to think through here.

---

## 🧠 The Part I'm Most Curious About: AI Reflections

This is probably the part of SoulNote that interests me the most.

I've been exploring LLMs, NLP and Retrieval-Augmented Generation (RAG) and I'm curious about how these technologies could work together in a personal journaling application.

Consider this:

Someone writes on Monday:

> I've been feeling exhausted lately. I don't really know why, but everything seems a little overwhelming.

On Wednesday:

> I finally talked to someone about what's been bothering me. I think I needed that.

And on Friday:

> Things aren't necessarily perfect, but I feel a little better.

Individually, these are just three entries.

But together, they might reveal something worth reflecting on.

I'd like SoulNote to eventually recognise connections like these, rather than treating every entry as an entirely separate conversation.

### How I Imagine It Working

The architecture I'm currently considering looks something like this:

1. **Entry Processing:** A user writes and saves a diary entry.
2. **Emotional Analysis:** An LLM examines the text for possible emotions, intentions and themes.
3. **Context Retrieval:** A retrieval system searches relevant previous entries, potentially using embeddings and vector similarity.
4. **Reflection Generation:** The LLM receives the current entry alongside relevant historical context and generates a response.
5. **Long-Term Insights:** Over time, the application could identify recurring themes and possible changes in emotional patterns.

I'm considering RAG for the memory component because I don't think simply sending an entire diary history to an LLM would be practical or particularly efficient.

I'm also aware that emotional interpretation isn't an exact science. An AI might misunderstand someone's words, miss sarcasm, or make assumptions that aren't necessarily true.

I'd rather have a system that acknowledges uncertainty than one that confidently tells someone how they feel.

And importantly, SoulNote isn't intended to diagnose mental-health conditions or replace professional support. Its purpose is reflection and self-understanding.

---

## 🚀 Getting Started

If you'd like to explore the project locally, here's how to get started.

### Prerequisites

- Python 3.8 or higher.
- pip.
- Git.

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd soulnote
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it:

**Windows**
```bash
venv\Scripts\activate
```

**Linux / macOS**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply Migrations

```bash
python manage.py migrate
```

### 5. Create an Administrator

```bash
python manage.py createsuperuser
```

### 6. Run the Application

```bash
python manage.py runserver
```

Then visit:

`http://127.0.0.1:8000/`

---

## 🗺️ What's Next?

SoulNote is still evolving. I have a few things in mind, although some architectural decisions may change as I experiment and learn more.

| Feature | Status |
|---|---|
| Django application foundation | In progress |
| User authentication | Implemented |
| Diary entry management | Implemented |
| User data isolation | In progress |
| AI emotion analysis | Planned |
| LLM-powered reflections | Planned |
| RAG-based contextual memory | Planned |
| Long-term emotional insights | Planned |

I'd also like to experiment with smaller language models, different embedding models and possibly locally hosted inference.

I'm not entirely sure which combination will work best yet. That is part of the exploration.

---

## 🤝 A Little About the Project

I'm building SoulNote partly because I'm interested in AI and the possibilities of making language models more context-aware and useful in everyday applications.

I'm particularly interested in the intersection of human language, emotional expression, memory and machine learning.

There are plenty of technical challenges here, from retrieval accuracy to hallucinations, privacy and the limitations of emotion recognition. I don't expect to solve all of them immediately.

For now, I'm more interested in experimenting, learning and seeing how far I can take the idea.

If you're interested in Django, Python, NLP, LLMs, or AI-powered applications, feel free to explore the project or share your thoughts.

---

### One thought before you leave.

We write things down for different reasons. Sometimes to remember, sometimes to forget and sometimes because we don't yet understand what we're feeling.

Perhaps, with the right tools, those little fragments of thought could help us understand a bigger picture.

**That's what I'm hoping to explore with SoulNote.**

*SoulNote — Your thoughts, your story, still unfolding.*
