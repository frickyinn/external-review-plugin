# ask-codewhale Skill Design

Date: 2026-06-02

## Goal

Create a repo-local `ask-codewhale` Codex skill for asking the local CodeWhale coding agent for cross review, second opinions, and simple delegated tasks. The skill should closely mirror the structure and contract of OMX `ask`, while keeping ask-codewhale-owned artifacts out of `.omx/`.

## Source-of-truth boundaries

- Reference behavior: OMX `ask` skill at `https://github.com/Yeachan-Heo/oh-my-codex/blob/main/skills/ask/SKILL.md` and the installed local copy at `/Users/frick/.codex/skills/ask/SKILL.md`.
- Skill authoring guidance: `/Users/frick/.codex/skills/writing-skills/SKILL.md`.
- Product output namespace: `.ask-codewhale/`.
- OMX runtime namespace: `.omx/`; do not write ask-codewhale artifacts there.

## Recommended approach

Use a small, repo-local skill document plus a local CodeWhale CLI execution convention.

Rejected approaches:

1. A helper script wrapper: useful for automation, but heavier than the requested skill and more fragile around shell quoting.
2. Extending `omx ask codewhale`: closest UX to OMX, but outside the repo-local scope and would require changing OMX or global install behavior.

## Architecture

- `skills/ask-codewhale/SKILL.md` is the canonical source file.
- `.codex/skills/ask-codewhale` is a symlink to `../../skills/ask-codewhale`, installing the skill for this repo without touching global skills.
- `.ask-codewhale/artifacts/` stores CodeWhale execution evidence and dogfood outputs.
- No new dependencies are introduced.
- The repo is initialized with git so design, implementation, and dogfood evidence can be audited.

## Skill behavior

The skill supports the user-facing workflow:

```bash
$ask-codewhale <question or task>
```

The skill instructs Codex to use local CodeWhale commands:

```bash
codewhale exec "<question or task>"
codewhale exec --auto "<simple delegated task>"
codewhale review "<review target>"
```

Command selection:

- Use `codewhale exec` for cross review, second opinions, plan review, code review prompts, and focused questions.
- Use `codewhale exec --auto` only when the user explicitly wants CodeWhale to perform a simple tool-backed delegated task.
- Use `codewhale review` when a git-diff review is the natural target and a usable diff exists.
- Do not silently switch to MCP, remote providers, or another coding agent if `codewhale` is missing.

## Artifact contract

After each local CodeWhale execution, save an artifact to:

```text
.ask-codewhale/artifacts/ask-codewhale-<slug>-<timestamp>.md
```

Minimum sections:

1. Original user task
2. Backend and final prompt sent to CodeWhale
3. Raw CodeWhale output
4. Concise summary
5. Action items / next steps

Dogfood artifacts use the same directory and are intended to be committed for the initial proof run.

## Error handling

- If `codewhale` is not installed, explain that the local CLI is required and stop without substituting another provider.
- If CodeWhale exits nonzero, still write an artifact containing the command, exit code, stdout/stderr, summary, and next steps.
- If the task requires filesystem or shell tool use but the user has not asked for delegation/tool-backed execution, stay with non-auto `codewhale exec`.
- If git review is requested without a git repo or diff, explain the missing review target and fall back to `codewhale exec` only if a prompt review target exists.
- Treat CodeWhale output as advisor input, not final truth; Codex remains responsible for synthesis and follow-up decisions.

## Verification plan

1. Confirm symlink install:

   ```bash
   test -L .codex/skills/ask-codewhale
   readlink .codex/skills/ask-codewhale
   ```

2. Confirm skill frontmatter contains valid `name` and `description` fields.
3. Run one dogfood review asking CodeWhale to review this repo's plan or skill implementation.
4. Save the dogfood output under `.ask-codewhale/artifacts/`.
5. Read the artifact and apply any clear, low-risk improvements.
6. Verify git status and the committed evidence.

## Scope exclusions

- No global `~/.codex/skills` installation.
- No OMX runtime state changes for ask-codewhale artifacts.
- No new wrapper script unless future dogfood proves the manual artifact contract is too error-prone.
- No provider fallback if CodeWhale is unavailable.

## Self-review

- No placeholders remain.
- Artifact namespace is `.ask-codewhale/`, not `.omx/`.
- The design is focused on one skill and one repo-local install path.
- Error handling keeps CodeWhale as a local advisor and preserves Codex ownership of final decisions.
