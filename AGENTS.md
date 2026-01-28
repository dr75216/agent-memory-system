# AGENTS.md - Golden Rules for Building Agent Memory System

## Project Goal
Build a simple CLI tool for AI agent memory. JSONL storage, Git-backed, 
basic issue tracking. ~500 lines total Python. Keep it simple.

## ALWAYS Do This

### Task Management
- Read this file at start of EVERY session
- Work on ONE specific task at a time (no nested planning)
- Ask "what should I work on?" if unclear
- Update progress after each task

### Verification
- Run tests after EVERY code change
- Actually RUN the code, don't just say "it works"
- Show me actual terminal output
- Commit only when tests pass

### Git Discipline  
- Commit after completing each small task (every 10-15 min)
- Commit message format: "feat: <what>" or "fix: <what>"
- Never commit broken code
- Never commit with failing tests

## NEVER Do This

### Planning Anti-Patterns
- ❌ NEVER create new plan files (plan.md, phase-X-plan.md, etc.)
- ❌ NEVER break tasks into "phases" unless I explicitly ask
- ❌ NEVER create nested sub-tasks
- ❌ NEVER declare "project complete" without my confirmation

### Code Anti-Patterns
- ❌ NEVER say "tests pass" without actually running them
- ❌ NEVER skip error handling
- ❌ NEVER commit commented-out code

## Current Task List
- [ ] Project structure setup
- [ ] Basic data schema design
- [ ] Create CLI skeleton
- [ ] Implement 'create' command
- [ ] Implement 'list' command
- [ ] Implement 'show' command
- [ ] Implement 'update' command
- [ ] Implement 'done' command
- [ ] Add dependency tracking
- [ ] Implement 'ready' command
- [ ] Add git auto-commit
- [ ] Write documentation

## Remember
This is a learning project. Keep it simple.
