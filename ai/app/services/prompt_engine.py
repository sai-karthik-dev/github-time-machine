"""
Jinja2-based prompt template engine.
Loads .j2 files from app/prompts/ and renders them with context variables.
"""

from __future__ import annotations

import os
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

_PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


class PromptEngine:
    """Load and render Jinja2 prompt templates."""

    def __init__(self, prompts_dir: Path | str | None = None):
        self._dir = Path(prompts_dir) if prompts_dir else _PROMPTS_DIR
        self._env = Environment(
            loader=FileSystemLoader(str(self._dir)),
            autoescape=select_autoescape(default=False),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render(self, template_name: str, **context) -> str:
        """
        Render a prompt template with the given context variables.

        Args:
            template_name: Filename in the prompts/ directory (e.g. "architecture_explain.j2")
            **context: Variables to inject into the template

        Returns:
            Rendered prompt string
        """
        template = self._env.get_template(template_name)
        return template.render(**context)

    def list_templates(self) -> list[str]:
        """Return all available template names."""
        return self._env.list_templates(extensions=["j2"])
