---
name: ask-codewhale
description: "Use when asking the local CodeWhale coding agent for cross review, second opinions, plan/code critique, or a simple delegated coding-agent task"
---

# Ask CodeWhale

Use the locally installed CodeWhale CLI as an external coding-agent advisor for focused questions, cross review, plan/code critique, or simple delegated tasks. This skill follows the local-advisor shape of OMX `ask` while keeping ask-codewhale artifacts in this repo's own namespace.

## Usage

```bash
$ask-codewhale <question or task>
codewhale exec "<question or task>"
codewhale exec --auto "<simple delegated task>"
codewhale review "<review target>"
```

## Command selection

- Use `codewhale exec "{{ARGUMENTS}}"` for cross review, second opinions, focused questions, plan review prompts, and code review prompts.
- Use `codewhale exec --auto "{{ARGUMENTS}}"` only when the user explicitly asks CodeWhale to perform a simple tool-backed delegated task.
- Use `codewhale review "{{ARGUMENTS}}"` when a git-diff review is the natural target and a usable repo/diff exists.
- If git review is requested but there is no git repo/diff and no prompt review target, stop with a precise missing-target message. If a prompt review target exists, use `codewhale exec` instead.

## Local CLI requirement

Prefer the local binary:

```bash
codewhale exec "{{ARGUMENTS}}"
```

If `codewhale` is missing, explain that the local CodeWhale CLI is required. Do not silently switch to an MCP server, remote provider, Claude, Gemini, Codex, or another coding agent.

## Artifact requirement

After local execution, save a markdown artifact to:

```text
.ask-codewhale/artifacts/ask-codewhale-<slug>-<timestamp>.md
```

Minimum sections:

1. Original user task
2. Backend and final prompt sent to CodeWhale
3. Raw CodeWhale output
4. Concise summary
5. Action items / next steps

If CodeWhale exits nonzero after execution begins, still save an artifact with the command, exit code, stdout/stderr, concise summary, and next steps. Treat CodeWhale output as advisory evidence; Codex remains responsible for synthesis and follow-up decisions.

Task: {{ARGUMENTS}}
