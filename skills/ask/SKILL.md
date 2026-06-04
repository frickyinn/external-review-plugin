---
name: ask
description: Route a namespaced External Review request to exactly one provider skill when the prompt clearly names CodeWhale or Claude; use for read-only external review/advice only.
---

# External Review Router

Use this skill as the thin router for the `external-review` plugin.

Official usage:

```bash
$external-review:ask <prompt naming exactly one provider>
```

Before routing, read and apply `../../shared/external-review-principles.md`.

## Routing contract

Route only inside this plugin and only when the prompt names exactly one provider with high confidence:

- Mentions of `claude` or `ask-claude` route to `external-review:ask-claude`.
- Mentions of `codewhale` or `ask-codewhale` route to `external-review:ask-codewhale`.

If no provider is named, stop and ask the user to specify either CodeWhale or Claude.

If multiple providers are named, stop and ask the user to choose exactly one provider.

If the wording asks for the best, default, automatic, or recommended reviewer without naming one provider, stop and ask for an explicit provider.

## Router boundaries

- Do not guess a provider from task type.
- Do not call CodeWhale or Claude CLIs directly from this router.
- Do not route through another global or unrelated skill.
- Do not fallback to a different provider when the selected provider is unavailable.
- Keep all provider execution details in the provider skills.

## Output expectation

After routing, synthesize the selected provider's advisory output and cite the artifact path when one was produced.

Task: {{ARGUMENTS}}
