# ask-codewhale dogfood review

## Original user task

Dogfood this repo by asking CodeWhale to review the ask-codewhale plan/code.

## Backend and final prompt sent to CodeWhale

Backend: `codewhale`

Command: `codewhale exec <prompt>`

```text
Review this repo-local Codex skill implementation for ask-codewhale. This is a read-only cross review; do not propose broad scope expansion.

Success criteria:
- Strictly follows the approved design.
- Mirrors OMX ask local advisor shape.
- Frontmatter follows writing-skills: description starts with Use when and is trigger-only, not a workflow summary.
- Installs via .codex/skills/ask-codewhale symlink to ../../skills/ask-codewhale.
- CodeWhale product artifacts go only under .ask-codewhale/artifacts/, not .omx/.
- Missing codewhale has no fallback provider.

Symlink target: ../../skills/ask-codewhale

--- skills/ask-codewhale/SKILL.md ---
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


--- approved design spec ---
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


--- test spec ---
# Test spec: `ask-codewhale`

## Verification steps

1. Verify repo-local install:
   - `test -L .codex/skills/ask-codewhale`
   - `readlink .codex/skills/ask-codewhale`
2. Verify skill metadata and writing-skills semantics:
   - `skills/ask-codewhale/SKILL.md` has valid `name` and `description`
   - `name` uses letters, numbers, and hyphens only
   - `description` starts with `Use when`, is trigger-only, and does not summarize the workflow
3. Verify command routing by inspecting skill rules:
   - cross review, second opinions, focused questions, plan/code review prompts select `codewhale exec`
   - natural git-diff review with an available diff selects `codewhale review`
   - explicit tool-backed/simple delegated task intent selects `codewhale exec --auto`
4. Run one dogfood CodeWhale review of the plan or skill implementation
5. Confirm artifact written under:
   - `.ask-codewhale/artifacts/ask-codewhale-<slug>-<timestamp>.md`
6. Confirm no product artifacts were written under `.omx/`
7. Verify the no-fallback failure contract:
   - use a controlled `PATH` that hides `codewhale`, or an equivalent safe command-availability probe
   - assert the documented behavior says the local CLI is required
   - assert no fallback backend/provider is invoked or suggested as an automatic substitute
8. Verify no-review-target behavior:
   - if git review is requested but there is no git repo/diff and no prompt review target, the skill instructs Codex to stop with a precise missing-target message
   - fallback to `codewhale exec` is allowed only when a prompt review target exists
9. Confirm git status only reflects intended repo-local skill/artifact changes and non-product OMX runtime state

## Test matrix

| ID | Scenario | Command / action | Expected result |
|---|---|---|---|
| T1 | Symlink install | `test -L .codex/skills/ask-codewhale && readlink .codex/skills/ask-codewhale` | Symlink exists and points to `../../skills/ask-codewhale` |
| T2 | Skill frontmatter shape | Parse/read `skills/ask-codewhale/SKILL.md` | `name` and `description` present; name is hyphen-safe |
| T3 | Skill description semantics | Inspect frontmatter description | Starts with `Use when`; trigger-only; no workflow summary shortcut |
| T4 | Default advisory flow | Inspect skill command selection rules | Cross review/focused questions route to `codewhale exec` |
| T5 | Delegated task flow | Inspect skill command selection rules | `codewhale exec --auto` is reserved for explicit tool-backed delegation |
| T6 | Diff review flow | Inspect skill command selection rules | `codewhale review` is used when a git diff is the natural target and exists |
| T7 | No review target | Inspect skill no-target branch | Stops with precise message when no git diff/repo and no prompt target exists |
| T8 | Success artifact | Dogfood run succeeds | Artifact saved under `.ask-codewhale/artifacts/` with prompt, output, summary, next steps |
| T9 | Failure artifact | Review/execute controlled nonzero local CLI path if safe | Failure contract preserves command, exit code/stdout/stderr when execution occurs |
| T10 | Missing CLI no-fallback | Run/inspect with `PATH=/usr/bin:/bin` or equivalent hiding `codewhale` | Clear local-CLI-required failure; no alternate provider invoked or suggested as automatic fallback |
| T11 | Namespace guard | Inspect repo after runs | No ask-codewhale product artifacts under `.omx/` |

## Acceptance criteria

- The repo contains a working `ask-codewhale` skill installed via `.codex/skills` symlink
- The skill explicitly uses local `codewhale` commands and mirrors OMX `ask` behavior closely
- The skill frontmatter follows writing-skills discovery rules: trigger-only `description` beginning with `Use when`
- All ask-codewhale evidence lands in `.ask-codewhale/artifacts/`
- A dogfood CodeWhale review has been run and saved
- The repo never writes ask-codewhale product artifacts under `.omx/`
- Missing `codewhale` produces a clear local-CLI-required failure with no automatic fallback provider
- Verification passes for symlink, metadata, artifact path, missing-CLI contract, and dogfood evidence


Return: verdict APPROVE or REQUEST_CHANGES, top issues only, and concrete suggested edits if any.
```

## Raw CodeWhale output

Exit code: `0`

```text
verdict: APPROVE

The `skills/ask-codewhale/SKILL.md` strictly follows the approved design, mirrors OMX `ask` shape, uses a trigger-only `Use when` description, defines the correct artefact namespace, and enforces no fallback on missing `codewhale`. No changes are required to the skill document. The symlink installation is a separate repo‑setup step and does not affect the SKILL.md content.

```

## Concise summary

CodeWhale returned an approve-style review. Raw output captured below.

## Action items / next steps

No action unless the raw output includes concrete low-risk improvements.
