#!/usr/bin/env python3
"""
LP Tuning house rule: NEVER use em dashes (or spaced en dashes) in anything published.
Usage:
    python scripts/clean_dashes.py file1.html file2.html ...   (rewrites in place)
    from clean_dashes import clean_dashes                      (use on any generated text)
Ranges such as 8-11% written with an unspaced en dash are left alone.
"""
import re, sys

EM = "—"
EN = "–"
NEW_SENTENCE = ("We", "It", "You", "Our", "The", "This", "That", "They", "There", "If", "No",
                "Not", "Every", "Your", "Each", "Most", "Many", "Some", "Call", "Get",
                "Contact", "Speak", "Tell", "Ask", "Book", "Its", "These", "Those", "Just")


def _dash_sub(text, first):
    """Replace spaced dashes in a run of text. `first` is the separator for the first dash
    (used in titles/headings), later dashes become commas or a full stop."""
    state = {"n": 0}

    def repl(m):
        raw = m.group(0)
        before = text[max(0, m.start() - 3):m.start()]
        after = text[m.end():m.end() + 25]
        # an unspaced en dash is a numeric range such as 8-11%: leave it alone
        if EN in raw and raw == EN:
            return raw
        # a spaced en dash between numbers is a range
        if EN in raw and re.search(r"\d$", before) and re.match(r"\d", after):
            return " to "
        state["n"] += 1
        word = re.match(r"[A-Za-z']+", after)
        word = word.group(0) if word else ""
        if state["n"] == 1 and first:
            return first
        if word in NEW_SENTENCE:
            return ". "
        return ", "

    return re.sub(r"\s*[\u2014\u2013]\s*(?=\S)", repl, text)


def clean_dashes(s: str) -> str:
    # entities to literal
    s = re.sub(r"&mdash;|&#8212;|&#x2014;|&ndash;(?=\s)", EM, s)
    # label patterns: "<strong>X</strong> - y", "<li>X - y", "<td>X - y"
    s = re.sub(r"(</strong>)\s*" + EM + r"\s*", r"\1: ", s)
    s = re.sub(r"(<(?:li|dt)[^>]*>)([^<" + EM + r"]{1,60}?)\s*" + EM + r"\s*", r"\1\2: ", s)
    # quoted brand strings: "LP Tuning - New Quote Request", "New Enquiry - LP Tuning"
    s = re.sub(r"((?:LP Tuning|LP Diesel Solutions))\s*" + EM + r"\s*", r"\1 | ", s)
    s = re.sub(r"\s*" + EM + r"\s*(LP Tuning)", r" | \1", s)

    # title-like elements: first dash becomes a colon
    def title_like(pattern):
        nonlocal s
        s = re.sub(pattern, lambda m: m.group(1) + _dash_sub(m.group(2), ": ") + m.group(3), s, flags=re.S)

    title_like(r"(<title>)(.*?)(</title>)")
    title_like(r"(<h1[^>]*>)(.*?)(</h1>)")
    title_like(r"(<h3[^>]*>)(.*?)(</h3>)")
    title_like(r'(<meta property="og:title" content=")([^"]*)(")')
    title_like(r'("headline": ")([^"]*)(")')
    title_like(r'("name": ")([^"]*)(")')

    # paired dashes around a short aside that contains commas: use brackets
    s = re.sub(r"(\S)\s+\u2014\s+([^\u2014<>.!?]{3,100}?,[^\u2014<>.!?]{1,100}?)\s+\u2014\s+", r"\1 (\2) ", s)
    # a single dash introducing a list (two or more commas before the sentence ends): colon
    s = re.sub(r"\s+\u2014\s+(?=[^\u2014<>.!?]*,[^\u2014<>.!?]*,)", ": ", s)

    # everything else: process text outside tags, descriptions and JSON strings by simple pass
    s = _dash_sub(s, None)
    # unspaced em dashes
    s = s.replace(EM, ", ")
    # tidy: only touch artefacts our own replacements can create (never CSS or JS punctuation)
    s = re.sub(r",( ,)+", ",", s)
    s = re.sub(r"[ \t]+,(?= )", ",", s)
    return s


if __name__ == "__main__":
    for path in sys.argv[1:]:
        with open(path, encoding="utf-8") as fh:
            old = fh.read()
        new = clean_dashes(old)
        if new != old:
            with open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(new)
            print("cleaned", path)
