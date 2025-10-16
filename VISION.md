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
*   **Intelligent Context Dumps** to the LLM, enabling semantic search and powerful reasoning over all course materials.

It moves the user from being an "information puller" to a "decision maker."

---

## Core Features (Revised)

### 1. The Daily Briefing (Assignments & Events)

*   **Description:** This is the cornerstone feature, providing a complete, prioritized summary of upcoming academic deadlines and campus life events.
*   **Interaction:** The user prompts, "What's my daily briefing?" The Co-Pilot responds with a rich, interactive component that displays:
    *   **High-Priority Tasks:** Assignments and assessments due within the next 24-48 hours.
    *   **Upcoming Events:** A unified calendar view of class events, club meetings, and school-wide deadlines.
*   **Example Prompts:**
    *   `"What's my briefing?"`
    *   `"What do I need to worry about today?"`

### 2. The Universal Resource Finder (LLM-Native Search)

*   **Description:** This feature replaces manual clicking through course folders. The Co-Pilot provides the LLM with a complete, structured context of all course materials (links, files, assignments, notes), allowing the AI to perform a semantic search and reasoning based on content and intent.
*   **Interaction:** The user asks a question about a resource. The Co-Pilot calls a "context dump" tool, which returns the entire course material structure. The LLM then reasons over this data and returns the correct link and context.
*   **Example Prompts:**
    *   `"Where is the syllabus for AP English?"`
    *   `"Find the PDF about the derivative in my Calculus class."`
    *   `"What resources do I have for the Hamlet unit?"`

### 3. The Intelligent Update Digest

*   **Description:** This solves the "Signal vs. Noise" problem by synthesizing the Schoology feed and prioritizing announcements from teachers and administrators over social chatter. It tracks which updates have been seen to provide a true "What's New" experience.
*   **Interaction:** The user asks, "Any new announcements?" The Co-Pilot queries its stateful mirror and returns only the posts received since the last interaction, often summarizing the most important items.
*   **Example Prompts:**
    *   `"What are the key announcements today?"`
    *   `"Any updates from the US Student Notices group?"`

### 4. The Performance Dashboard (Future)

*   **Description:** Transforms reactive grade checking into a proactive and insightful experience by tracking grade changes and providing performance context.
*   **Interaction:** The user asks, "How are my grades?". The Co-Pilot renders an interactive component showing new grade alerts, class averages, and performance trends (`↑` or `↓`).

---

