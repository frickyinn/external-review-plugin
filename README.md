# External Review for Codex

`external-review` is a small personal Codex plugin for read-only second opinions from local coding agents.

Use it when you want Claude or CodeWhale to look at a plan, implementation, README, skill, or current diff while Codex keeps ownership of the final decision. This is intentionally lightweight: it is a plugin wrapper around local CLIs, not an official review system or task runner.

## What it adds

```text
$external-review:ask-claude [--model <model>] [--effort <effort>] <review task>
$external-review:ask-codewhale <review task>
$external-review:ask <prompt naming Claude or CodeWhale>
```

- `$external-review:ask-claude` uses your local `claude` CLI. It defaults to `--model opus --effort high`; pass leading `--model` or `--effort` options to override those values.
- `$external-review:ask-codewhale` uses your local `codewhale` CLI.
- `$external-review:ask` is only a router. It works when the prompt names exactly one provider; it will not choose a default or silently fall back.

The plugin asks for advisory review only. It tells the external provider not to edit files, run destructive commands, or operate production systems.

## Requirements

Install and authenticate Codex plus at least one provider CLI yourself:

- `claude` for `$external-review:ask-claude`
- `codewhale` for `$external-review:ask-codewhale`

The plugin does not install providers or manage their credentials.

## Install from GitHub

Add this repository as a Codex plugin marketplace:

```bash
codex plugin marketplace add frickyinn/external-review-plugin
```

Then restart Codex, open `/plugins`, install **External Review**, and start a new Codex thread before using the skills.

Updates with:

```bash
codex plugin marketplace upgrade external-review
```

## Examples

Ask Claude for an implementation review:

```text
$external-review:ask-claude Review this implementation for correctness and missed edge cases.
```

Ask Claude with an explicit model and effort:

```text
$external-review:ask-claude --model sonnet --effort medium Review README.md for install clarity.
```

Ask CodeWhale to inspect the current diff:

```text
$external-review:ask-codewhale Review the current diff for API boundary problems.
```

Use the router only when the prompt clearly names one provider:

```text
$external-review:ask Ask Claude to review README.md for install clarity.
```

## Copy into AGENTS.md or CLAUDE.md

If you want a repo to remember this workflow, copy this small policy into that repo's `AGENTS.md` or `CLAUDE.md`:

```md
## External review policy

For plan, code, or documentation reviews, use the External Review Codex plugin: `$external-review:ask-claude [--model <model>] [--effort <effort>] <review task>` or `$external-review:ask-codewhale <review task>`. Treat the result as advisory evidence, review the generated `.external-review/artifacts/` artifact, and verify advice against the repo docs, code, and tests.
```

## Artifacts and privacy

When a provider execution begins, the plugin records evidence in the working repository:

```text
.external-review/artifacts/
.external-review/tmp/
```

Artifacts may contain prompts, private paths, source excerpts, model output, or secrets. Review them before committing or sharing. Temporary files under `.external-review/tmp/` are scratch files and should not be committed.

## Troubleshooting

- If the plugin does not appear in `/plugins`, confirm the marketplace was added with `codex plugin marketplace add frickyinn/external-review-plugin`, then restart Codex.
- If Claude or CodeWhale is unavailable, confirm the matching CLI is on `PATH` and authenticated. The plugin will not switch providers for you.
- If the router stops for clarification, use a direct provider skill or make the prompt name exactly one provider.

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

## Developer checks

```bash
python3 plugins/external-review/scripts/validate_external_review_contract.py
python3 -m json.tool .agents/plugins/marketplace.json >/dev/null
python3 -m json.tool plugins/external-review/.codex-plugin/plugin.json >/dev/null
git diff --check
git diff --cached --check
git ls-files .omx .ask-codewhale .external-review
git check-ignore .omx/example .external-review/tmp/example .external-review/artifacts/example
```

## License

MIT. See [`LICENSE`](LICENSE).
