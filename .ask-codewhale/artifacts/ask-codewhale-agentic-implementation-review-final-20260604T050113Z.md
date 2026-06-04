# Ask CodeWhale Artifact: Agentic Implementation Review Final

## Original user task

Final Autopilot implementation dogfood for docs/superpowers/specs/2026-06-04-ask-codewhale-agentic-review-design.md after code-review readability/precedence fix.

## Backend and final prompt sent to CodeWhale

- Backend: local CodeWhale CLI
- Command shape: `DEEPSEEK_FORCE_HTTP1=1 codewhale --sandbox-mode read-only --approval-policy never -C /Users/frick/ws_idea/ask-codewhale exec --auto <safe prompt from .ask-codewhale/tmp>`
- Exit code: `0`
- Prompt style: concise repo-aware prompt; repository/file contents were not pasted

```text
Read-only repo-aware review of the current final ask-codewhale implementation. Inspect this checkout yourself; do not modify files and do not rely on pasted file contents.

Targets: skills/ask-codewhale/SKILL.md, .gitignore, docs/superpowers/specs/2026-06-04-ask-codewhale-agentic-review-design.md

Check: command-selection precedence is clear; repo-aware reviews default to concise prompts plus CodeWhale agentic exploration; fixed-text questions remain plain exec; the skill has no runtime dependency on planning docs; .gitignore only adds .ask-codewhale/tmp/ and not artifacts.

Return: APPROVE or REQUEST_CHANGES, top blocking findings only, and file-path evidence.
```

## Raw or cleaned CodeWhale output

```text
All three files read. Now comparing each against the review criteria.

---

**1. Command-selection precedence is clear** — PASS

SKILL.md lines 21-25 establish a clean three-way precedence:

> *"Apply these precedence rules: use `codewhale review` only for actual diff targets; use plain `codewhale exec` only for fixed-text or no-tool questions; use `codewhale exec --auto` when CodeWhale must inspect the checkout or when the user explicitly delegates a task to CodeWhale."*

Four distinct subsections follow (Repo-aware review, Plain advisor questions, Git diff review, Delegated write tasks), each with unambiguous triggers and constraints.

**2. Repo-aware reviews default to concise prompts + agentic exploration** — PASS

The "Repo-aware review" subsection (lines 29-37) directly encodes:

> *"Send a concise prompt that names the task, target paths, constraints, and expected output."*
> *"Do not paste large file contents, full repository context, broad diffs, or untracked artifact bodies when CodeWhale can read the worktree itself."*

Confirmed. The policy is explicit: concise prompts, let CodeWhale inspect the checkout.

**3. Fixed-text questions remain plain exec** — PASS

The "Plain advisor questions" subsection (lines 40-44):

> *"Use plain `codewhale exec` for fixed-text, conceptual, or no-tool advisor questions where repository inspection is not needed."*

No drift. Fixed-text/notool stays on plain `exec`.

**4. The skill has no runtime dependency on planning docs** — PASS

Grep of `SKILL.md` for `external_review_rules`, `agentic-review-design`, `docs/superpowers`, and `planning` returns zero hits. The skill is self-contained. The design doc (`2026-06-04-ask-codewhale-agentic-review-design.md`) confirms this boundary explicitly — *"The final ask-codewhale skill must be self-contained and must not mention, depend on, or require that file"* (line 20).

**5. `.gitignore` only adds `.ask-codewhale/tmp/` and not artifacts** — PASS

`.gitignore` contents:

```text
.omx/
.ask-codewhale/tmp/
```

- `.ask-codewhale/tmp/` is present.
- `.ask-codewhale/artifacts/` is absent — matching the design doc's explicit exclusion: *"`.ask-codewhale/artifacts/` should not be newly ignored because existing design allows deliberate dogfood artifacts to be committed after review."*
- `.omx/` is pre-existing OMX runtime state, not an ask-codewhale artifact.

---

**Verdict: APPROVE**

No blocking findings. The implementation matches the design doc across all five criteria. Evidence:

| Criterion | File | Evidence |
|---|---|---|
| Clear command-selection precedence | `skills/ask-codewhale/SKILL.md` | Lines 21-25, four subsections |
| Repo-aware → concise prompts + agentic | `skills/ask-codewhale/SKILL.md` | Lines 29-37 |
| Fixed-text → plain exec preserved | `skills/ask-codewhale/SKILL.md` | Lines 40-44 |
| No runtime dependency on planning docs | `skills/ask-codewhale/SKILL.md` | Zero references to `docs/` |
| .gitignore only ignores tmp/, not artifacts | `.gitignore` | 3 lines, artifacts absent |

--- stderr ---
tool: read_file (path: /Users/frick/ws_idea/ask-codewhale/skills/ask-codewhale/SKILL.md)
tool: read_file (path: /Users/frick/ws_idea/ask-codewhale/.gitignore)
tool: read_file (path: <107 chars>)
tool read_file completed: ---
name: ask-codewhale
description: "Use when asking the local CodeWhale coding agent for cross review, second opinions, plan/code critique, or a simple delegated coding-agent task"
---

# Ask CodeWhale

Use the locally installed CodeWhale CLI as an external coding-agent advisor for
focused ques...
tool read_file completed: # OMX runtime/workflow state is local and not an ask-codewhale product artifact.
.omx/
.ask-codewhale/tmp/

tool read_file completed: # ask-codewhale Agentic Review Design

Date: 2026-06-04

## Goal

Revise the repo-local `ask-codewhale` skill so CodeWhale is used as an external coding agent for repo-aware reviews instead of a one-shot model that receives large pasted context. The skill should prefer concise prompts that identi...
```

## Concise summary

All three files read. Now comparing each against the review criteria.

---

**1. Command-selection precedence is clear** — PASS

SKILL.md lines 21-25 establish a clean three-way precedence:

> *"Apply these precedence rules: use `codewhale review` only for actual diff targets; use plain `codewhale exec` only for fixed-text or no-tool questions; use `codewhale exec --auto` when CodeWhale must inspect the checkout or when the user explicitly delegates a task to CodeWhale."*

Four distinct subsections follow (Repo-aware review, Plain advisor questions, Git diff review, Delegated write tasks), each with unambiguous triggers and constraints.

**2. Repo-aware reviews default to concise prompts + agentic exploration** — PASS

The "Repo-aware review" subsection (lines 29-37) directly encodes:

> *"Send a concise prompt that names the task, target paths, constraints, and expected output."*
> *"Do not paste large file contents, full repository context, broad diffs, or untracked artifact bodies when CodeWhale can read the worktree itself."*

Confirmed. The policy is explicit: concise prompts, let CodeWhale inspect the checkout.

**3. Fixed-text questions remain plain exec** — PASS

The "Plain advisor questions" subsection (lines 40-44):

> *"Use plain `codewhale exec` for fixed-text, conceptual, or no-tool advisor questions where repository inspection is not needed."*

No drift. Fixed-tex...

## Action items / next steps

1. Treat CodeWhale output as advisory evidence for Autopilot review.
2. Fix any blocking findings before final review/QA.
