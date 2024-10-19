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
from collections import defaultdict
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

HEADING_RE = re.compile(r"<h([2-6])>(.+?)</h\1>")
def _make_heading_linkable(match: re.Match, used_headings: defaultdict[str, int]) -> str:
    level, text = match.groups()
    slug = _slugify(text)

    used_count = used_headings[slug]
    if used_count:
        slug += f"_{used_count + 1}"
    used_headings[slug] += 1

    return (f'<h{level} id="{slug}">'
            f'{text}'
            f'<span class="permalink"> <a href="#{slug}">🔗</a></span>'
            f'</h{level}>')

def _handle_tag(match: re.Match, locals: dict[str]) -> str:
    body = textwrap.dedent(match.group(2).strip("\n"))
    match match.group(1):
        case "comment":
            return ""
        case "include":
            is_ct_template = body.endswith(".ct")
            with open(body) as file:
                body = file.read()
            if is_ct_template:
                body = parse(body, locals)
            return body
        case "markdown":
            body = commonmark.commonmark(body)

            def heading_re_callback(match: re.Match) -> str:
                return _make_heading_linkable(match, locals["ct_used_heading_slugs"])
            return HEADING_RE.sub(heading_re_callback, body)
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
    new_locals = {
        "ct_used_heading_slugs": defaultdict(int),
    }
    if locals is not None:
        new_locals.update(locals)

    return CUSTOM_TAG_RE.sub(lambda match: _handle_tag(match, new_locals), s)
