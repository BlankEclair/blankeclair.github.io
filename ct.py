"""
# Claire's Templater
A custom, primitive templating engine that only depends on the commonmark
library.

Note: This is not meant for untrusted input! It is quite literally designed to
let templates run arbitrary code, so please use it only on trusted input.

## Why?
...
I'm... not sure?

## Usage
1. Have https://pypi.org/project/commonmark installed
2. `import ct`
3. `ct.parse(str)`
"""

import re
import ast
import html # Not needed, but helpful for <c:python>
import textwrap
import commonmark

# 100% proper parser, don't @ me
CUSTOM_TAG_RE = re.compile(r"<c:(\w+)>([\s\S]+?)</c:\1>")

SPECIAL_CHARACTERS_RE = re.compile(r"\W")
CONSECUTIVE_UNDERSCORES_RE = re.compile(r"_{2,}")
def _slugify(s: str) -> str:
    s = s.lower()
    s = SPECIAL_CHARACTERS_RE.sub("_", s)
    s = CONSECUTIVE_UNDERSCORES_RE.sub("_", s)
    return s.strip("_")

HEADING_RE = re.compile(r"<h([1-6])>(.+?)</h\1>")
def _make_heading_linkable(match: re.Match) -> str:
    level, text = match.groups()
    slug = _slugify(text)

    return (f'<h{level} id="{slug}">'
            f'{text}'
            f'<span class="permalink"> <a href="#{slug}">🔗</a></span>'
            f'</h{level}>')

def _handle_tag(match: re.Match, locals: dict[str]) -> str:
    body = match.group(2)
    match match.group(1):
        case "comment":
            return ""
        case "include":
            with open(body) as file:
                body = file.read()
            return parse(body, locals)
        case "markdown":
            body = textwrap.dedent(body.strip("\n"))
            body = commonmark.commonmark(body)
            return HEADING_RE.sub(_make_heading_linkable, body)
        case "python":
            # https://greentreesnakes.readthedocs.io/
            tree = ast.parse(body)

            arguments = ast.arguments([], [], None, [], [], None, [])
            func = ast.FunctionDef("_ct_inline_function", arguments, tree.body, [], None, None)
            ast.fix_missing_locations(func)

            module = ast.parse("")
            module.body = [func]
            exec(compile(module, "<inline>", "exec"), globals(), locals)
            return str(locals["_ct_inline_function"]())
        case _:
            raise ValueError(f'Unknown tag "c:{match.group(1)}"')

def parse(s: str, locals: dict[str] | None = None) -> str:
    locals = locals if locals is not None else {}
    return CUSTOM_TAG_RE.sub(lambda match: _handle_tag(match, locals), s)
