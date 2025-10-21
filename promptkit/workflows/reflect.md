# Reflect Workflow (AI-Facing)

## Mission
Help the student capture what happened during a study block, document learnings, and choose follow-up actions.

## Preconditions
- Student has recently completed a session (self-study, tutoring, activity work, etc.).
- `notes/progress-journal.md` is available for logging results.

If the session is still in progress, ask the user if they would like to finish the active workflow before reflecting.

## Workflow Steps
1. **Session Snapshot & Draft Entry**
   - Prompt the user to summarize recent activity (assist them by providing some suggestions/reminders by reviewing `git log` or recent file changes since the last reflection). This summary should be concise and neutral, forming the 'Activity or Question' and 'What I Asked / Did' columns.
   - Draft a journal entry (Date, Activity, What I Asked/Did) based on this summary and the current date.
   - Present this draft with bullet points to the user for review and input.

2. **Capture Learnings**
   - Offer the following reflection prompts to the user to guide their thinking for the 'What I Learned' column:
     - What surprised me today?
     - How did the Tutor workflow help?
     - What should I bring to the next stand-up or mentoring session?
   - Prompt the user for their key takeaways, discoveries, or code insights based on these prompts or their own thoughts.
   - Present a summary of the entry as bullet points to the user for approval.

3. **Plan Next Actions & Finalize Entry**
   - Work with the student to define concrete next steps (e.g., revisit an Activity, write tests, ask a Tutor question).
   - If new goals or questions emerged, remind them to update `notes/learning-plan.md` (you may open the file to guide them).
   - Combine the drafted session snapshot, user's reflections, and next action into a complete table row.
   - Present a summary of the combined entry as bullet points to the user for approval.
   - Use the `replace` tool to insert this new row into the `notes/progress-journal.md` table, replacing the first empty row. If no empty rows remain, append the row to the end.

4. **Close the Loop**
   - Summarise the session and confirm the next workflow or task (another Tutor session, independent practice, or a break).
   - Reinforce that their notes are the source of truth for future sessions.


## Completion Criteria
- `notes/progress-journal.md` contains a new entry with learnings and next actions.
- Any new goals/questions have been copied over to `notes/learning-plan.md` if needed.
- No other files have been modified without approval
- Student knows what they will do next and which workflow to trigger when ready.
