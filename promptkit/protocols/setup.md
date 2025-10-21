# Setup Protocol 

## Purpose
Ensure the student’s active CLI (Gemini, Claude, Codex) knows about PromptKit by updating the matching root-level briefing file **only when PromptKit guidance is missing**.

## Preconditions
- You are running in the repository root and it contains the `promptkit/` directory of the (`ls` should include with `promptkit`).
- The repository root may contain `AGENTS.md`, `GEMINI.md`, or `CLAUDE.md` depending on the CLI.
- Shell commands (`pwd`, `ls`, `rg`, `cat`, `tee`) are available.

If any prerequisite fails, pause and ask the student or instructor what to do before continuing.

## Steps
1. **Confirm Location**
   - Run `ls .` to ensure you are in the repository root and you can see which briefing files exist (`AGENTS.md`, `GEMINI.md`, `CLAUDE.md`).

2. **Detect CLI Briefing Files**
   - Build a list of briefing files that exist in the repository root (any combination of `../GEMINI.md`, `../CLAUDE.md`, `../AGENTS.md`).
   - If none are present, report the issue to the student and stop.

3. **Check for Existing PromptKit Instructions**
   - For each file in the list, run `rg -q "PromptKit" ../<CLI_FILE>`.
   - Track which files already contain PromptKit guidance. If **all** files already mention PromptKit, finish the protocol and tell the student no changes were required.

4. **Append PromptKit Briefing (Only Where Missing)**
   - Prepare the following briefing block:
     ```text
     ## PromptKit Quick Reference
     - Review the available artefacts when the student requests them:
       - Protocol: `promptkit/protocols/setup.md` — instructions for updating these CLI briefings.
       - Workflow: `promptkit/workflows/tutor.md` — guide for tutoring/explanation sessions.
       - Workflow: `promptkit/workflows/reflect.md` — guide for documenting outcomes and next steps.
     - Student notes live in `promptkit/notes/`; instructor Activities are in `promptkit/activities/` (read-only).
     - When new workflows arrive, expect additional files under `promptkit/workflows/`.
     ```
   - For each file lacking PromptKit instructions, append the block using a here-doc, e.g.
     ```bash
     cat <<'END_PROMPTKIT' >> ../<CLI_FILE>
     ...content...
     END_PROMPTKIT
     ```

5. **Confirm Success**
   - For each file that was updated, display the tail (e.g., `tail -n 20 ../<CLI_FILE>`) to verify the new PromptKit block appears.
   - Inform the student which files were updated.
   - Load the tutoring instructions before beginning:
     ```
     cat promptkit/workflows/tutor.md
     ```
   - Immediately trigger the Tutor workflow so the student starts with guided questions:
     ```
     workflow tutor
     ```

## Completion Criteria
- Every detected CLI briefing file either already contained, or now contains, a PromptKit quick reference.
- The tutor workflow is activated, ensuring the student begins with guided questioning.
