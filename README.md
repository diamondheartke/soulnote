# SoulNote — AI-Powered Emotional Diary

SoulNote is a secure, private, and empathetic journaling web application built with **Python Django**. It allows users to record their daily thoughts, track emotional trends, and prepare for AI-driven emotional reflection and feedback.

---

## 🛠️ Tech Stack

*   **Backend:** Python 3.8+ / Django 4.2 LTS
*   **Database:** SQLite (Local development) / MariaDB (Production-ready)
*   **Frontend:** Tailwind CSS (via Play CDN), Django Template Language (DTL)
*   **Authentication:** Django's built-in secure auth system (Password hashing, session-based auth, CSRF protection)

---

## ✨ Features

*   **Secure User Authentication:** Custom registration, login, and logout views ensuring user entries remain completely private to their account.
*   **ModelForm Validation:** Clean, automated form handling and data validation bridging Django models directly to user inputs.
*   **Forensic Audit Metadata:** Automatically logs the client's IP address with every entry submission for security auditing and tracking.
*   **LLM-Ready Schema:** Database models pre-configured with fields to store future AI-detected emotions and reflective responses.
*   **Responsive UI:** Minimalist, calming aesthetic styled with Tailwind CSS.

---

## 🚀 Getting Started Locally

Follow these instructions to get a copy of the project up and running on your local machine for development and testing.

### Prerequisites
*   Python 3.8 or higher installed on your system.
*   `pip` (Python package manager).

### Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/soulnote.git](https://github.com/your-username/soulnote.git)
   cd soulnote
