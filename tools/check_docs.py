#!/usr/bin/env python3
"""Validate plugin usage documentation against plugin source.

Checks performed:
- Every public plugin method has a matching markdown heading.
- Every documented plugin method exists in source.
- Documented parameter names are real parameters.
- Required positional/keyword parameters are documented in the heading.
- Plugin headings are alphabetically ordered.
"""

from __future__ import annotations

import ast
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_DIR = ROOT / "src" / "synack" / "plugins"
DOC_DIR = ROOT / "docs" / "src" / "usage" / "plugins"
IGNORED_PLUGIN_FILES = {"__init__.py", "base.py"}


@dataclass(frozen=True)
class Method:
    name: str
    required_params: tuple[str, ...]
    params: tuple[str, ...]


def decorator_name(decorator: ast.expr) -> str:
    if isinstance(decorator, ast.Name):
        return decorator.id
    if isinstance(decorator, ast.Attribute):
        return decorator.attr
    if isinstance(decorator, ast.Call):
        return decorator_name(decorator.func)
    return ""


def is_property_method(node: ast.FunctionDef) -> bool:
    decorators = {decorator_name(d) for d in node.decorator_list}
    return "property" in decorators or "setter" in decorators


def get_methods(plugin_file: Path) -> dict[str, Method]:
    tree = ast.parse(plugin_file.read_text(), filename=str(plugin_file))
    methods: dict[str, Method] = {}
    for class_node in [n for n in tree.body if isinstance(n, ast.ClassDef)]:
        for node in class_node.body:
            if not isinstance(node, ast.FunctionDef):
                continue
            if node.name.startswith("_") or is_property_method(node):
                continue

            args = list(node.args.posonlyargs) + list(node.args.args)
            if args and args[0].arg == "self":
                args = args[1:]
            params = [a.arg for a in args] + [a.arg for a in node.args.kwonlyargs]
            if node.args.vararg:
                params.append(node.args.vararg.arg)
            if node.args.kwarg:
                params.append(node.args.kwarg.arg)

            positional_defaults = [None] * (len(args) - len(node.args.defaults)) + list(node.args.defaults)
            required = [arg.arg for arg, default in zip(args, positional_defaults) if default is None]
            required.extend(
                arg.arg for arg, default in zip(node.args.kwonlyargs, node.args.kw_defaults)
                if default is None
            )

            methods[node.name] = Method(
                name=node.name,
                required_params=tuple(required),
                params=tuple(params),
            )
    return methods


def split_params(params_text: str) -> list[str]:
    params: list[str] = []
    current = []
    quote = ''
    depth = 0
    for char in params_text:
        if quote:
            current.append(char)
            if char == quote:
                quote = ''
            continue
        if char in "'\"":
            quote = char
            current.append(char)
        elif char in "([{":
            depth += 1
            current.append(char)
        elif char in ")]}" and depth > 0:
            depth -= 1
            current.append(char)
        elif char == ',' and depth == 0:
            params.append(''.join(current).strip())
            current = []
        else:
            current.append(char)
    if current:
        params.append(''.join(current).strip())
    return [p for p in params if p]


def get_doc_headings(doc_file: Path, plugin: str) -> dict[str, tuple[int, str, tuple[str, ...]]]:
    if not doc_file.exists():
        return {}
    headings: dict[str, tuple[int, str, tuple[str, ...]]] = {}
    pattern = re.compile(rf"^##\s+{re.escape(plugin)}\.(\w+)(?:\(([^)]*)\))?:?\s*$")
    for line_no, line in enumerate(doc_file.read_text().splitlines(), 1):
        match = pattern.match(line)
        if not match:
            continue
        name = match.group(1)
        params_text = match.group(2) or ""
        params = []
        for raw_param in split_params(params_text):
            param = raw_param.split("=", 1)[0].strip().lstrip("*")
            if param:
                params.append(param)
        headings[name] = (line_no, line, tuple(params))
    return headings


def main() -> int:
    errors: list[str] = []
    for plugin_file in sorted(PLUGIN_DIR.glob("*.py")):
        if plugin_file.name in IGNORED_PLUGIN_FILES:
            continue
        plugin = plugin_file.stem
        methods = get_methods(plugin_file)
        headings = get_doc_headings(DOC_DIR / f"{plugin}.md", plugin)

        for name, method in methods.items():
            if name not in headings:
                errors.append(f"{plugin}: missing docs for {plugin}.{name}")
                continue
            line_no, _line, documented_params = headings[name]
            unknown = sorted(set(documented_params) - set(method.params))
            missing_required = sorted(set(method.required_params) - set(documented_params))
            if unknown:
                errors.append(
                    f"{plugin}.md:{line_no}: {plugin}.{name} documents unknown params: {', '.join(unknown)}"
                )
            if missing_required:
                errors.append(
                    f"{plugin}.md:{line_no}: {plugin}.{name} missing required params: "
                    f"{', '.join(missing_required)}"
                )

        for name, (line_no, _line, _params) in headings.items():
            if name not in methods:
                errors.append(f"{plugin}.md:{line_no}: stale docs for missing method {plugin}.{name}")

        current_order = list(headings)
        sorted_order = sorted(current_order)
        if current_order != sorted_order:
            errors.append(
                f"{plugin}.md: plugin headings are not alphabetical: "
                f"current={current_order}, expected={sorted_order}"
            )

    if errors:
        print("Documentation check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Plugin documentation check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
