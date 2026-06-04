---
name: ask-claude
description: Ask local Claude for read-only external review, critique, or a second opinion using short repo-aware prompts and Claude-specific execution rules.
---

# Ask Claude

Use the locally installed Claude CLI as a read-only external reviewer for focused questions, plan/code critique, skill review, implementation review, and second opinions.

Official usage:

```bash
$external-review:ask-claude <question or review task>
```

Before execution, read and apply `../../shared/external-review-principles.md`.

## Repo-aware review

Use Claude CLI with a short prompt and read-only inspection tools when Claude should inspect the checkout itself.

Prefer a safe prompt-file/stdin pattern such as:

```bash
timeout 600s claude -p \
  --no-session-persistence \
  --permission-mode default \
  --allowedTools Read Grep Glob LS \
    "Bash(git status:*)" \
    "Bash(git diff:*)" \
    "Bash(git ls-files:*)" \
    "Bash(rg:*)" \
    "Bash(sed:*)" \
    "Bash(cat:*)" \
    "Bash(nl:*)" \
    "Bash(wc:*)" \
  --debug-file .external-review/tmp/claude-<slug>-<timestamp>.debug.log \
  < .external-review/tmp/claude-<slug>-<timestamp>.prompt.md
```

The command above shows command shape only. Adjust flags to the installed Claude CLI version when necessary, while preserving the read-only review contract. If a local environment needs a wrapper such as a proxy command, use it without changing the prompt or artifact policy.

## Prompt content

- Send a concise prompt with the task, target paths, constraints, and expected output.
- Do not paste broad repository context, full diffs, large file bodies, or untracked artifact contents when Claude can read the worktree itself.
- Tell Claude not to modify files.
- Use no session persistence for review calls when the CLI supports it.
- Restrict tools to read-only file/search/listing and safe git inspection commands when the CLI supports tool restrictions.

## Fixed-text advisor questions

For bounded fixed-text questions where repository inspection is not needed, use Claude CLI with no session persistence and no repository context. If the installed Claude CLI supports fully disabling tools, use that supported flag; otherwise do not claim a no-tool guarantee. A safe fixed-text command shape is:

```bash
claude -p --no-session-persistence --disable-slash-commands \
  < .external-review/tmp/claude-<slug>-<timestamp>.prompt.md
```

## Read-only boundary

This plugin excludes delegated write modes. Do not ask Claude to edit files, run destructive actions, or perform credentialed/external-production work. If the user wants Claude to perform writes, explain that this plugin is read-only and ask for a separate explicit workflow outside `external-review`.

## Local CLI requirement

Prefer the local `claude` binary. If it is missing, report that Claude is required for `external-review:ask-claude`. Do not switch to CodeWhale or another provider.

## Artifact requirement

After Claude execution begins, save an artifact under:

```text
.external-review/artifacts/external-review-claude-<slug>-<timestamp>.md
```

Capture exit code, stdout, stderr, and debug-file path when available. Follow the slug, timestamp, minimum-section, privacy, and temporary-file rules in `../../shared/external-review-principles.md`.

Task: {{ARGUMENTS}}
