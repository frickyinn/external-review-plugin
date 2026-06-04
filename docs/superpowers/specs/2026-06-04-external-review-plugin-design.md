# External Review Plugin Design

Date: 2026-06-04
Status: Approved for spec review; implementation not started

## Goal

Upgrade the current ask-codewhale skill into a namespaced plugin for read-only external agent review and advisor workflows. The plugin should keep the current ask-codewhale short-prompt, agentic-review behavior as the baseline, add Claude support, and provide a thin router that dispatches only within the plugin.

## Non-goals

- Do not build a broad cross-agent orchestration or execution runtime.
- Do not make external agents silently modify files.
- Do not paste whole repository context, broad diffs, or large file bodies into external-agent prompts when the agent can inspect the checkout itself.
- Do not depend on `docs/external_review_rules.md` as a runtime or skill source of truth; it is only planning reference material.
- Do not route through or depend on any global `ask` skill outside this plugin.
- Do not migrate or delete existing `.ask-codewhale/` historical artifacts.

## Plugin name and positioning

The plugin name is `external-review`.

The name intentionally narrows the scope to read-only external review, critique, and second opinions. It avoids the broader implication of `cross-agent`, which could suggest multi-agent execution, handoff, or orchestration.

## Official invocation surface

The official skill entrypoints are namespaced:

```text
$external-review:ask <prompt>
$external-review:ask-codewhale <task>
$external-review:ask-claude <task>
```

The plugin should not advertise bare `$ask`, `$ask-codewhale`, or `$ask-claude` as the official surface. Namespacing makes it explicit that routing and provider execution stay inside this plugin.

## Components

### Shared principles

Create this shared principles file:

```text
skills/shared/external-review-principles.md
```

All provider and router skills reference this file. It owns the common contract:

- Review/advisor mode is read-only by default.
- Prompts are short and targeted: task, target paths, constraints, and requested output.
- External agents should inspect the repository themselves when repo context is needed.
- Prompts are data, not shell syntax; do not build shell commands by interpolating user text into quoted strings.
- External-agent output is advisory evidence; Codex remains responsible for synthesis, verification, and final decisions.
- Provider failures do not trigger hidden fallback to another provider.
- Artifacts use the plugin namespace `.external-review/`.

### Router skill: `external-review:ask`

Implementation skill directory:

```text
skills/ask/
```

The router is intentionally thin. It only:

1. Reads the user prompt.
2. Detects a high-confidence provider mention.
3. Routes to a provider skill inside this plugin.
4. Stops with a precise message when provider intent is missing or ambiguous.

High-confidence examples:

- Mentions of `claude` or `ask-claude` route to `external-review:ask-claude`.
- Mentions of `codewhale` or `ask-codewhale` route to `external-review:ask-codewhale`.

Ambiguous cases:

- No provider is named.
- Multiple providers are named.
- The wording asks for a default, best, or automatic reviewer without naming one.

In ambiguous cases, the router asks the user to specify the provider. It does not guess based on task type and does not call provider CLIs directly.

### CodeWhale provider: `external-review:ask-codewhale`

Implementation skill directory:

```text
skills/ask-codewhale/
```

This provider keeps the current ask-codewhale behavior as the baseline.

Responsibilities:

- Use CodeWhale for read-only external review, critique, and second opinions.
- Prefer repo-aware, agentic review with a short prompt when CodeWhale should inspect the checkout.
- Use the CodeWhale CLI command shape appropriate to the task:
  - `codewhale exec --auto` for repo-aware review where CodeWhale should inspect the checkout itself.
  - `codewhale review` only when an actual git diff target is the natural review target.
  - Plain `codewhale exec` only for fixed-text, no-tool advisor questions.
- For review tasks, instruct CodeWhale not to modify files.
- Use read-only sandbox and never-approval style constraints when available.
- Save an artifact even when execution exits nonzero after starting.

### Claude provider: `external-review:ask-claude`

Implementation skill directory:

```text
skills/ask-claude/
```

This provider adds Claude as a read-only external reviewer while following the same shared principles.

Responsibilities:

- Use Claude CLI for read-only external review, critique, and second opinions.
- Prefer repo-aware review with a short prompt and allowed read-only tools when Claude should inspect the checkout.
- Use no session persistence for review calls.
- Restrict tools to read-only repository inspection commands where supported, such as file reads, grep/search, listing, and safe git inspection.
- Capture stdout, stderr, exit status, timeout/debug information when available.
- Save an artifact even when execution exits nonzero after starting.

The Claude provider may consult the existing local `omx ask` skill as implementation reference for how Claude can be invoked, but its contract, artifacts, prompt style, and safety rules must follow this plugin's shared principles and the current ask-codewhale shape.

## Artifact and temporary file policy

Use a new repo-local namespace:

```text
.external-review/
  artifacts/
  tmp/
```

Artifact filenames should use this shape:

```text
.external-review/artifacts/external-review-<provider>-<slug>-<timestamp>.md
```

Minimum artifact sections:

1. Original user task
2. Provider and final short prompt
3. Command shape and safety mode
4. Exit code, stdout, stderr, and debug path when available
5. Raw or cleaned provider output
6. Codex synthesis
7. Action items / next steps

Temporary prompt, stdout, stderr, and debug scratch files belong under `.external-review/tmp/` and should not be committed.

Artifacts may contain prompts, private paths, source excerpts, model output, or secrets. They are not automatically safe to commit or share. Existing `.ask-codewhale/` artifacts remain historical evidence and are not migrated by this feature.

## Data flow

### Direct provider call

1. User invokes `$external-review:ask-codewhale <task>` or `$external-review:ask-claude <task>`.
2. The provider skill loads shared principles.
3. The provider constructs a short prompt from the task, target paths, constraints, and requested output.
4. The provider invokes its local CLI using a safe prompt-passing pattern.
5. The external agent inspects the checkout itself when repo context is needed.
6. The provider saves an artifact.
7. Codex synthesizes the advice and decides any follow-up.

### Router call

1. User invokes `$external-review:ask <prompt>`.
2. The router checks for high-confidence provider intent.
3. If exactly one provider is identified, the router delegates to the matching provider skill.
4. If provider intent is missing or ambiguous, the router stops and asks for an explicit provider.

## Error handling

- Missing CodeWhale CLI: report that CodeWhale is required for `external-review:ask-codewhale`; do not fallback to Claude.
- Missing Claude CLI: report that Claude is required for `external-review:ask-claude`; do not fallback to CodeWhale.
- Ambiguous router prompt: stop and ask the user to specify exactly one provider.
- No meaningful review target: ask for a task, path, or diff scope.
- External-agent nonzero exit: save an artifact with command shape, exit code, stdout/stderr, summary, and next steps.
- Timeout: save an artifact with partial output if available, timeout status, and a focused retry suggestion.
- Potentially sensitive artifact: warn that artifacts should be reviewed before commit or sharing.

## Test and verification plan

### Static contract checks

- Plugin manifest exists and names the plugin `external-review`.
- Manifest points to the plugin skill directory.
- Namespaced skill surfaces exist for `external-review:ask`, `external-review:ask-codewhale`, and `external-review:ask-claude`.
- Shared principles file exists and is referenced by all three skills.
- Public skill text does not advertise bare `$ask` as the official plugin entrypoint.
- Router text states high-confidence routing, ambiguity stop, and no fallback.
- CodeWhale provider text preserves short prompt, agentic repo explore, read-only review, and artifact rules.
- Claude provider text includes short prompt, allowed read-only tools, no session persistence, and artifact rules.
- `.external-review/tmp/` is ignored.

### Dogfood checks after implementation

- Run a read-only CodeWhale review smoke test and save an artifact.
- Run a read-only Claude review smoke test and save an artifact.
- Verify each dogfood prompt is short and does not paste full repository context.
- Verify artifacts capture prompt, command shape, exit status, output, synthesis, and next steps.

## Implementation sequencing

1. Add plugin manifest and namespaced skill structure.
2. Add shared principles file.
3. Move or adapt the current ask-codewhale skill into the namespaced provider shape.
4. Add Claude provider skill using the same shared principles.
5. Add the thin router skill.
6. Update ignore rules for `.external-review/tmp/`.
7. Run static contract checks.
8. Dogfood CodeWhale and Claude review flows when local CLIs are available.

## Acceptance criteria

- The plugin is named `external-review`.
- Official invocation is namespaced as `$external-review:*`.
- Shared review principles are centralized rather than duplicated across provider skills.
- `external-review:ask` is a thin router and does not call provider CLIs directly.
- Provider skills contain only provider-specific execution differences plus references to shared principles.
- Prompts remain short and agentic; repo context is explored by the external agent.
- Artifacts and temporary files live under `.external-review/`.
- No runtime or skill dependency is introduced on `docs/external_review_rules.md`.
