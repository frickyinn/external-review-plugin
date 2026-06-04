---
name: ask-codewhale
description: "Use when asking the local CodeWhale coding agent for cross review, second opinions, plan/code critique, or a simple delegated coding-agent task"
---

# Ask CodeWhale

Use the locally installed CodeWhale CLI as an external coding-agent advisor for
focused questions, cross review, plan/code critique, repo-aware review, or simple
delegated tasks. This skill follows the local-advisor shape of OMX `ask` while
keeping ask-codewhale artifacts in this repo's own namespace.

## Usage

```bash
$ask-codewhale <question or task>
codewhale exec <safe fixed-text prompt>
codewhale --sandbox-mode read-only --approval-policy never -C <repo> \
  exec --auto <safe repo-aware prompt>
codewhale review <diff review target>
```

The command examples above show command shape only. Pass user-supplied prompts
safely; do not build shell commands by directly interpolating template variables
into quoted strings.

## Command selection

Apply these precedence rules: use `codewhale review` only for actual diff
targets; use plain `codewhale exec` only for fixed-text or no-tool questions;
use `codewhale exec --auto` when CodeWhale must inspect the checkout or when the
user explicitly delegates a task to CodeWhale.

### Repo-aware review

Use `codewhale exec --auto` for repository, implementation, skill, plan, or code
reviews where CodeWhale should inspect the checkout itself.

- Prefer a read-only shape such as `codewhale --sandbox-mode read-only
  --approval-policy never -C <repo> exec --auto <safe repo-aware prompt>`.
- Send a concise prompt that names the task, target paths, constraints, and
  expected output.
- Do not paste large file contents, full repository context, broad diffs, or
  untracked artifact bodies when CodeWhale can read the worktree itself.
- Tell CodeWhale not to modify files for review tasks.

### Plain advisor questions

Use plain `codewhale exec` for fixed-text, conceptual, or no-tool advisor
questions where repository inspection is not needed.

Examples include critiquing a short pasted paragraph, comparing concise design
options, or asking a focused question whose answer does not depend on reading the
checkout.

### Git diff review

Use `codewhale review` when a git diff is the natural review target.

- Default diff source is the current working tree diff.
- If the user specifies staged changes, a commit range, or another diff scope,
  use that explicit scope.
- If no usable diff exists but there is still a target path or prompt to review,
  fall back to repo-aware `codewhale exec --auto` and explain the fallback.
- If neither a diff nor a meaningful prompt target exists, stop with a precise
  missing-target message.

### Delegated write tasks

Use `codewhale exec --auto` for write-capable delegated tasks only when the user
explicitly asks CodeWhale to perform the task, not merely review it.

Warn that this mode can have filesystem or shell side effects. Do not use it
silently for destructive, external-production, credentialed, broad, or
preference-dependent changes.

## Prompt passing and shell safety

Prefer one of these safe prompt-passing patterns:

- pass arguments through an argv-safe command construction,
- write the prompt to a temporary file and pass the file contents safely,
- use a carefully quoted here-doc,
- or use another non-interpolating mechanism provided by the execution
  environment.

Avoid command examples that directly splice user text into shell strings. Treat
prompts as data, not shell syntax.

## Local CLI requirement

Prefer the local binary. If `codewhale` is missing, explain that the local
CodeWhale CLI is required. Do not silently switch to an MCP server, remote
provider, Claude, Gemini, Codex, or another coding agent.

## Artifact requirement

After local execution, save a markdown artifact to:

```text
.ask-codewhale/artifacts/ask-codewhale-<slug>-<timestamp>.md
```

Minimum sections:

1. Original user task
2. Backend and final prompt sent to CodeWhale
3. Command shape, exit code, stdout, and stderr when available
4. Raw or cleaned CodeWhale output
5. Concise summary
6. Action items / next steps

If CodeWhale exits nonzero after execution begins, still save an artifact with
the command, exit code, stdout/stderr, concise summary, and next steps. Treat
CodeWhale output as advisory evidence; Codex remains responsible for synthesis
and follow-up decisions.

Artifacts may contain prompts, private paths, source excerpts, model output, or
secrets. Review artifacts before committing or sharing them. Prefer structured or
plain output such as `--json`, `--output-format stream-json`, or cleaned text
when practical so artifacts are readable and not polluted by TUI control
sequences.

Use `.ask-codewhale/tmp/` only for temporary prompt/stdout/stderr scratch files.
Temporary files should not be committed.

Task: {{ARGUMENTS}}
