# External Review Shared Principles

Apply these principles to every `external-review` skill.

## Scope

- Use this plugin only for read-only external review, critique, and second opinions.
- Do not ask external agents to edit files, run destructive changes, perform credentialed actions, or operate external production systems.
- Do not include delegated write-task modes in provider skills.
- Treat external-agent output as advisory evidence. Codex remains responsible for synthesis, verification, and final decisions.

## Short prompt contract

Send short, repo-aware prompts. Include only:

1. the task or review question,
2. relevant target paths or diff scope,
3. constraints and non-goals,
4. expected output format.

Do not paste full repository context, broad diffs, large file bodies, or untracked artifact contents when the selected external agent can inspect the checkout itself.

## Agentic repository exploration

When repository context is needed, let the selected external agent inspect the checkout with its own read-only tools or allowed read-only shell commands. Review prompts should say that the external agent must not modify files.

## Prompt and shell safety

Treat user prompts as data, not shell syntax. Prefer safe prompt-passing patterns:

- pass prompt text through argv-safe command construction,
- write prompt text to `.external-review/tmp/` and pass it by stdin or another non-interpolating mechanism,
- use a carefully quoted here-doc when a temporary file is not practical.

Do not build shell commands by directly interpolating user text into quoted strings.

## Provider isolation

Do not silently fallback across providers. If CodeWhale is unavailable, report a CodeWhale requirement for the CodeWhale skill. If Claude is unavailable, report a Claude requirement for the Claude skill.

## Artifacts

After provider execution begins, save a markdown artifact under:

```text
.external-review/artifacts/external-review-<provider>-<slug>-<timestamp>.md
```

Slug format: lowercase ASCII kebab-case derived from the task, with non-alphanumeric runs collapsed to `-`, trimmed to 64 characters, and defaulting to `review` when empty.

Timestamp format: UTC `YYYYMMDDTHHMMSSZ`.

Minimum artifact sections:

1. Original user task
2. Provider and final short prompt
3. Command shape and safety mode
4. Exit code, stdout, stderr, and debug path when available
5. Raw or cleaned provider output
6. Codex synthesis
7. Action items / next steps

Artifacts may contain prompts, private paths, source excerpts, model output, or secrets. Review artifacts before committing or sharing them. Dogfood artifacts are generated and retained locally for verification, but are not automatically staged or committed; commit one only when it has been reviewed for sensitive content and intentionally selected as durable evidence.

Use `.external-review/tmp/` only for temporary prompt/stdout/stderr/debug scratch files. Temporary files must not be committed.
