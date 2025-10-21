# Debug Workflow

Use this workflow when investigating and fixing bugs or unexpected behavior.

## Phase 1: Investigation 🔍

### 1. Document the Problem
- What is the expected behavior?
- What is actually happening?
- When did this start occurring?
- Steps to reproduce the issue
- Any error messages or logs

### 2. Gather Context
- [ ] Read relevant error messages/logs in detail
- [ ] Identify which files/functions are involved
- [ ] Check recent changes that might be related
- [ ] Look for similar issues in past commits

### 3. Form Hypotheses
- List 2-3 possible causes
- Order by likelihood
- Consider both obvious and subtle causes

## Phase 2: Testing Hypotheses 🧪

### 4. Test Each Hypothesis
For each hypothesis:
- [ ] Design a test to confirm or reject it
- [ ] Execute the test
- [ ] Document results
- [ ] Move to next hypothesis if rejected

### 5. Isolate the Root Cause
- [ ] Create minimal reproduction case
- [ ] Confirm the exact line/logic causing the issue
- [ ] Understand why it's happening

## Phase 3: Resolution 🔧

### 6. Design the Fix
- Consider multiple solution approaches
- Choose the safest and most maintainable option
- Plan how to test the fix

### 7. Implement the Fix
- [ ] Make minimal changes necessary
- [ ] Add tests to prevent regression
- [ ] Verify fix works in original context
- [ ] Test edge cases

### 8. Validation
- [ ] Run full test suite
- [ ] Manual testing of fixed functionality
- [ ] Check for any side effects
- [ ] Confirm original reproduction case is resolved

## Phase 4: Documentation 📝

### 9. Document the Solution
- [ ] Clear commit message explaining the bug and fix
- [ ] Update code comments if logic was confusing
- [ ] Add any necessary documentation
- [ ] Note any technical debt created or resolved

### 10. Reflection
- How could this bug have been prevented?
- Any patterns to watch for in the future?
- Improvements to testing or development process?

## When to Use This Workflow

✅ Unexpected behavior or errors
✅ Test failures
✅ Performance issues
✅ User-reported bugs

❌ New feature development (use Project Workflow)
❌ Learning about unfamiliar code (use Learning Workflow)

## Common Bug Categories

**Logic Errors:** Incorrect conditions, wrong calculations
**State Issues:** Race conditions, uninitialized variables
**Integration Problems:** API changes, dependency conflicts  
**Environment Issues:** Configuration, permissions, paths

