# Project Workflow

Use this workflow when building new features or starting new projects.

## Phase 1: Planning 📋

### 1. Define Requirements
- What problem are we solving?
- Who is the target user?
- What are the success criteria?
- Any technical constraints or requirements?

**Use template:** `templates/prd.md` for larger projects

### 2. Break Down Tasks
- List specific, testable outcomes
- Order tasks by dependencies
- Estimate complexity (Simple/Medium/Complex)
- Identify potential challenges

**Use template:** `templates/task-breakdown.md`

### 3. Get Approval
- Review plan with human
- Clarify any uncertainties
- Adjust scope if needed

## Phase 2: Implementation 🔨

### 4. Setup Environment
- Ensure all dependencies are available
- Create necessary files/directories
- Set up testing framework if needed

### 5. Implement Task by Task
For each task:
- [ ] Implement the minimum viable solution
- [ ] Write/update tests
- [ ] Verify functionality manually
- [ ] Commit changes with clear message
- [ ] Get approval before moving to next task

### 6. Integration & Polish
- [ ] Ensure all parts work together
- [ ] Add error handling
- [ ] Improve user experience
- [ ] Update documentation

## Phase 3: Review 🔍

### 7. Final Testing
- [ ] Run all tests
- [ ] Test edge cases
- [ ] Performance check if relevant

### 8. Documentation
- [ ] Update README if needed
- [ ] Add code comments for complex logic
- [ ] Document any setup or usage instructions

### 9. Reflection
- What went well?
- What could be improved?
- What did we learn?
- Any technical debt to address later?

## When to Use This Workflow

✅ Building new features
✅ Starting new projects  
✅ Major refactoring efforts
✅ When requirements are complex or unclear

❌ Quick bug fixes (use Debug Workflow)
❌ Learning/exploration (use Learning Workflow)
❌ Simple one-off tasks