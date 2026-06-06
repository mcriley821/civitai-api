"""Sphinx configuration for py-civitai-api docs."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath("../../src"))

project = "py-civitai-api"
author = "mcriley821"
release = "0.0.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "myst_parser",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "furo"
html_extra_path = ["openapi.yaml"]

myst_enable_extensions = ["colon_fence"]

autodoc_typehints = "description"
autodoc_member_order = "bysource"
autodoc_default_options = {
    "members": True,
    "show-inheritance": True,
    "undoc-members": False,
}

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pydantic": ("https://docs.pydantic.dev/latest/", None),
}

# Suppress ambiguous cross-reference warnings from autodoc (duplicate field names
# across Pydantic models, and two Creator classes in types.model / types.creator).
suppress_warnings = ["ref.python"]


def _openapi_full_page(app, pagename, templatename, context, doctree):  # noqa: ANN001, ANN201
    if pagename == "openapi":
        return "openapi_full.html"
    return None


def setup(app):  # noqa: ANN001, ANN201
    app.connect("html-page-context", _openapi_full_page)
