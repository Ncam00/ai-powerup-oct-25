# PromptKit

PromptKit gives Dev Academy students a lightweight home base for working with AI coding assistants during bootcamp. The focus is on reflection, question-driven learning, and teacher-curated activities that arrive throughout the course.

## Quick Start
1. Fork this repository to your own GitHub account.
2. When working on a challenge, clone your fork into the challenge and then add it to your git ignore file
```
git clone https://github.com/[your-username]/promptkit
echo 'promptkit' >> .gitignore
```
3. Install Gemini CLI: `npm install -g @google/gemini-cli` ([GitHub](https://github.com/google-gemini/gemini-cli))
4. Open the AI CLI of your choice (Gemini, Claude, Codex) and tell it: "read promptkit/protocols/setup.md to learn how to use PromptKit."
4. Choose a workflow:
   - `activate the tutor workflow` — have your AI explain concepts, debug, or explore new ideas with you.
   - `activate the reflect workflow` — capture what you accomplished and decide next learning goals alongside your AI.

## Repository Layout
- `activities/` — Instructor-supplied exercises. **Treat everything here as read-only.** You will merge new activities from the upstream repo as the course progresses.
- `notes/` — Your personal workspace for goals, reflections, and takeaways. Update these files whenever you finish a learning session.
- `protocols/` & `workflows/` — Minimal instructions your AI assistant runs. 

## Growing With PromptKit
As the bootcamp continues, instructors will unlock additional workflows and protocols. Keep this repo handy across your projects so you can reuse the same reflection habits, question prompts, and AI collaboration patterns everywhere you build.
