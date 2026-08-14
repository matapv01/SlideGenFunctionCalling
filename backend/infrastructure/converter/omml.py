"""Small LaTeX -> Office Math (OMML) converter for native PowerPoint equations.

PowerPoint stores a modern editable equation inside ``a14:m``.  The equation
itself is OMML (``m:oMath``/``m:oMathPara``), not a PNG.  This module handles
the LaTeX constructs emitted by the slide-generation prompts and deliberately
keeps unknown commands as editable text instead of failing the whole export.
"""

from __future__ import annotations

from dataclasses import dataclass
import re

from lxml import etree


A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
A14_NS = "http://schemas.microsoft.com/office/drawing/2010/main"
M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"


def _tag(namespace: str, name: str) -> str:
    return f"{{{namespace}}}{name}"


def _element(namespace: str, name: str, **attributes: str) -> etree._Element:
    node = etree.Element(_tag(namespace, name))
    for key, value in attributes.items():
        node.set(key, value)
    return node


GREEK = {
    "alpha": "α",
    "beta": "β",
    "gamma": "γ",
    "delta": "δ",
    "epsilon": "ε",
    "varepsilon": "ϵ",
    "zeta": "ζ",
    "eta": "η",
    "theta": "θ",
    "vartheta": "ϑ",
    "iota": "ι",
    "kappa": "κ",
    "lambda": "λ",
    "mu": "μ",
    "nu": "ν",
    "xi": "ξ",
    "pi": "π",
    "varpi": "ϖ",
    "rho": "ρ",
    "sigma": "σ",
    "varsigma": "ς",
    "tau": "τ",
    "upsilon": "υ",
    "phi": "ϕ",
    "varphi": "φ",
    "chi": "χ",
    "psi": "ψ",
    "omega": "ω",
    "Gamma": "Γ",
    "Delta": "Δ",
    "Theta": "Θ",
    "Lambda": "Λ",
    "Xi": "Ξ",
    "Pi": "Π",
    "Sigma": "Σ",
    "Upsilon": "Υ",
    "Phi": "Φ",
    "Psi": "Ψ",
    "Omega": "Ω",
}

SYMBOLS = {
    "pm": "±",
    "mp": "∓",
    "times": "×",
    "cdot": "·",
    "ast": "∗",
    "le": "≤",
    "leq": "≤",
    "ge": "≥",
    "geq": "≥",
    "neq": "≠",
    "ne": "≠",
    "approx": "≈",
    "equiv": "≡",
    "sim": "∼",
    "in": "∈",
    "notin": "∉",
    "subset": "⊂",
    "subseteq": "⊆",
    "supset": "⊃",
    "supseteq": "⊇",
    "to": "→",
    "rightarrow": "→",
    "leftarrow": "←",
    "leftrightarrow": "↔",
    "infty": "∞",
    "partial": "∂",
    "nabla": "∇",
    "forall": "∀",
    "exists": "∃",
    "emptyset": "∅",
    "land": "∧",
    "lor": "∨",
    "mid": "|",
    "cap": "∩",
    "cup": "∪",
    "oplus": "⊕",
    "otimes": "⊗",
}

FUNCTIONS = {
    "log",
    "ln",
    "lg",
    "sin",
    "cos",
    "tan",
    "cot",
    "sec",
    "csc",
    "sinh",
    "cosh",
    "tanh",
    "lim",
    "max",
    "min",
}

NARY_SYMBOLS = {
    "sum": "∑",
    "prod": "∏",
    "coprod": "∐",
    "int": "∫",
    "iint": "∬",
    "iiint": "∭",
    "oint": "∮",
}


def _append_text(parent: etree._Element, text: str, *, color: str, size: str) -> None:
    """Append an OMML run using DrawingML run properties."""
    if text == "":
        return
    run = _element(M_NS, "r")
    run_properties = _element(A_NS, "rPr", sz=size)
    run_properties.append(_element(A_NS, "latin", typeface="Cambria Math"))
    if color:
        solid_fill = _element(A_NS, "solidFill")
        solid_fill.append(_element(A_NS, "srgbClr", val=color.lstrip("#").upper()))
        run_properties.append(solid_fill)
    run.append(run_properties)
    text_node = _element(M_NS, "t")
    text_node.text = text
    run.append(text_node)
    parent.append(run)


def _run_node(text: str, *, color: str, size: str) -> etree._Element:
    run = _element(M_NS, "r")
    if text:
        _append_text(run, text, color=color, size=size)
        return run[0]
    run_properties = _element(A_NS, "rPr", sz=size)
    run_properties.append(_element(A_NS, "latin", typeface="Cambria Math"))
    run.append(run_properties)
    run.append(_element(M_NS, "t"))
    return run


def _argument(parent: etree._Element, children: list[etree._Element]) -> None:
    argument = _element(M_NS, "e")
    for child in children:
        argument.append(child)
    parent.append(argument)


def _group(children: list[etree._Element]) -> etree._Element:
    group = _element(M_NS, "e")
    for child in children:
        group.append(child)
    return group


@dataclass
class _Parser:
    source: str
    color: str
    size: str
    position: int = 0

    def parse(self, stop: str | None = None) -> list[etree._Element]:
        nodes: list[etree._Element] = []
        while self.position < len(self.source):
            char = self.source[self.position]
            if stop is not None and char == stop:
                self.position += 1
                break
            if char == "\\":
                node = self._command()
            elif char in "^_":
                self.position += 1
                if nodes:
                    script = self._script_argument()
                    nodes[-1] = self._attach_script(nodes[-1], char, script)
                continue
            elif char == "{":
                self.position += 1
                nodes.extend(self.parse("}"))
                continue
            elif char == "}":
                if stop is None:
                    self.position += 1
                    continue
                break
            elif char.isspace():
                self.position += 1
                # OMML lays out operators and identifiers itself. Source
                # whitespace is therefore not needed for the visual result.
                continue
            else:
                self.position += 1
                node = self._run(char)

            if node is not None:
                nodes.append(node)
        return nodes

    def _command(self) -> etree._Element | None:
        self.position += 1
        if self.position >= len(self.source):
            return None

        if not self.source[self.position].isalpha():
            char = self.source[self.position]
            self.position += 1
            if char in {",", "!", ";", ":", " "}:
                return None
            return self._run({"{": "{", "}": "}", "\\": "\\"}.get(char, char))

        start = self.position
        while self.position < len(self.source) and self.source[self.position].isalpha():
            self.position += 1
        command = self.source[start:self.position]

        if command in {"frac", "dfrac", "tfrac"}:
            numerator = self._required_group()
            denominator = self._required_group()
            fraction = _element(M_NS, "f")
            _argument(fraction, numerator)
            _argument(fraction, denominator)
            return fraction

        if command == "sqrt":
            # Optional root index is represented as the degree. It is rarely
            # emitted by the slide prompt, but supporting it costs little.
            degree: list[etree._Element] = []
            self._skip_spaces()
            if self.position < len(self.source) and self.source[self.position] == "[":
                self.position += 1
                raw_start = self.position
                while self.position < len(self.source) and self.source[self.position] != "]":
                    self.position += 1
                degree = _Parser(
                    self.source[raw_start:self.position],
                    self.color,
                    self.size,
                ).parse()
                if self.position < len(self.source):
                    self.position += 1
            radical = _element(M_NS, "rad")
            if degree:
                _argument(radical, degree)
            _argument(radical, self._required_group())
            return radical

        if command in {"hat", "widehat", "bar", "overline", "vec", "tilde", "dot", "ddot"}:
            accent = {
                "hat": "^",
                "widehat": "^",
                "bar": "¯",
                "overline": "¯",
                "vec": "→",
                "tilde": "~",
                "dot": "˙",
                "ddot": "¨",
            }[command]
            acc = _element(M_NS, "acc")
            acc_pr = _element(M_NS, "accPr")
            acc_pr.append(_element(M_NS, "chr", val=accent))
            acc.append(acc_pr)
            _argument(acc, self._required_group_or_atom())
            return acc

        if command in {"mathcal", "mathscr", "mathrm", "mathbf", "mathit", "text", "operatorname"}:
            value = self._required_group_text()
            if command in {"mathcal", "mathscr"}:
                value = "".join(_MATHCAL.get(char, char) for char in value)
            return self._run(value)

        if command == "left" or command == "right":
            self._skip_spaces()
            if self.position < len(self.source):
                delimiter = self.source[self.position]
                self.position += 1
                return self._run(delimiter if delimiter != "." else "")
            return None

        if command == "begin":
            environment = self._required_group_text()
            if environment in {"matrix", "pmatrix", "bmatrix", "Bmatrix", "vmatrix", "Vmatrix"}:
                return self._matrix(environment)
            return self._run(environment)

        if command in GREEK:
            return self._run(GREEK[command])
        if command in SYMBOLS:
            return self._run(SYMBOLS[command])
        if command in NARY_SYMBOLS:
            nary = _element(M_NS, "nary")
            nary_pr = _element(M_NS, "naryPr")
            nary_pr.append(_element(M_NS, "chr", val=NARY_SYMBOLS[command]))
            nary.append(nary_pr)
            nary.append(_element(M_NS, "e"))
            return nary
        if command in FUNCTIONS:
            return self._run(command)

        # Keep unknown commands editable and visible. For example, a command
        # not in the table becomes ``custom`` instead of disappearing.
        return self._run(command)

    def _run(self, text: str) -> etree._Element:
        return _run_node(text, color=self.color, size=self.size)

    def _skip_spaces(self) -> None:
        while self.position < len(self.source) and self.source[self.position].isspace():
            self.position += 1

    def _required_group(self) -> list[etree._Element]:
        self._skip_spaces()
        if self.position >= len(self.source):
            return []
        if self.source[self.position] == "{":
            self.position += 1
            return self.parse("}")
        node = self._command() if self.source[self.position] == "\\" else self.parse_atom()
        return [node] if node is not None else []

    def _required_group_or_atom(self) -> list[etree._Element]:
        return self._required_group()

    def _required_group_text(self) -> str:
        self._skip_spaces()
        if self.position >= len(self.source):
            return ""
        if self.source[self.position] != "{":
            node = self.parse_atom()
            return "" if node is None else "".join(node.itertext())
        self.position += 1
        start = self.position
        depth = 1
        while self.position < len(self.source) and depth:
            if self.source[self.position] == "{":
                depth += 1
            elif self.source[self.position] == "}":
                depth -= 1
            self.position += 1
        return self.source[start:self.position - 1]

    def parse_atom(self) -> etree._Element | None:
        if self.position >= len(self.source):
            return None
        char = self.source[self.position]
        self.position += 1
        return self._run(char)

    def _script_argument(self) -> list[etree._Element]:
        self._skip_spaces()
        if self.position < len(self.source) and self.source[self.position] == "{":
            self.position += 1
            return self.parse("}")
        node = self._command() if self.position < len(self.source) and self.source[self.position] == "\\" else self.parse_atom()
        return [node] if node is not None else []

    def _attach_script(
        self,
        base: etree._Element,
        marker: str,
        script: list[etree._Element],
    ) -> etree._Element:
        if base.tag == _tag(M_NS, "nary"):
            child_name = "sub" if marker == "_" else "sup"
            child = _element(M_NS, child_name)
            for node in script:
                child.append(node)
            # naryPr, sub, sup, e is the order required by OMML. Rebuild the
            # tail so both ``_{...}^{...}`` and ``^{...}_{...}`` are valid.
            existing_scripts = {
                existing.tag.rsplit("}", 1)[-1]: existing
                for existing in base
                if existing.tag in {
                    _tag(M_NS, "sub"),
                    _tag(M_NS, "sup"),
                }
            }
            existing_scripts[child_name] = child
            nary_properties = next(
                existing
                for existing in base
                if existing.tag == _tag(M_NS, "naryPr")
            )
            degree = next(
                existing
                for existing in base
                if existing.tag == _tag(M_NS, "e")
            )
            base.clear()
            base.append(nary_properties)
            for script_name in ("sub", "sup"):
                if script_name in existing_scripts:
                    base.append(existing_scripts[script_name])
            base.append(degree)
            return base

        if marker == "_":
            tag = "sSub"
            script_tag = "sub"
        else:
            tag = "sSup"
            script_tag = "sup"
        # If the base already has the other script, combine both into sSubSup.
        if base.tag in {_tag(M_NS, "sSub"), _tag(M_NS, "sSup")}:
            existing_tag = "sub" if base.tag == _tag(M_NS, "sSub") else "sup"
            combined = _element(M_NS, "sSubSup")
            for child in base:
                if child.tag == _tag(M_NS, existing_tag):
                    continue
                combined.append(child)
            if existing_tag == "sub":
                combined.append(next(child for child in base if child.tag == _tag(M_NS, "sub")))
                new_script = _element(M_NS, "sup")
            else:
                new_script = _element(M_NS, "sub")
                combined.append(new_script)
                combined.append(next(child for child in base if child.tag == _tag(M_NS, "sup")))
            for node in script:
                new_script.append(node)
            return combined

        scripted = _element(M_NS, tag)
        scripted.append(_element(M_NS, "e"))
        script_node = _element(M_NS, script_tag)
        for node in script:
            script_node.append(node)
        scripted.append(script_node)
        # A base is always the first child of sSub/sSup.
        scripted[0].append(base)
        return scripted

    def _matrix(self, environment: str) -> etree._Element:
        closing = "\\end{" + environment + "}"
        end = self.source.find(closing, self.position)
        if end < 0:
            raw = self.source[self.position:]
            self.position = len(self.source)
        else:
            raw = self.source[self.position:end]
            self.position = end + len(closing)

        matrix = _element(M_NS, "m")
        for raw_row in re.split(r"\\\\", raw):
            row = _element(M_NS, "mr")
            for raw_cell in raw_row.split("&"):
                cell = _element(M_NS, "e")
                cell_parser = _Parser(raw_cell.strip(), self.color, self.size)
                for child in cell_parser.parse():
                    cell.append(child)
                row.append(cell)
            matrix.append(row)
        return matrix


_MATHCAL = {
    "A": "𝒜", "B": "ℬ", "C": "𝒞", "D": "𝒟", "E": "ℰ", "F": "ℱ",
    "G": "𝒢", "H": "ℋ", "I": "ℐ", "J": "𝒥", "K": "𝒦", "L": "ℒ",
    "M": "ℳ", "N": "𝒩", "O": "𝒪", "P": "𝒫", "Q": "𝒬", "R": "ℛ",
    "S": "𝒮", "T": "𝒯", "U": "𝒰", "V": "𝒱", "W": "𝒲", "X": "𝒳",
    "Y": "𝒴", "Z": "𝒵",
}


def latex_to_omml(
    latex: str,
    *,
    color: str = "#000000",
    size_pt: float = 24.0,
    paragraph: bool = True,
) -> etree._Element | None:
    """Return an ``a14:m`` element containing an editable OMML equation."""
    source = str(latex or "").strip()
    if not source:
        return None

    parser = _Parser(
        source=source,
        color=color,
        size=str(max(1, round(float(size_pt) * 100))),
    )
    nodes = parser.parse()
    if not nodes:
        return None

    math = _element(M_NS, "oMath")
    for node in nodes:
        math.append(node)

    wrapper = etree.Element(
        _tag(A14_NS, "m"),
        nsmap={"a14": A14_NS, "a": A_NS, "m": M_NS},
    )
    if paragraph:
        math_para = _element(M_NS, "oMathPara")
        math_para.append(math)
        wrapper.append(math_para)
    else:
        wrapper.append(math)
    return wrapper


def omml_has_math(node: etree._Element | None) -> bool:
    return node is not None and node.find(f".//{_tag(M_NS, 'oMath')}") is not None
