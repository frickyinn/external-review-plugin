#!/usr/bin/env python3
"""Validate the external-review plugin contract.

This guard complements the generic plugin validator. It proves that the
plugin-level shared principles file is present, resolvable from each skill using
its installed relative path, present in a simulated plugin-root package, and
exposed by the repository marketplace wrapper.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PLUGIN_ROOT.parents[1]
MARKETPLACE = REPO_ROOT / ".agents" / "plugins" / "marketplace.json"
PLUGIN_MANIFEST = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
PUBLIC_REPO_URL = "https://github.com/frickyinn/external-review-plugin"
SHARED = PLUGIN_ROOT / "shared" / "external-review-principles.md"
SKILLS = {
    "ask": PLUGIN_ROOT / "skills" / "ask" / "SKILL.md",
    "ask-codewhale": PLUGIN_ROOT / "skills" / "ask-codewhale" / "SKILL.md",
    "ask-claude": PLUGIN_ROOT / "skills" / "ask-claude" / "SKILL.md",
}
REL_SHARED = Path("../../shared/external-review-principles.md")
FORBIDDEN_RUNTIME_REF = "docs/external_review_rules.md"
BARE_INVOCATIONS = ("$ask ", "$ask-codewhale", "$ask-claude")
REQUIRED_USAGES = (
    "$external-review:ask ",
    "$external-review:ask-codewhale ",
    "$external-review:ask-claude ",
)
BAD_INTERFACE_PHRASES = (
    "cross-agent execution",
    "handoff runtime",
    "autonomous execution",
    "multi-agent task runner",
)


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def display_path(path: Path) -> str:
    for root in (PLUGIN_ROOT, REPO_ROOT):
        try:
            return str(path.relative_to(root))
        except ValueError:
            pass
    return str(path)


def read(path: Path) -> str:
    if not path.exists():
        fail(f"missing required file: {display_path(path)}")
    return path.read_text()


def frontmatter_name(text: str, path: Path) -> str:
    parts = text.split("---", 2)
    if len(parts) < 3:
        fail(f"missing YAML frontmatter: {path.relative_to(PLUGIN_ROOT)}")
    match = re.search(r"^name:\s*([^\n]+)\s*$", parts[1], re.MULTILINE)
    if not match:
        fail(f"missing frontmatter name: {path.relative_to(PLUGIN_ROOT)}")
    return match.group(1).strip().strip('"')


def validate_manifest() -> None:
    manifest = json.loads(read(PLUGIN_MANIFEST))
    if manifest.get("name") != "external-review":
        fail("plugin manifest name must be external-review")
    if manifest.get("skills") != "./skills/":
        fail('plugin manifest skills must be "./skills/"')
    for key in ("homepage", "repository"):
        value = manifest.get(key)
        if value != PUBLIC_REPO_URL:
            fail(f"plugin manifest {key} must be {PUBLIC_REPO_URL}, got {value!r}")
    interface = manifest.get("interface") or {}
    interface_text = " ".join(
        str(value)
        for value in (
            manifest.get("description", ""),
            interface.get("shortDescription", ""),
            interface.get("longDescription", ""),
            *(interface.get("defaultPrompt") or []),
        )
    ).lower()
    if "read-only" not in interface_text:
        fail("manifest interface must position plugin as read-only")
    for phrase in BAD_INTERFACE_PHRASES:
        if phrase in interface_text:
            fail(f"manifest interface uses broad orchestration phrase: {phrase}")


def validate_marketplace() -> None:
    marketplace = json.loads(read(MARKETPLACE))
    if marketplace.get("name") != "external-review":
        fail("marketplace name must be external-review")
    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list) or len(plugins) != 1:
        fail("marketplace must expose exactly one plugin entry")
    entry = plugins[0]
    if entry.get("name") != "external-review":
        fail("marketplace plugin entry name must be external-review")
    source = entry.get("source") or {}
    if source.get("source") != "local":
        fail("marketplace source must be local")
    if source.get("path") != "./plugins/external-review":
        fail('marketplace source.path must be "./plugins/external-review"')
    expected_root = REPO_ROOT / "plugins" / "external-review"
    if not expected_root.exists():
        fail("marketplace source.path target does not exist")


def validate_skills() -> None:
    all_skill_text = ""
    for expected_name, path in SKILLS.items():
        text = read(path)
        all_skill_text += text + "\n"
        actual_name = frontmatter_name(text, path)
        if actual_name != expected_name:
            fail(f"{path.relative_to(PLUGIN_ROOT)} frontmatter name is {actual_name!r}, expected {expected_name!r}")
        if str(REL_SHARED) not in text:
            fail(f"{path.relative_to(PLUGIN_ROOT)} does not reference {REL_SHARED}")
        resolved = (path.parent / REL_SHARED).resolve()
        if resolved != SHARED.resolve():
            fail(f"{path.relative_to(PLUGIN_ROOT)} shared reference resolves to {resolved}, expected {SHARED}")
        if FORBIDDEN_RUNTIME_REF in text:
            fail(f"{path.relative_to(PLUGIN_ROOT)} depends on {FORBIDDEN_RUNTIME_REF}")

    for usage in REQUIRED_USAGES:
        if usage not in all_skill_text:
            fail(f"missing namespaced usage in skills: {usage}")
    for invocation in BARE_INVOCATIONS:
        if invocation in all_skill_text:
            fail(f"public skill text contains bare invocation: {invocation}")


def validate_shared() -> None:
    text = read(SHARED)
    if FORBIDDEN_RUNTIME_REF in text:
        fail(f"shared principles depend on {FORBIDDEN_RUNTIME_REF}")
    for required in ("lowercase ASCII kebab-case", "YYYYMMDDTHHMMSSZ", "not automatically staged or committed"):
        if required not in text:
            fail(f"shared principles missing artifact policy text: {required}")


def validate_gitignore_and_shims() -> None:
    gitignore = read(REPO_ROOT / ".gitignore")
    if not re.search(r"^\.external-review/tmp/$", gitignore, re.MULTILINE):
        fail(".gitignore must ignore .external-review/tmp/")
    if not re.search(r"^\.external-review/artifacts/$", gitignore, re.MULTILINE):
        fail(".gitignore must ignore .external-review/artifacts/")
    for shim in (REPO_ROOT / ".codex" / "skills" / "ask", REPO_ROOT / ".codex" / "skills" / "ask-codewhale", REPO_ROOT / ".codex" / "skills" / "ask-claude"):
        if shim.exists() or shim.is_symlink():
            fail(f"bare project-local skill shim must not exist: {shim.relative_to(REPO_ROOT)}")


def validate_simulated_plugin_root() -> None:
    with tempfile.TemporaryDirectory(prefix="external-review-plugin-") as tmp:
        package_root = Path(tmp) / "external-review"
        package_root.mkdir()
        shutil.copytree(PLUGIN_ROOT / ".codex-plugin", package_root / ".codex-plugin")
        shutil.copytree(PLUGIN_ROOT / "skills", package_root / "skills")
        shutil.copytree(PLUGIN_ROOT / "shared", package_root / "shared")
        copied_shared = package_root / "shared" / "external-review-principles.md"
        if not copied_shared.exists():
            fail("simulated plugin root is missing shared/external-review-principles.md")
        for name in SKILLS:
            copied_skill = package_root / "skills" / name / "SKILL.md"
            resolved = (copied_skill.parent / REL_SHARED).resolve()
            if resolved != copied_shared.resolve() or not resolved.exists():
                fail(f"simulated plugin root cannot resolve shared principles from skill {name}")


def main() -> None:
    validate_marketplace()
    validate_manifest()
    validate_skills()
    validate_shared()
    validate_gitignore_and_shims()
    validate_simulated_plugin_root()
    print("external-review-contract-ok")


if __name__ == "__main__":
    main()
