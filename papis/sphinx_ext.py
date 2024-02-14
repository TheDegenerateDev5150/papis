import os
import sys
import docutils
from typing import Any, Callable, Dict, List, Optional

from sphinx import application
from sphinx_click.ext import ClickDirective
from docutils.parsers.rst import Directive


class CustomClickDirective(ClickDirective):     # type: ignore[misc]
    def run(self) -> Any:
        sections = super().run()

        # NOTE: just remove the title section so we can add our own
        return sections[0].children[1:]


class PapisConfig(Directive):
    has_content: bool = True
    optional_arguments: int = 3
    required_arguments: int = 1
    option_spec: Dict[str, type] = {"default": str, "section": str, "description": str}
    add_index: int = True

    def run(self) -> Any:
        from papis.config import get_general_settings_name, get_default_settings

        default_settings = get_default_settings()
        key = self.arguments[0]

        section = self.options.get("section", get_general_settings_name())
        default = self.options.get(
            "default",
            default_settings.get(section, {}).get(key, "<missing>"))

        lines = []
        lines.append("")
        lines.append(".. _config-{section}-{key}:".format(section=section, key=key))
        lines.append("")
        lines.append("`{key} <#config-{section}-{key}>`__"
                     .format(section=section, key=key))

        if "\n" in str(default):
            lines.append("    - **Default**: ")
            lines.append("        .. code::")
            lines.append("")
            for lindef in default.split("\n"):
                lines.append(3 * "    " + lindef)
        else:
            lines.append("    - **Default**: ``{value!r}``"
                         .format(value=default))
        lines.append("")

        view = docutils.statemachine.ViewList(lines)
        self.content = view + self.content  # type: ignore[has-type]

        node = docutils.nodes.paragraph()
        node.document = self.state.document
        self.state.nested_parse(self.content, self.content_offset, node)

        return node.children


def make_link_resolve(
        github_project_url: str,
        revision: str) -> Callable[[str, Dict[str, Any]], Optional[str]]:
    def linkcode_resolve(domain: str, info: Dict[str, Any]) -> Optional[str]:
        url = None
        if domain != "py" or not info["module"]:
            return url

        modname = info["module"]
        objname = info["fullname"]

        mod = sys.modules.get(modname)
        if not mod:
            return url

        obj = mod
        for part in objname.split("."):
            try:
                obj = getattr(obj, part)
            except Exception:
                return url

        import inspect

        try:
            filepath = "{}.py".format(os.path.join(*obj.__module__.split(".")))
        except Exception:
            return url

        if filepath is None:
            return url

        try:
            source, lineno = inspect.getsourcelines(obj)
        except Exception:
            return url
        else:
            linestart, linestop = lineno, lineno + len(source) - 1

        return (
            "{}/blob/{}/{}#L{}-L{}"
            .format(github_project_url, revision, filepath, linestart, linestop)
        )

    return linkcode_resolve


def remove_module_docstring(app: application.Sphinx,
                            what: str,
                            name: str,
                            obj: object,
                            options: Any,
                            lines: List[str]) -> None:
    # NOTE: this is used to remove the module documentation for commands so that
    # we can show the module members in the `Developer API Reference` section
    # without the tutorial / examples parts.
    if what == "module" and ".commands." in name and options.get("members"):
        del lines[:]


def setup(app: application.Sphinx) -> Dict[str, Any]:
    app.setup_extension("sphinx.ext.linkcode")
    app.setup_extension("sphinx_click.ext")

    app.add_directive("click", CustomClickDirective, override=True)
    app.add_directive("papis-config", PapisConfig)

    app.connect("autodoc-process-docstring", remove_module_docstring)

    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
