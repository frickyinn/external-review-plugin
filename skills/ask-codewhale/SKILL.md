---
name: ask-codewhale
description: Ask local CodeWhale for read-only external review, critique, or a second opinion using short repo-aware prompts and CodeWhale-specific execution rules.
---

# Ask CodeWhale

Use the locally installed CodeWhale CLI as a read-only external reviewer for focused questions, plan/code critique, skill review, implementation review, and second opinions.

Official usage:

```bash
$external-review:ask-codewhale <question or review task>
```

Before execution, read and apply `../../shared/external-review-principles.md`.

## Command selection

Apply these precedence rules:

1. Use `codewhale review` only when an actual git diff target is the natural review target.
2. Use plain `codewhale exec` only for fixed-text or no-tool advisor questions where repository inspection is not needed.
3. Use `codewhale exec --auto` when CodeWhale should inspect the checkout itself.

For repository, implementation, skill, plan, or code reviews, prefer a repo-aware read-only shape:

```bash
codewhale --sandbox-mode read-only --approval-policy never -C <repo> \
  exec --auto <safe repo-aware prompt>
```

The command above shows command shape only. Pass prompt text safely; do not splice user text into a shell string.

## Repo-aware review

Use `codewhale exec --auto` for review tasks where CodeWhale should inspect the checkout.

- Send a concise prompt with the task, target paths, constraints, and expected output.
- Do not paste broad repository context, full diffs, large file bodies, or untracked artifact contents when CodeWhale can read the worktree itself.
- Tell CodeWhale not to modify files.
- Keep filesystem posture read-only and approval policy noninteractive when available.

## Git diff review

Use `codewhale review` when a git diff is the natural review target.

- Default diff source is the current working tree diff.
- If the user specifies staged changes, a commit range, or another diff scope, use that explicit scope.
- If no usable diff exists but there is still a target path or prompt to review, use repo-aware `codewhale exec --auto` and explain the fallback.
- If neither a diff nor a meaningful prompt target exists, stop with a precise missing-target message.

## Fixed-text advisor questions

Use plain `codewhale exec` for bounded fixed-text or no-tool questions where repository inspection is not needed.

## Read-only boundary

This plugin excludes delegated write modes. Do not ask CodeWhale to edit files, run destructive actions, or perform credentialed/external-production work. If the user wants CodeWhale to perform writes, explain that this plugin is read-only and ask for a separate explicit workflow outside `external-review`.

## Local CLI requirement

Prefer the local `codewhale` binary. If it is missing, report that CodeWhale is required for `external-review:ask-codewhale`. Do not switch to Claude or another provider.

## Artifact requirement

After CodeWhale execution begins, save an artifact under:

```text
.external-review/artifacts/external-review-codewhale-<slug>-<timestamp>.md
```

Follow the slug, timestamp, minimum-section, privacy, and temporary-file rules in `../../shared/external-review-principles.md`.

Task: {{ARGUMENTS}}
