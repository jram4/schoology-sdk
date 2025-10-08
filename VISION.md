# `VISION.md`

## Project: Schoology Co-Pilot

### High-Level Vision

The Schoology Co-Pilot is a conversational agent, built on the OpenAI Apps SDK, that transforms the fragmented and noisy Schoology platform into a unified, proactive, and actionable assistant for students. It eliminates the cognitive load of navigating countless pages and feeds by synthesizing all critical academic and campus life information into a single, intelligent dialogue within ChatGPT.

### The Problem with the Current State

Schoology serves as a digital repository but forces the student to be a reactive information hunter. The core pain points are:

*   **Information Silos:** Critical data is scattered across a dozen separate Course and Group pages, with no single source of truth.
*   **Signal vs. Noise:** The main feed is a chronological firehose where urgent deadlines, new grades, and low-priority announcements have the same visual weight.
*   **Reactive Workflow:** The student must manually and repeatedly pull information, check for updates, and synthesize connections in their own mind.

### The Co-Pilot Vision

The Schoology Co-Pilot will be an intelligent partner that manages the logistics of student life, allowing the student to focus on learning and participation. It will provide:

*   A **unified view** of all courses, groups, grades, and deadlines.
*   **Proactive insights** that surface what's important, right now.
*   **Actionable components** that turn information into plans and actions directly within the chat.

It moves the user from being an "information puller" to a "decision maker."

---

## Core Features

### 1. The Daily Briefing

*   **Description:** This is the cornerstone feature. At any time, the user can ask for a complete, prioritized summary of their academic and campus life. The Co-Pilot will scan all courses and groups to synthesize a single, digestible intelligence report.
*   **Interaction:** The user prompts, "What's my daily briefing?" or "What's up for today?". The Co-Pilot responds with a rich, interactive component that displays:
    *   **High-Priority Tasks:** Assignments and assessments due within the next 24-48 hours.
    *   **Key Announcements:** An intelligent summary of important new posts, filtering out social chatter.
    *   **Upcoming Events:** A unified calendar view of class events, club meetings, and school-wide deadlines.
*   **Example Prompts:**
    *   `"What's my briefing?"`
    *   `"What do I need to worry about today?"`
    *   `"Give me a rundown of the week."`

### 2. The Performance Dashboard

*   **Description:** This feature transforms the stressful, reactive process of checking grades into a proactive and insightful experience. It tracks grade changes, provides context, and helps the user understand their academic standing at a glance.
*   **Interaction:** When a new grade is posted, the Co-Pilot can proactively alert the user. The user can also ask, "How are my grades?". The Co-Pilot will render an interactive component showing:
    *   **New Grade Alerts:** A prominent notification for any recently posted grade.
    *   **Class Averages:** A clean list of current averages for all courses.
    *   **Performance Trends:** Simple visual indicators (e.g., `↑` or `↓`) to show if a grade has improved or declined since the last new entry. The user can then ask follow-up questions like, `"Why did my Physics grade change?"` to get a breakdown.
*   **Example Prompts:**
    *   `"Any new grades?"`
    *   `"How am I doing in AP Calculus?"`
    *   `"Show me my current academic performance."`

### 3. The Interactive Planner

*   **Description:** This feature turns the static "To-Do" list into a dynamic, personal planning workspace. It allows the user to organize their assignments and personal tasks, turning intent into a concrete plan.
*   **Interaction:** The user prompts, "Help me plan my night." The Co-Pilot fetches all upcoming assignments and presents them in a `fullscreen` Kanban-style board component. The user can:
    *   **Prioritize:** Drag and drop tasks into "To Do," "In Progress," and "Done" columns.
    *   **Augment:** Add their own personal tasks (e.g., "Study for SAT," "Finish college essay").
    *   **Persist:** The state of the board is saved, so the plan is always up-to-date and can be revisited in any future conversation.
*   **Example Prompts:**
    *   `"Let's plan my week."`
    *   `"I have 3 hours to work, what should I focus on?"`
    *   `"Show me my current plan."`