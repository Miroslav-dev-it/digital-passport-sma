"""Plugin management for post-processing generated code."""
from __future__ import annotations

from collections.abc import Iterable
from typing import Mapping

from domain.ports import PluginPort


class PluginManager:
    """Select and execute plugins based on request."""

    def __init__(self, plugins: Iterable[PluginPort]) -> None:
        self._registry: Mapping[str, PluginPort] = {plugin.name: plugin for plugin in plugins}

    def resolve(self, requested: Iterable[str]) -> list[PluginPort]:
        """Return plugin instances based on requested names (all if empty)."""
        requested_list = list(requested)
        if not requested_list:
            return list(self._registry.values())
        resolved: list[PluginPort] = []
        for name in requested_list:
            plugin = self._registry.get(name)
            if plugin:
                resolved.append(plugin)
        return resolved


class TrimTrailingSpaces:
    """Strip trailing whitespace from every line."""

    name = "trim_trailing_spaces"

    async def run(self, code: str, language: str) -> str:  # noqa: D401
        return "\n".join(line.rstrip() for line in code.splitlines())


class PythonBlackFormat:
    """Format python code with Black if available."""

    name = "python_black"

    async def run(self, code: str, language: str) -> str:  # noqa: D401
        if language != "python":
            return code
        import asyncio
        import os
        import subprocess
        import tempfile

        with tempfile.NamedTemporaryFile("w+", suffix=".py", delete=False) as handle:
            handle.write(code)
            handle.flush()
            path = handle.name
        try:
            process = await asyncio.create_subprocess_exec("black", "--quiet", path)
            await process.wait()
            with open(path, "r", encoding="utf-8") as result_file:
                return result_file.read()
        except FileNotFoundError:
            return code
        finally:
            try:
                os.remove(path)
            except OSError:
                pass
