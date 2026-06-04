# ask-claude Model and Effort Parameters Design

## Goal

Add Claude CLI-like model and effort selection to the `external-review:ask-claude` provider only. The provider should default to Claude Opus with high effort while allowing callers to override those values explicitly at the start of an `ask-claude` invocation.

This is a provider-local feature. The `external-review:ask` router must not parse, document, or pass through these options, and `external-review:ask-codewhale` must remain unchanged.

## Current context

The repository currently packages the `external-review` plugin under `plugins/external-review/`. The Claude provider contract lives in:

```text
plugins/external-review/skills/ask-claude/SKILL.md
```

The provider already uses short repo-aware prompts, local Claude CLI execution, no session persistence, read-only inspection tools, and `.external-review/` artifacts. The current command examples omit explicit model and effort selection.

Local `claude --help` confirms the relevant CLI flags:

- `--model <model>` accepts aliases such as `opus` or `sonnet`, or full model names.
- `--effort <level>` accepts `low`, `medium`, `high`, `xhigh`, or `max`.

## User interface

The official Claude provider usage becomes:

```bash
$external-review:ask-claude [--model <model>] [--effort <effort>] <question or review task>
```

Defaults:

```text
model = opus
effort = high
```

Examples:

```bash
$external-review:ask-claude Review this implementation for missed edge cases.
$external-review:ask-claude --model sonnet --effort medium Review README.md for install clarity.
$external-review:ask-claude --model claude-opus-4-8 --effort xhigh Review the current diff for API boundary risks.
```

## Parsing rules

The provider parses only a short option prefix at the beginning of the task string.

Supported options:

- `--model <model>`
- `--effort <effort>`

Rules:

1. Parse options only while the next token is `--model` or `--effort`.
2. Stop parsing at the first token that does not start with `--`; the remaining text is the review task.
3. If the first unparsed token starts with `--`, reject it as an unknown leading option instead of treating it as task text.
4. Require a value after each supported option.
5. Restrict `--effort` to `low`, `medium`, `high`, `xhigh`, or `max`.
6. Allow `--model` values accepted by the installed Claude CLI, including aliases and full model names.
7. Do not treat later occurrences of `--model` or `--effort` inside the review task as configuration after task parsing has started.

This keeps normal review prompts safe. For example, this should be interpreted as task text, not as a configuration override:

```bash
$external-review:ask-claude Review whether the docs mention --model and --effort correctly.
```

## Command behavior

Both Claude execution modes should include the resolved values.

Repo-aware review command shape:

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

Fixed-text advisor command shape:

```bash
claude -p \
  --model <resolved-model> \
  --effort <resolved-effort> \
  --no-session-persistence \
  --disable-slash-commands \
  < .external-review/tmp/claude-<slug>-<timestamp>.prompt.md
```

The provider should continue to pass prompt content through a prompt file and stdin. User text must not be interpolated into a shell command string.

## Error handling

Before invoking Claude, the provider should report a clear error when:

- `claude` is not installed or not on `PATH`.
- A leading supported option is missing its value.
- A leading option is unknown.
- `--effort` is not one of `low`, `medium`, `high`, `xhigh`, or `max`.
- No review task remains after option parsing.

Missing Claude remains provider-local: do not fall back to CodeWhale or another reviewer.

## Artifacts

Artifact location and privacy policy stay unchanged:

```text
.external-review/artifacts/external-review-claude-<slug>-<timestamp>.md
```

The artifact should record:

- the original user task,
- the parsed/resolved model and effort,
- the final short prompt,
- the command shape and safety mode,
- exit code, stdout, stderr, and debug path when available,
- Claude output,
- Codex synthesis and action items.

Temporary prompt/stdout/stderr/debug files remain under `.external-review/tmp/`.

## Router boundary

Do not change `plugins/external-review/skills/ask/SKILL.md` except if a validation comment is ever needed. The router should keep routing by provider name only. It must not advertise or parse `--model` or `--effort`.

This means the following is intentionally unsupported:

```bash
$external-review:ask --model opus Ask Claude to review this plan.
```

Users who want model or effort control must invoke `external-review:ask-claude` directly.

## Files to update during implementation

1. `plugins/external-review/skills/ask-claude/SKILL.md`
   - Document the new usage, defaults, parsing rules, and errors.
   - Add `--model <resolved-model>` and `--effort <resolved-effort>` to both command shapes.
   - State the default as `--model opus --effort high`.

2. `README.md`
   - Add a concise Claude example showing optional `--model` and `--effort`.
   - Keep all examples namespaced as `$external-review:ask-claude`.

3. `plugins/external-review/scripts/validate_external_review_contract.py`
   - Add contract checks that `ask-claude` documents `--model opus`, `--effort high`, and the allowed effort set.
   - Add a guard that the router skill does not document or advertise `--model` or `--effort`.

No implementation is planned for `ask-codewhale`, the router, plugin manifest, marketplace entry, or shared artifact rules.

## Testing and verification

Implementation should be verified with:

```bash
python3 plugins/external-review/scripts/validate_external_review_contract.py
python3 -m json.tool plugins/external-review/.codex-plugin/plugin.json >/dev/null
claude --help | grep -E -- '--model|--effort'
git diff --check
```

A lightweight dogfood review may be added if the local Claude CLI is available and authenticated, but it should not be the only proof of correctness. The contract validator should prove the documented provider boundary even when no live Claude call is run.

## Success criteria

The change is successful when:

- `external-review:ask-claude` clearly supports optional leading `--model` and `--effort` parameters.
- The default behavior is explicitly `opus` with `high` effort.
- The Claude command shapes always include the resolved model and effort.
- Invalid effort values and malformed leading options fail before provider execution.
- The router and CodeWhale provider remain unaffected.
- Existing read-only, short-prompt, artifact, and no-fallback boundaries are preserved.
