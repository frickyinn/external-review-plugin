# External Review

`external-review` is a Codex plugin for read-only second opinions from local external coding agents.

Use it when you want Claude or CodeWhale to review a plan, implementation, README, skill, or current diff while Codex keeps ownership of synthesis and final decisions. The plugin is advisory only: it is not a task runner, it does not ask external agents to edit files, and it does not perform destructive or production actions.

## What it provides

The plugin installs three namespaced skills:

```text
$external-review:ask-claude <review task>
$external-review:ask-codewhale <review task>
$external-review:ask <prompt naming Claude or CodeWhale>
```

Claude and CodeWhale are supported as peer local providers. The router skill only routes when your prompt names exactly one provider; it does not make a provider choice for you and it does not fall back from one provider to another.

## Provider requirements

### Claude

To use `$external-review:ask-claude`, install and authenticate the local `claude` CLI yourself. This plugin does not install Claude or manage Claude credentials.

### CodeWhale

To use `$external-review:ask-codewhale`, install and authenticate the local `codewhale` CLI yourself. This plugin does not install CodeWhale or manage CodeWhale credentials.

CodeWhale is a terminal-native coding agent. Its official materials describe it as a DeepSeek-first coding agent that can work with local projects from the terminal and operate with mode, approval, and sandbox controls. See the official site and docs:

- https://www.codewhale.net/
- https://codewhale.net/en/docs

## Install from GitHub

Add this repository as a Codex plugin marketplace:

```bash
codex plugin marketplace add frickyinn/external-review-plugin
```

After adding the marketplace:

1. Restart Codex or refresh the plugin directory.
2. Open `/plugins`.
3. Select **External Review**.
4. Install and enable the plugin.
5. Start a new Codex thread before using the `$external-review:*` skills.

## Usage examples

Ask Claude for an implementation review:

```text
$external-review:ask-claude Review this implementation for correctness and missed edge cases.
```

Ask CodeWhale to inspect the current diff:

```text
$external-review:ask-codewhale Review the current diff for API boundary problems.
```

Use the router when the prompt clearly names exactly one provider:

```text
$external-review:ask Ask Claude to review README.md for install clarity.
```

If the router prompt names no provider, names multiple providers, or asks for the best/default/automatic reviewer, Codex should stop and ask you to choose exactly one provider.

## Safety model

`external-review` is intentionally narrow:

- External provider output is advisory evidence, not final truth.
- Codex remains responsible for verification, synthesis, and final decisions.
- Prompts should be short and repo-aware: task, target paths or diff scope, constraints, and expected output.
- Do not paste broad diffs, whole repository context, large file bodies, or untracked artifact contents when the provider can inspect the checkout itself.
- Do not ask the provider to edit files, run destructive commands, perform credentialed actions, or operate external production systems.
- Provider failures do not trigger hidden fallback to another provider.

## Artifacts and privacy

When a provider execution begins, the plugin records review evidence under the working repository:

```text
.external-review/artifacts/
.external-review/tmp/
```

Artifacts may contain prompts, private paths, source excerpts, model output, or secrets. Review artifacts before committing or sharing them. Temporary files under `.external-review/tmp/` are scratch files and should not be committed.

## Troubleshooting

### The plugin does not appear in `/plugins`

- Confirm the marketplace was added with `codex plugin marketplace add frickyinn/external-review-plugin`.
- Run `codex plugin marketplace list` to inspect configured marketplace roots.
- Restart Codex after changing marketplace configuration.
- Confirm this repository contains `.agents/plugins/marketplace.json` and `plugins/external-review/.codex-plugin/plugin.json`.

### Claude or CodeWhale is unavailable

- Confirm the relevant CLI exists on your `PATH`:
  - `claude` for `$external-review:ask-claude`
  - `codewhale` for `$external-review:ask-codewhale`
- Complete the provider's own authentication/setup.
- Re-run the selected provider skill. The plugin will not silently switch providers.

### A router prompt stops for clarification

Use a direct provider skill, or make the router prompt name exactly one provider:

```text
$external-review:ask Ask Claude to review the current plan.
$external-review:ask Ask CodeWhale to review the current diff.
```

## Repository layout

```text
external-review/
  README.md
  LICENSE
  .agents/plugins/marketplace.json
  plugins/external-review/
    .codex-plugin/plugin.json
    skills/
      ask/SKILL.md
      ask-claude/SKILL.md
      ask-codewhale/SKILL.md
    shared/external-review-principles.md
    scripts/validate_external_review_contract.py
```

The repository root is the GitHub marketplace wrapper. The installable Codex plugin bundle lives in `plugins/external-review/`.

## Developer validation

Run these checks from the repository root:

```bash
python3 plugins/external-review/scripts/validate_external_review_contract.py
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool plugins/external-review/.codex-plugin/plugin.json >/dev/null
git diff --check
git diff --cached --check
git status --short
git ls-files .omx .ask-codewhale .external-review
git check-ignore .omx/example .external-review/tmp/example .external-review/artifacts/example
```

Use `git status --short` and `git ls-files` to confirm local runtime files and unsanitized artifacts are not part of the intended release commit. `git check-ignore` should report ignored local scratch paths such as `.omx/` and `.external-review/tmp/`.

Optional dogfood checks, when local provider CLIs are installed and authenticated:

- Run one Claude review smoke.
- Run one CodeWhale review smoke.
- Confirm prompts are short and do not paste broad repository context.
- Confirm generated artifacts are reviewed before any commit or sharing.

## Release checklist

Before publishing:

- Confirm `python3 plugins/external-review/scripts/validate_external_review_contract.py` passes.
- Confirm `.agents/plugins/marketplace.json` points to `./plugins/external-review`.
- Confirm `plugins/external-review/.codex-plugin/plugin.json` has the intended version, homepage, repository, and license.
- Do not publish `.omx/`, `.external-review/tmp/`, or unsanitized local dogfood artifacts.
- Review any artifact intentionally force-added under `.external-review/artifacts/` for private paths, source excerpts, model output, and secrets.

## License

MIT. See [`LICENSE`](LICENSE).
