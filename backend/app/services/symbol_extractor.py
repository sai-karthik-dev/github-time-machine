import logging

from tree_sitter import Language, Node, Parser

logger = logging.getLogger(__name__)

try:
    import tree_sitter_python as tspython
    PY_LANG = Language(tspython.language())
except ImportError:
    PY_LANG = None

try:
    import tree_sitter_javascript as tsjs
    JS_LANG = Language(tsjs.language())
except ImportError:
    JS_LANG = None

_JS_FAMILY = ("javascript", "typescript", "typescriptreact", "javascriptreact")


class SymbolExtractor:
    """Parses source files with tree-sitter to extract functions, classes, and imports.

    Each returned symbol dict has a "type" of "function", "class", or "import" so
    callers can route them to the right table (functions vs. import edges).
    """

    def parse_file(self, file_path: str, language: str) -> list[dict]:
        lang = self._get_lang(language)
        if lang is None:
            return []

        try:
            with open(file_path, "rb") as fh:
                source = fh.read()
        except Exception:
            return []

        parser = Parser(lang)
        root = parser.parse(source).root_node

        result = []
        result.extend(self._extract_functions(root, language))
        result.extend(self._extract_classes(root, language))
        result.extend(self._extract_imports(root, language))
        return result

    def _get_lang(self, language: str):
        if language == "python" and PY_LANG is not None:
            return PY_LANG
        if language in _JS_FAMILY and JS_LANG is not None:
            return JS_LANG
        return None

    def _extract_functions(self, root: Node, language: str) -> list[dict]:
        results = []
        try:
            if language == "python":
                query = PY_LANG.query(
                    "(function_definition name: (identifier) @func_name body: (block) @func_body) "
                    + "(decorated_definition definition: (function_definition name: (identifier) @func_name))"
                )
            elif language in _JS_FAMILY:
                query = JS_LANG.query(
                    "(function_declaration name: (identifier) @func_name body: (_) @func_body) "
                    + "(method_definition name: (property_identifier) @func_name body: (_) @func_body) "
                    + "(arrow_function) @arrow"
                )
            else:
                return results

            seen = set()
            for node, tag in query.captures(root):
                if tag == "func_name" and node.type == "identifier":
                    name = node.text.decode("utf-8", errors="replace")
                    func_node = node.parent
                    start_line = func_node.start_point[0] + 1
                    end_line = func_node.end_point[0] + 1
                    key = f"{name}:{start_line}:{end_line}"
                    if key not in seen:
                        seen.add(key)
                        results.append({
                            "name": name,
                            "type": "function",
                            "start_line": start_line,
                            "end_line": end_line,
                            "is_exported": False,
                        })
        except Exception as e:
            logger.debug(f"Function extraction failed: {e}")

        return results

    def _extract_classes(self, root: Node, language: str) -> list[dict]:
        results = []
        try:
            if language == "python":
                query = PY_LANG.query("(class_definition name: (identifier) @class_name)")
            elif language in _JS_FAMILY:
                query = JS_LANG.query("(class_declaration name: (identifier) @class_name)")
            else:
                return results

            for node, tag in query.captures(root):
                if tag == "class_name" and node.type == "identifier":
                    name = node.text.decode("utf-8", errors="replace")
                    class_node = node.parent
                    results.append({
                        "name": name,
                        "type": "class",
                        "start_line": class_node.start_point[0] + 1,
                        "end_line": class_node.end_point[0] + 1,
                        "is_exported": False,
                    })
        except Exception as e:
            logger.debug(f"Class extraction failed: {e}")

        return results

    def _extract_imports(self, root: Node, language: str) -> list[dict]:
        results = []
        try:
            if language == "python":
                query = PY_LANG.query(
                    "(import_statement name: (dotted_name) @import_name) "
                    + "(import_from_statement module_name: (dotted_name) @import_name)"
                )
            elif language in _JS_FAMILY:
                query = JS_LANG.query(
                    "(import_statement source: (string) @import_source) "
                    + "(import_statement specifier: (import_specifier name: (identifier) @import_name))"
                )
            else:
                return results

            for node, tag in query.captures(root):
                name = node.text.decode("utf-8", errors="replace").strip("\"'")
                results.append({
                    "name": name,
                    "type": "import",
                    "start_line": node.start_point[0] + 1,
                    "end_line": node.end_point[0] + 1,
                    "is_exported": False,
                })
        except Exception as e:
            logger.debug(f"Import extraction failed: {e}")

        return results