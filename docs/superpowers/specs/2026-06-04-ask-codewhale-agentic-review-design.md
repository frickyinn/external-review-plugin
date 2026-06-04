# ask-codewhale Agentic Review Design

Date: 2026-06-04

## Goal

Revise the repo-local `ask-codewhale` skill so CodeWhale is used as an external coding agent for repo-aware reviews instead of a one-shot model that receives large pasted context. The skill should prefer concise prompts that identify the task, target paths, and constraints, then let CodeWhale inspect the checkout itself when repository context is available.

## Source-of-truth boundaries

- Canonical skill file: `skills/ask-codewhale/SKILL.md`.
- Product artifact namespace: `.ask-codewhale/`.
- Temporary execution namespace: `.ask-codewhale/tmp/`.
- Existing design history: `docs/superpowers/specs/2026-06-02-ask-codewhale-design.md`.
- `docs/external_review_rules.md` is planning context only for this revision. The final `ask-codewhale` skill must be self-contained and must not mention, depend on, or require that file.

## Problem statement

The current skill routes cross review, plan review, and code review prompts to plain `codewhale exec`. Current CodeWhale CLI help says plain `exec` is a one-shot model response and `exec --auto` enables non-interactive filesystem and shell tool use. Because repo-aware review is currently described as a plain prompt path, Codex is likely to paste large chunks of repository context into the prompt. That is inefficient, increases privacy exposure, and underuses CodeWhale's agentic repository exploration capability.

Review evidence also identified adjacent risks:

- Direct shell examples such as `codewhale exec "{{ARGUMENTS}}"` encourage unsafe prompt interpolation.
- Artifact capture stores raw prompts and outputs that may contain sensitive data.
- `codewhale review` does not define the source of the git diff it reviews.
- Tool-backed `--auto` use needs clearer distinction between read-only review and delegated write tasks.
- Raw CodeWhale output can contain TUI or ANSI control sequences unless structured output or cleanup is used.

## Selected approach

Use a minimal contract revision. Update the skill text and ignore only temporary files. Do not add a wrapper script or expand the repo into a full review workflow.

Rejected alternatives:

1. Add a helper wrapper script. This would make behavior more enforceable, but it reintroduces quoting and maintenance surface that the original design avoided.
2. Build a full review workflow with scope selection, retry logic, artifact indexing, and structured parsing. This is useful later, but it is too broad for the current correction.
3. Keep repo-aware review on plain `exec` and rely on the caller to paste enough context. This preserves the current inefficiency and prevents CodeWhale from acting as an independent reviewer.

## Command selection design

The revised skill should distinguish four paths.

### Repo-aware review

Use this for repository, implementation, plan, code, or skill reviews where CodeWhale should inspect the checkout.

- Prefer `codewhale exec --auto` with read-only intent and constraints.
- Prompt content should be concise: describe the task, target path(s), expected output, and safety constraints.
- Do not paste large file contents, full repo context, or broad diffs when CodeWhale can read the worktree itself.
- Ask CodeWhale not to modify files for review tasks.

Example shape, not a required literal command:

```bash
codewhale --sandbox-mode read-only --approval-policy never -C <repo> exec --auto <safe-prompt>
```

### Plain advisor review

Use plain `codewhale exec` only when the request is fixed-text, conceptual, or no-tool by nature.

Examples:

- Critique a short paragraph pasted by the user.
- Compare two concise design options without requiring repository inspection.
- Answer a focused advisor question where no checkout exploration is needed.

### Git diff review

Use `codewhale review` when the natural target is a git diff.

Rules:

- Default diff source is the current working tree diff.
- If the user specifies staged changes, a commit range, or another diff scope, use that explicit scope.
- If no usable diff exists, fall back to repo-aware `exec --auto` review when there is still a meaningful target path or prompt; otherwise report the missing review target.

### Delegated write task

Use `codewhale exec --auto` for write-capable delegated tasks only when the user explicitly asks CodeWhale to perform the task, not merely to review it.

The skill should warn that this can have filesystem or shell side effects. For destructive, external-production, credentialed, or broad changes, Codex must not treat this as a silent default.

## Prompt passing and shell safety

The revised skill should avoid examples that interpolate `{{ARGUMENTS}}` directly into a quoted shell command. It should instruct Codex to use safe prompt passing, such as:

- argv-safe command construction,
- a temporary prompt file,
- a here-doc with careful shell quoting,
- or another safe non-interpolating mechanism.

The skill should still record the backend and final prompt in the artifact, but it should not present unsafe shell snippets as copy-pasteable examples.

## Artifact and privacy design

Artifacts remain under `.ask-codewhale/artifacts/` and should include:

1. Original user task.
2. Backend and final prompt sent to CodeWhale.
3. Command shape, exit status, stdout, and stderr when available.
4. Raw or cleaned CodeWhale output.
5. Concise summary.
6. Action items or next steps.

Privacy requirements:

- Artifacts may contain prompts, private paths, source excerpts, model output, and secrets.
- Do not commit artifacts without reviewing them for sensitive content.
- Nonzero CodeWhale exits still require an artifact if execution began.
- Prefer structured or plain output (`--json`, `--output-format stream-json`, or cleaned text) when practical, so artifacts are readable and not polluted by TUI control sequences.

`.ask-codewhale/tmp/` is temporary scratch space and should be ignored by git. `.ask-codewhale/artifacts/` should not be newly ignored because existing design allows deliberate dogfood artifacts to be committed after review.

## File changes planned for implementation

1. `skills/ask-codewhale/SKILL.md`
   - Update command selection for repo-aware review, plain advisor review, git diff review, and delegated write tasks.
   - Add concise repo-aware prompting policy.
   - Add shell-safe prompt passing guidance.
   - Add artifact privacy and output cleanup guidance.
   - Keep the skill self-contained; do not reference `docs/external_review_rules.md`.

2. `.gitignore`
   - Add `.ask-codewhale/tmp/` only.
   - Do not add `.ask-codewhale/artifacts/`.

No changes are planned to `docs/external_review_rules.md`, existing artifacts, global skill installation, or the symlink at `.codex/skills/ask-codewhale`.

## Verification plan

1. Static skill checks:
   - Frontmatter still contains `name: ask-codewhale`.
   - Description still starts with `Use when` and remains trigger-only.
   - `SKILL.md` distinguishes plain `exec`, repo-aware `exec --auto`, `review`, and write-capable `exec --auto` delegation.
   - `SKILL.md` requires concise repo-aware prompts rather than pasted large context.
   - `SKILL.md` does not mention `docs/external_review_rules.md`.

2. File-boundary checks:
   - `.gitignore` contains `.ask-codewhale/tmp/`.
   - `.gitignore` does not newly ignore `.ask-codewhale/artifacts/`.
   - `docs/external_review_rules.md` remains unmodified by the implementation.

3. Dogfood check:
   - Run one short-prompt repo-aware CodeWhale review using `exec --auto` in a read-only shape.
   - Confirm CodeWhale can inspect repository files itself.
   - Save a reviewed artifact under `.ask-codewhale/artifacts/`.

4. Final status check:
   - Confirm changed files match the approved scope.
   - Report any artifact privacy caveat before committing or sharing artifacts.

## Scope exclusions

- No wrapper script.
- No full workflow engine.
- No global `~/.codex/skills` changes.
- No dependency changes.
- No deletion of existing committed dogfood artifacts.
- No implementation dependency on `docs/external_review_rules.md`.

## Success criteria

The revision is successful when `ask-codewhale` guides Codex toward short, repo-aware prompts for CodeWhale reviews, reserves large pasted context for fixed-text/no-tool cases, documents safe prompt passing and artifact privacy, and preserves the lightweight repo-local skill architecture.
