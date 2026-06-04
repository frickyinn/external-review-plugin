---
name: ask-claude
description: Ask local Claude for read-only external review, critique, or a second opinion using short repo-aware prompts and Claude-specific execution rules.
---

# Ask Claude

Use the locally installed Claude CLI as a read-only external reviewer for focused questions, plan/code critique, skill review, implementation review, and second opinions.

Official usage:

```bash
$external-review:ask-claude [--model <model>] [--effort <effort>] <question or review task>
```

Before execution, read and apply `../../shared/external-review-principles.md`.

## Model and effort options

Default to Claude Opus with high effort:

```bash
--model opus --effort high
```

Parse only these leading options before the review task:

- `--model <model>`: pass the model value to Claude CLI. Accept aliases or full model names supported by the installed `claude` binary.
- `--effort <effort>`: pass the effort value to Claude CLI. Allowed values are `low`, `medium`, `high`, `xhigh`, and `max`.

Parsing rules:

1. Parse options only while the next token is `--model` or `--effort`.
2. Stop parsing at the first token that does not start with `--`; the remaining text is the review task.
3. If the first unparsed token starts with `--`, reject it as an unknown leading option instead of treating it as task text.
4. Require a value after each supported option.
5. Do not treat later mentions of `--model` or `--effort` inside the review task as configuration after task parsing has started.

If no options are provided, use `--model opus --effort high`. If the parsed effort is not one of `low`, `medium`, `high`, `xhigh`, or `max`, stop before invoking Claude and report the invalid value. If no review task remains after option parsing, stop and ask for a review task.

## Repo-aware review

Use Claude CLI with a short prompt and read-only inspection tools when Claude should inspect the checkout itself.

Prefer a safe prompt-file/stdin pattern such as:

```bash
timeout 600s claude -p \
  --model <resolved-model> \
  --effort <resolved-effort> \
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
claude -p \
  --model <resolved-model> \
  --effort <resolved-effort> \
  --no-session-persistence \
  --disable-slash-commands \
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

Record the resolved model and effort in the artifact alongside the original user task, final short prompt, command shape, provider output, Codex synthesis, and action items.

Task: {{ARGUMENTS}}
