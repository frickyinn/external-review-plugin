# External Review GitHub Distribution Design

Date: 2026-06-04
Status: Approved design; implementation not started

## Goal

Package the current `external-review` Codex plugin as a GitHub-open-source, marketplace-first project that different users and machines can install through Codex. The repository should be publishable as `external-review`, with a clear root README, a marketplace entry, and the plugin bundle isolated under `plugins/external-review/`.

## Confirmed decisions

- Distribution path: GitHub marketplace-first.
- Repository shape: marketplace wrapper repository, not plugin-at-root.
- Public repository name and positioning: `external-review`.
- Provider support: Claude and CodeWhale are both fully supported local providers.
- README provider wording: present Claude and CodeWhale as peer providers; do not rank the providers.
- CodeWhale explanation: include a short public-facing explanation based on official CodeWhale materials, with links to the official site and docs.
- Recommended packaging approach: release-ready packaging, not a minimal wrapper and not a multi-plugin platform.

## Source-of-truth boundaries

- Root repository: public marketplace wrapper, README, installation guidance, and maintainer/developer instructions.
- Plugin bundle: `plugins/external-review/`.
- Plugin manifest: `plugins/external-review/.codex-plugin/plugin.json`.
- Plugin skills: `plugins/external-review/skills/`.
- Shared runtime principles: `plugins/external-review/shared/external-review-principles.md`.
- Contract validator: `plugins/external-review/scripts/validate_external_review_contract.py`.
- Runtime artifacts created by the plugin: `.external-review/artifacts/` in the user's working repository, not inside the plugin bundle.
- Temporary runtime files: `.external-review/tmp/`, ignored by git.
- Existing `.ask-codewhale/` dogfood artifacts are historical local evidence, not part of the public release package unless explicitly sanitized and selected.
- `docs/external_review_rules.md` is local planning/runtime reference material and must not become a public README dependency.

## Recommended repository structure

```text
external-review/
  README.md
  LICENSE
  .agents/
    plugins/
      marketplace.json
  plugins/
    external-review/
      .codex-plugin/
        plugin.json
      skills/
        ask/
          SKILL.md
        ask-claude/
          SKILL.md
        ask-codewhale/
          SKILL.md
      shared/
        external-review-principles.md
      scripts/
        validate_external_review_contract.py
  docs/
    superpowers/
      specs/
        ...
```

The root is the GitHub project and marketplace source. The plugin bundle lives under `plugins/external-review/` so public project docs, design specs, CI files, and release material do not pollute the plugin package boundary.

## Marketplace design

Add a marketplace file at:

```text
.agents/plugins/marketplace.json
```

It should expose one plugin entry, `external-review`, and point to the plugin bundle using a root-relative local source path:

```json
{
  "name": "external-review",
  "plugins": [
    {
      "name": "external-review",
      "source": {
        "source": "local",
        "path": "./plugins/external-review"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Developer Tools"
    }
  ]
}
```

This follows Codex plugin marketplace guidance: Codex can add and track a Git-backed marketplace, and each marketplace entry points at a plugin folder through `source.path`.

## README design

The README should make the project usable by someone who has not seen the local dogfood history.

### Opening

Explain the plugin in one sentence:

```text
external-review is a Codex plugin for read-only second opinions from local external coding agents.
```

Immediately state the safety boundary:

- It is for review, critique, and advisory second opinions.
- It is not a task runner.
- It does not ask external agents to edit files, run destructive actions, or operate external production systems.
- Codex remains responsible for synthesis, verification, and final decisions.

### Supported providers

Show Claude and CodeWhale as peer local providers:

```text
$external-review:ask-claude <review task>
$external-review:ask-codewhale <review task>
$external-review:ask <prompt naming Claude or CodeWhale>
```

Do not use priority wording that ranks one provider above the other. It is acceptable for README examples to list Claude before CodeWhale, but the prose should describe them as separately supported provider skills.

### Provider requirements

Claude requirement:

- User must have the local `claude` CLI installed.
- User must complete Claude's own authentication/setup.
- The plugin does not install or authenticate Claude for the user.

CodeWhale requirement:

- User must have the local `codewhale` CLI installed.
- User must complete CodeWhale's own authentication/setup.
- The plugin does not install or authenticate CodeWhale for the user.

CodeWhale explanation:

- Briefly describe CodeWhale as a terminal-native coding agent / DeepSeek-first coding agent that can inspect a project from the terminal and operate under mode, approval, and sandbox controls.
- Link to official CodeWhale materials:
  - https://www.codewhale.net/
  - https://codewhale.net/en/docs

### Installation

Primary public installation path:

```bash
codex plugin marketplace add owner/external-review
```

The README should instruct maintainers to replace `owner/external-review` with the real GitHub owner/repo before publishing.

User flow after adding the marketplace:

1. Restart Codex or refresh the plugin directory.
2. Open `/plugins`.
3. Select `External Review`.
4. Install and enable it.
5. Start a new Codex thread before using the plugin.

### Usage examples

Examples should cover:

```text
$external-review:ask-claude Review this implementation for correctness and missed edge cases.

$external-review:ask-codewhale Review the current diff for API boundary problems.

$external-review:ask Ask Claude to review README.md for install clarity.
```

Router examples must explicitly name exactly one provider. The README should explain that the router asks for clarification when no provider or multiple providers are named.

### Safety and privacy

README must include:

- Provider output is advisory evidence, not final truth.
- Prompts should be short and repo-aware: task, target paths, constraints, expected output.
- Do not paste broad diffs, whole repo context, or large file bodies when the provider can inspect the checkout itself.
- The plugin must not silently fallback across providers.
- Artifacts under `.external-review/artifacts/` may contain prompts, private paths, source excerpts, model output, or secrets.
- Users must review artifacts before committing or sharing them.
- `.external-review/tmp/` is temporary scratch and must not be committed.

### Developer section

Include a maintainer/developer section covering:

- Repository layout.
- Plugin bundle path.
- Validator command:

```bash
python3 plugins/external-review/scripts/validate_external_review_contract.py
```

- Packaging sanity checks.
- Release checklist.

## Runtime flow

### Direct provider skill

1. User invokes `$external-review:ask-claude <task>` or `$external-review:ask-codewhale <task>`.
2. Codex loads the selected provider skill.
3. The provider skill reads `../../shared/external-review-principles.md` from inside the installed plugin bundle.
4. The provider constructs a short prompt from the task, target paths, constraints, and expected output.
5. The local provider CLI performs read-only review and may inspect the checkout itself.
6. The provider saves an artifact under `.external-review/artifacts/` in the user's active working repository.
7. Codex synthesizes the external advice and decides follow-up.

### Router skill

1. User invokes `$external-review:ask <prompt>`.
2. The router checks whether exactly one provider is named.
3. Mentions of Claude route to `$external-review:ask-claude`.
4. Mentions of CodeWhale route to `$external-review:ask-codewhale`.
5. No provider, multiple providers, or requests for a default/best/automatic reviewer stop with a clarification request.
6. The router does not call provider CLIs directly and does not guess a provider from task type.

## Error handling

- Missing Claude CLI: report that Claude is required for `$external-review:ask-claude`; do not fallback to CodeWhale.
- Missing CodeWhale CLI: report that CodeWhale is required for `$external-review:ask-codewhale`; do not fallback to Claude.
- Ambiguous router prompt: ask the user to choose exactly one provider.
- No meaningful review target: ask for a task, path, or diff scope.
- Provider nonzero exit after execution begins: save an artifact with command shape, exit code, stdout/stderr, provider output when available, Codex synthesis, and next steps.
- Timeout: save partial evidence when available and suggest a narrower retry.
- Sensitive artifact risk: warn users to review artifacts before commit or sharing.

## Verification plan

After implementation, run:

```bash
python3 plugins/external-review/scripts/validate_external_review_contract.py
```

The validator should prove:

- The manifest name is `external-review`.
- The manifest `skills` path remains `./skills/` relative to the plugin bundle.
- All skill frontmatter names match their directories.
- All skills reference `../../shared/external-review-principles.md` and the reference resolves correctly inside the plugin bundle.
- The simulated plugin-root package contains the shared principles file and can resolve it from every skill.
- Public skill text uses `$external-review:*` examples rather than bare `$ask*` as official plugin entrypoints.
- The skills do not depend on `docs/external_review_rules.md`.
- `.external-review/tmp/` is ignored.

Also verify:

```bash
git diff --check
git status --short
```

Optional dogfood checks when local CLIs are available:

- Run one Claude review smoke.
- Run one CodeWhale review smoke.
- Confirm prompts are short and do not paste broad repository context.
- Confirm artifacts contain the required sections and are not automatically staged.

## Open-source cleanup plan

Before publishing:

1. Move the plugin bundle into `plugins/external-review/`.
2. Move the validator into `plugins/external-review/scripts/` and update path assumptions if necessary.
3. Add `.agents/plugins/marketplace.json`.
4. Add root `README.md`.
5. Add or confirm `LICENSE`.
6. Update `.gitignore` for root-level local state:
   - ignore `.omx/`,
   - ignore `.external-review/tmp/`,
   - keep `.external-review/artifacts/` untracked unless a reviewed sample artifact is intentionally selected.
7. Do not publish `.external-review/tmp/` or `.omx/`.
8. Do not publish unsanitized dogfood artifacts.
9. Either remove `docs/external_review_rules.md` from the public package or keep it only as clearly internal/reference material that README does not depend on.
10. Remove stale repo-local skill shims if they conflict with plugin packaging.
11. Replace README placeholder `owner/external-review` with the actual GitHub owner/repo before public release.

## Scope exclusions

- No CI or release automation in this design.
- No npm, Cargo, Homebrew, or binary packaging.
- No provider CLI auto-installation.
- No provider authentication automation.
- No new providers.
- No write-capable external-agent delegation mode.
- No configuration UI.
- No multi-plugin platform governance beyond the wrapper structure needed for this one plugin.
- No migration of historical `.ask-codewhale/` artifacts into the plugin package.

## Success criteria

The packaging work is complete when:

- The repository root reads like a publishable GitHub project named `external-review`.
- `README.md` explains purpose, install, usage, provider requirements, CodeWhale context, safety, artifacts, troubleshooting, and developer verification.
- `.agents/plugins/marketplace.json` exposes `plugins/external-review/` as an installable plugin.
- The plugin bundle is isolated under `plugins/external-review/`.
- The validator passes from the root command.
- No local runtime state or unsanitized artifacts are part of the public release surface.
- Users on other machines can install the plugin through the Codex marketplace flow and use the namespaced `$external-review:*` skills after installing local provider CLIs.

## Self-review

- No placeholders remain except the intentional README publication placeholder `owner/external-review`, which must be replaced before release.
- The design does not contradict the already-approved `external-review` read-only plugin boundary.
- The repo shape is focused on one publishable plugin and does not become a general multi-plugin platform.
- The README wording treats Claude and CodeWhale as peer providers without priority phrasing.
- CodeWhale is explained through official public links rather than assumed local knowledge.
