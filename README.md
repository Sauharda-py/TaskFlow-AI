# SQL Task Agent

A conversational AI task manager that allows you to interact with a SQLite database using **natural language**.

Instead of writing SQL queries, users can simply ask things like:

* "Show my pending tasks"
* "Add a task to buy groceries"
* "Mark task 3 as completed"
* "Search tasks about reports"
* "Delete task 5"

The application uses an LLM-powered SQL agent to translate natural-language requests into database operations while restricting the agent to the supported task-management operations.

## Features

* 💬 Natural-language interaction with tasks
* 🤖 LLM-powered SQL agent
* 🗄️ SQLite database
* ➕ Create tasks
* 🔍 Search and filter tasks
* ✏️ Update task status
* 🗑️ Delete tasks
* 📊 Live task statistics
* 🧠 Conversation memory
* 🎨 Custom Streamlit interface
* ⚡ Groq-powered inference
* 🏠 Optional Ollama support for local models

## Tech Stack

* **Python**
* **Streamlit** — Web interface
* **SQLite** — Task database
* **LangChain** — SQL database toolkit and LLM integration
* **LangGraph** — Agent and conversation state management
* **Groq** — LLM inference
* **Ollama** — Optional local LLM support

## How It Works

```text
User
  │
  ▼
Streamlit Chat Interface
  │
  ▼
Natural Language Request
  │
  ▼
LLM-powered SQL Agent
  │
  ▼
SQL Database Toolkit
  │
  ▼
SQLite (my_tasks.db)
  │
  ▼
Task Data
  │
  ▼
Natural Language Response
```

The application defines a `tasks` table containing:

```sql
id
title
description
status
created_at
```

The allowed task statuses are:

```text
Pending
In Progress
Completed
```

The agent is instructed to perform only supported task operations such as creating, reading, updating, and deleting tasks.

## Project Structure

```text
sql-task-agent/
│
├── main.py
├── pyproject.toml
├── requirements.txt
├── README.md
├── .gitignore
├── .python-version
│
└── my_tasks.db        # created locally
```

The SQLite database is generated locally and should not be committed to the repository.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/sql-task-agent.git
cd sql-task-agent
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

**Linux/macOS:**

```bash
source .venv/bin/activate
```

**Windows:**

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
```

Do **not** commit your `.env` file to GitHub.

You can create an `.env.example` file for other users:

```env
GROQ_API_KEY=
```

## Running the Application

Start the Streamlit application with:

```bash
streamlit run main.py
```

The application will open in your browser.

## Example Queries

You can interact with the agent using natural language.

### View tasks

```text
Show my pending tasks
```

### Create a task

```text
Add task: Buy groceries
```

### Search

```text
Search tasks about report
```

### Update

```text
Mark task 3 as completed
```

### Delete

```text
Delete task 5
```

## Database

The application uses SQLite with a `tasks` table:

```text
tasks
├── id
├── title
├── description
├── status
└── created_at
```

The database is created automatically when the application starts.

## LLM Configuration

The default model uses **Groq** through LangChain.

An optional Ollama configuration is also included in the project, allowing the application to be adapted to a locally hosted model.

## Security and Database Accuracy

The agent is given explicit rules for database operations and is instructed to:

* Use only supported SQL operation patterns.
* Use only valid task statuses.
* Never fabricate database rows.
* Report exactly the rows returned by the database.
* Avoid displaying raw SQL queries to the user.

## Future Improvements

* User authentication
* Multiple task lists
* Due dates and reminders
* Task priorities
* PostgreSQL/MySQL support
* Better confirmation for destructive operations
* Local LLM configuration through Ollama
* Deployment to Streamlit Community Cloud

## License

This project is available under the MIT License.