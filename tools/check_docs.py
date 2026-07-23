#!/usr/bin/env python3
"""Doc-drift checker for the OVOS Technical Manual (mkdocs-material site).

Subcommands: links, json, python-imports, signatures, all

Stdlib only (yaml is optional, only used to validate the workflow file
separately, not by this script).
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

DOCS_DIR = Path("docs")
ALLOWLIST_PATH = Path("tools/docs_checks_allowlist.yaml")

FENCE_RE = re.compile(r"^(?P<indent>[ \t]*)```(?P<lang>[a-zA-Z0-9_-]*)[ \t]*\n(?P<body>.*?)^(?P=indent)```[ \t]*$",
                       re.DOTALL | re.MULTILINE)
LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
IMG_RE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
SKIP_NEXT_RE = re.compile(r"<!--\s*docs-check:\s*skip-next\s*-->")


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def load_allowlist() -> dict:
    """Very small YAML-ish loader for our own allowlist file (no PyYAML dep).

    Expected shape (simple, hand-authored):

        json:
          - file: docs/foo.md
            reason: "fragment example, not standalone json"
        python_imports:
          - module: my_skill
            reason: "template placeholder"
        signatures:
          - file: docs/bar.md
            reason: "..."
    """
    if not ALLOWLIST_PATH.exists():
        return {"json": [], "python_imports": [], "signatures": []}
    try:
        import yaml  # type: ignore
        with open(ALLOWLIST_PATH) as f:
            data = yaml.safe_load(f) or {}
    except Exception:
        data = _naive_yaml_parse(ALLOWLIST_PATH.read_text())
    data.setdefault("json", [])
    data.setdefault("python_imports", [])
    data.setdefault("signatures", [])
    return data


def _naive_yaml_parse(text: str) -> dict:
    """Extremely small fallback parser for our restricted allowlist schema,
    used only if PyYAML is unavailable. Handles:

        key:
          - subkey: value
            subkey2: "value"
    """
    result: dict = {}
    current_key = None
    current_item: dict | None = None
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line or line.strip().startswith("#"):
            continue
        if not line.startswith(" ") and line.endswith(":"):
            current_key = line[:-1].strip()
            result[current_key] = []
            current_item = None
            continue
        stripped = line.strip()
        if stripped.startswith("- "):
            if current_item is not None and current_key:
                result[current_key].append(current_item)
            current_item = {}
            stripped = stripped[2:]
        if ":" in stripped and current_item is not None:
            k, _, v = stripped.partition(":")
            v = v.strip().strip('"').strip("'")
            current_item[k.strip()] = v
    if current_item is not None and current_key:
        result[current_key].append(current_item)
    return result


def iter_fences(text: str):
    """Yield (lang, body, start_line) for every fenced code block."""
    for m in FENCE_RE.finditer(text):
        lang = m.group("lang") or ""
        body = m.group("body")
        start_line = text[: m.start()].count("\n") + 1
        # detect a skip-next comment immediately preceding the fence
        preceding = text[: m.start()]
        prev_line = preceding.rstrip("\n").rsplit("\n", 1)[-1] if preceding.strip() else ""
        skip = bool(SKIP_NEXT_RE.search(prev_line))
        yield lang, body, start_line, skip


def slugify_heading(text: str) -> str:
    """Approximate GitHub/mkdocs-material heading slug algorithm."""
    text = re.sub(r"<[^>]+>", "", text)  # strip inline html
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text


def all_md_files():
    return sorted(DOCS_DIR.rglob("*.md"))


# ---------------------------------------------------------------------------
# Check: links
# ---------------------------------------------------------------------------

def check_links() -> tuple[int, int, list[str]]:
    failures: list[str] = []
    passed = 0

    # Precompute heading slugs per file
    headings_by_file: dict[Path, set[str]] = {}
    for f in all_md_files():
        text = f.read_text(errors="replace")
        slugs = set()
        for m in HEADING_RE.finditer(text):
            slugs.add(slugify_heading(m.group(2)))
        headings_by_file[f] = slugs

    for f in all_md_files():
        text = f.read_text(errors="replace")
        links = [(m.start(), m.group(1)) for m in LINK_RE.finditer(text)]
        imgs = [(m.start(), m.group(1)) for m in IMG_RE.finditer(text)]
        for pos, target in links:
            lineno = text[:pos].count("\n") + 1
            ok, msg = _check_link(f, target, headings_by_file)
            if ok:
                passed += 1
            else:
                failures.append(f"{f}:{lineno}: link '{target}' -> {msg}")
        for pos, target in imgs:
            lineno = text[:pos].count("\n") + 1
            ok, msg = _check_image(f, target)
            if ok:
                passed += 1
            else:
                failures.append(f"{f}:{lineno}: image '{target}' -> {msg}")
    return passed, len(failures), failures


def _check_link(src: Path, target: str, headings_by_file) -> tuple[bool, str]:
    if target.startswith(("http://", "https://", "mailto:")):
        return True, ""
    if target.startswith("#"):
        anchor = target[1:]
        slugs = headings_by_file.get(src, set())
        if anchor in slugs:
            return True, ""
        return False, f"anchor #{anchor} not found in {src}"
    path_part, _, anchor = target.partition("#")
    if not path_part:
        return True, ""
    resolved = (src.parent / unquote(path_part)).resolve()
    if not resolved.exists():
        return False, f"file not found: {path_part}"
    if anchor:
        if resolved.suffix != ".md":
            return True, ""
        slugs = headings_by_file.get(resolved)
        if slugs is None:
            text = resolved.read_text(errors="replace")
            slugs = {slugify_heading(m.group(2)) for m in HEADING_RE.finditer(text)}
            headings_by_file[resolved] = slugs
        if anchor not in slugs:
            return False, f"anchor #{anchor} not found in {path_part}"
    return True, ""


def _check_image(src: Path, target: str) -> tuple[bool, str]:
    if target.startswith(("http://", "https://")):
        return True, ""
    resolved = (src.parent / unquote(target)).resolve()
    if not resolved.exists():
        return False, f"image not found: {target}"
    return True, ""


# ---------------------------------------------------------------------------
# Check: json
# ---------------------------------------------------------------------------

def strip_jsonc_comments(s: str) -> str:
    # remove // line comments (not inside strings) - simple state machine
    out = []
    in_str = False
    str_ch = ""
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if in_str:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(s[i + 1])
                i += 2
                continue
            if c == str_ch:
                in_str = False
            i += 1
            continue
        if c in ('"', "'"):
            in_str = True
            str_ch = c
            out.append(c)
            i += 1
            continue
        if c == "/" and i + 1 < n and s[i + 1] == "/":
            while i < n and s[i] != "\n":
                i += 1
            continue
        if c == "/" and i + 1 < n and s[i + 1] == "*":
            i += 2
            while i + 1 < n and not (s[i] == "*" and s[i + 1] == "/"):
                i += 1
            i += 2
            continue
        out.append(c)
        i += 1
    # strip trailing commas
    return re.sub(r",(\s*[}\]])", r"\1", "".join(out))


def check_json(allowlist) -> tuple[int, int, list[str]]:
    failures: list[str] = []
    passed = 0
    allow_files = {a.get("file") for a in allowlist.get("json", [])}
    for f in all_md_files():
        text = f.read_text(errors="replace")
        for lang, body, lineno, skip in iter_fences(text):
            if lang.lower() not in ("json", "json5", "jsonc"):
                continue
            if skip:
                continue
            if not body.strip():
                continue
            content = body
            is_relaxed = lang.lower() in ("json5", "jsonc")
            if is_relaxed:
                content = strip_jsonc_comments(body)
            try:
                json.loads(content)
                passed += 1
                continue
            except Exception as e:
                last_err = e
            # jsonc/json5 fences may be intentional config *fragments* (a
            # snippet meant to be merged into mycroft.conf, not a standalone
            # document) - accept if wrapping in an object brace parses.
            if is_relaxed:
                try:
                    json.loads("{" + content + "}")
                    passed += 1
                    continue
                except Exception as e:
                    last_err = e
            if str(f) in allow_files:
                passed += 1
                continue
            failures.append(f"{f}:{lineno}: json fence invalid ({lang or 'json'}): {last_err}")
    return passed, len(failures), failures


# ---------------------------------------------------------------------------
# Check: python-imports
# ---------------------------------------------------------------------------

def _default_venv_py() -> str:
    """Prefer an explicit override, then the shared OVOS dev venv (local
    dev machines), falling back to whatever `python3` is currently running
    under (CI runners that pip-install straight into the job's venv)."""
    override = os.environ.get("DOCS_CHECK_PYTHON")
    if override:
        return override
    shared = os.path.expanduser("~/.venvs/ovos/bin/python")
    if os.path.exists(shared):
        return shared
    return sys.executable


VENV_PY = _default_venv_py()


def _extract_imports(body: str) -> list[tuple[str, str | None, int]]:
    """Return list of (module, attr_or_None, lineno) for top-level import lines."""
    results = []
    try:
        tree = ast.parse(body)
    except SyntaxError:
        return results
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                results.append((alias.name, None, node.lineno))
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.level > 0:
                continue  # relative import, skip
            mod = node.module or ""
            for alias in node.names:
                if alias.name == "*":
                    continue
                results.append((mod, alias.name, node.lineno))
    return results


def _venv_available() -> bool:
    return os.path.exists(VENV_PY)


def _check_module_attr(module: str, attr: str | None) -> tuple[bool, str]:
    code = f"import {module}" if attr is None else f"from {module} import {attr}"
    script = f"import sys\ntry:\n    {code}\nexcept Exception as e:\n    print(f'ERR:{{type(e).__name__}}:{{e}}')\n    sys.exit(1)\nsys.exit(0)\n"
    env = dict(os.environ)
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    try:
        proc = subprocess.run([VENV_PY, "-c", script], capture_output=True, text=True, timeout=30, env=env)
    except Exception as e:
        return False, str(e)
    if proc.returncode == 0:
        return True, ""
    return False, (proc.stdout.strip() or proc.stderr.strip().splitlines()[-1] if proc.stderr else "import failed")


def check_python_imports(allowlist) -> tuple[int, int, list[str]]:
    failures: list[str] = []
    passed = 0
    allow_modules = {a.get("module") for a in allowlist.get("python_imports", [])}

    if not _venv_available():
        return 0, 0, [f"SKIPPED: venv python not found at {VENV_PY}"]

    cache: dict[tuple[str, str | None], tuple[bool, str]] = {}

    for f in all_md_files():
        text = f.read_text(errors="replace")
        for lang, body, lineno, skip in iter_fences(text):
            if lang.lower() != "python":
                continue
            if skip:
                continue
            for module, attr, rel_line in _extract_imports(body):
                if not module:
                    continue
                top = module.split(".")[0]
                if top in allow_modules or module in allow_modules:
                    passed += 1
                    continue
                key = (module, attr)
                if key not in cache:
                    cache[key] = _check_module_attr(module, attr)
                ok, msg = cache[key]
                actual_line = lineno + rel_line - 1
                if ok:
                    passed += 1
                else:
                    what = module if attr is None else f"{module}.{attr}"
                    failures.append(f"{f}:{actual_line}: import '{what}' failed: {msg}")
    return passed, len(failures), failures


# ---------------------------------------------------------------------------
# Check: signatures (best effort)
# ---------------------------------------------------------------------------

CALL_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)\s*\(")
ASSIGN_CALL_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*=\s*([A-Za-z_][A-Za-z0-9_.]*)\s*\(")


def _resolve_import_map(body: str) -> dict[str, str]:
    """Map local name -> fully qualified dotted path, for top-level imports."""
    mapping = {}
    try:
        tree = ast.parse(body)
    except SyntaxError:
        return mapping
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                local = alias.asname or alias.name.split(".")[0]
                mapping[local] = alias.name
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.level > 0:
                continue
            mod = node.module or ""
            for alias in node.names:
                if alias.name == "*":
                    continue
                local = alias.asname or alias.name
                mapping[local] = f"{mod}.{alias.name}"
    return mapping


def _check_attr_chain(dotted: str, attr: str) -> tuple[bool | None, str]:
    """Returns (True/False/None-ambiguous, msg)."""
    script = (
        "import sys\n"
        "try:\n"
        f"    import importlib\n"
        f"    parts = '{dotted}'.split('.')\n"
        "    obj = None\n"
        "    for i in range(len(parts), 0, -1):\n"
        "        try:\n"
        "            obj = importlib.import_module('.'.join(parts[:i]))\n"
        "            rest = parts[i:]\n"
        "            break\n"
        "        except Exception:\n"
        "            continue\n"
        "    else:\n"
        "        print('AMBIGUOUS: cannot import base'); sys.exit(2)\n"
        "    for r in rest:\n"
        "        obj = getattr(obj, r)\n"
        f"    ok = hasattr(obj, '{attr}')\n"
        "    print('OK' if ok else 'MISSING')\n"
        "    sys.exit(0 if ok else 1)\n"
        "except Exception as e:\n"
        "    print(f'AMBIGUOUS:{type(e).__name__}:{e}')\n"
        "    sys.exit(2)\n"
    )
    env = dict(os.environ)
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    try:
        proc = subprocess.run([VENV_PY, "-c", script], capture_output=True, text=True, timeout=30, env=env)
    except Exception as e:
        return None, str(e)
    out = proc.stdout.strip()
    if out == "OK":
        return True, ""
    if out == "MISSING":
        return False, f"attribute '{attr}' missing on {dotted}"
    return None, out or proc.stderr.strip()


def check_signatures(allowlist) -> tuple[int, int, list[str]]:
    failures: list[str] = []
    passed = 0
    if not _venv_available():
        return 0, 0, [f"SKIPPED: venv python not found at {VENV_PY}"]

    allow_files = {a.get("file") for a in allowlist.get("signatures", [])}

    for f in all_md_files():
        if str(f) in allow_files:
            continue
        text = f.read_text(errors="replace")
        for lang, body, lineno, skip in iter_fences(text):
            if lang.lower() != "python" or skip:
                continue
            import_map = _resolve_import_map(body)
            if not import_map:
                continue
            for m in list(CALL_RE.finditer(body)) + []:
                name, attr = m.group(1), m.group(2)
                if name not in import_map:
                    continue
                dotted = import_map[name]
                ok, msg = _check_attr_chain(dotted, attr)
                if ok is None:
                    continue  # ambiguous -> skip, no false positives
                if ok:
                    passed += 1
                else:
                    rel_line = body[: m.start()].count("\n") + 1
                    failures.append(f"{f}:{lineno + rel_line - 1}: {msg}")
    return passed, len(failures), failures


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _report(name: str, passed: int, failed: int, failures: list[str]) -> bool:
    print(f"\n=== {name}: {passed} passed, {failed} failed ===")
    for line in failures:
        print(f"  {line}")
    return failed == 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("check", choices=["links", "json", "python-imports", "signatures", "all"])
    args = parser.parse_args()

    allowlist = load_allowlist()
    ok = True

    if args.check in ("links", "all"):
        p, n, fails = check_links()
        ok &= _report("links", p, n, fails)
    if args.check in ("json", "all"):
        p, n, fails = check_json(allowlist)
        ok &= _report("json", p, n, fails)
    if args.check in ("python-imports", "all"):
        p, n, fails = check_python_imports(allowlist)
        ok &= _report("python-imports", p, n, fails)
    if args.check in ("signatures", "all"):
        p, n, fails = check_signatures(allowlist)
        ok &= _report("signatures", p, n, fails)

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
