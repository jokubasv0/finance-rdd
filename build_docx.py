"""Build a Word document from out/paper.md, embedding the figures."""

import re
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

OUT = Path(__file__).resolve().parent / "out"
SRC = OUT / "paper.md"
DST = OUT / "Pricing_Regime_Change.docx"

INLINE = re.compile(r"(\*\*.+?\*\*|\*[^*]+?\*|\$(?![0-9])[^$\n]{1,60}\$)")
# Inline maths in prose: y_it, alpha_i, t_cut. Short tokens only, and never
# followed by another word character, so image filenames such as
# fig1_levels.png are left alone.
SUB = re.compile(r"_([A-Za-z0-9]{1,4})(?![A-Za-z0-9])")


def add_text(par, chunk):
    """Add plain text, turning _tokens into real subscripts."""
    pos = 0
    for m in SUB.finditer(chunk):
        if m.start() > pos:
            par.add_run(chunk[pos:m.start()])
        par.add_run(m.group(1)).font.subscript = True
        pos = m.end()
    if pos < len(chunk):
        par.add_run(chunk[pos:])


def add_runs(par, text):
    """Split a line into normal / bold / italic runs."""
    text = text.replace("\\", "")
    for chunk in INLINE.split(text):
        if not chunk:
            continue
        if chunk.startswith("**") and chunk.endswith("**"):
            par.add_run(chunk[2:-2]).bold = True
        elif chunk.startswith("$") and chunk.endswith("$") and not chunk[1].isdigit():
            add_math_runs(par, chunk[1:-1])
        elif chunk.startswith("*") and chunk.endswith("*"):
            par.add_run(chunk[1:-1]).italic = True
        else:
            add_text(par, chunk)


def add_math_runs(par, text):
    """Render a plain-text formula, turning _x into real subscripts."""
    buf = ""
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == "_":
            if buf:
                par.add_run(buf).italic = True
                buf = ""
            j = i + 1
            tok = ""
            while j < len(text) and (text[j].isalnum() or text[j] in "+-"):
                tok += text[j]
                j += 1
            if tok:
                r = par.add_run(tok)
                r.italic = True
                r.font.subscript = True
                i = j
                continue
        buf += ch
        i += 1
    if buf:
        par.add_run(buf).italic = True


def build():
    doc = Document()
    st = doc.styles["Normal"]
    st.font.name = "Calibri"
    st.font.size = Pt(11)
    st.paragraph_format.space_after = Pt(8)
    st.paragraph_format.line_spacing = 1.25

    for sec in doc.sections:
        sec.left_margin = sec.right_margin = Cm(2.5)
        sec.top_margin = sec.bottom_margin = Cm(2.2)

    # sober academic palette: near-black headings, not the Word default blue
    from docx.shared import RGBColor
    for name in ("Title", "Heading 1", "Heading 2", "Heading 3", "Heading 4"):
        try:
            style = doc.styles[name]
        except KeyError:
            continue
        style.font.color.rgb = RGBColor(0x1A, 0x1A, 0x1A)
        style.font.name = "Calibri"
    doc.styles["Heading 1"].font.size = Pt(16)
    doc.styles["Heading 2"].font.size = Pt(13)
    doc.styles["Heading 3"].font.size = Pt(11.5)
    doc.styles["Heading 4"].font.size = Pt(11)

    lines = SRC.read_text().splitlines()
    # Join soft-wrapped caption continuations ("**Figure 8.** ... is" / "treated in turn")
    # so a caption is one paragraph, not two centred fragments.
    _joined, _k = [], 0
    while _k < len(lines):
        _ln = lines[_k]
        if _ln.strip().startswith(("**Figure", "**Table")):
            _buf = _ln.rstrip()
            _k += 1
            while _k < len(lines):
                _nx = lines[_k].strip()
                if (not _nx) or _nx.startswith(("**", "|", "!", "#", "$$", ">", "-", "*")):
                    break
                _buf += " " + _nx
                _k += 1
            _joined.append(_buf)
            continue
        _joined.append(_ln)
        _k += 1
    lines = _joined
    i = 0
    while i < len(lines):
        raw = lines[i]
        line = raw.strip()

        # blank
        if not line:
            i += 1
            continue

        # horizontal rule
        if line == "---":
            i += 1
            continue

        # display maths: $$ ... $$
        if line.startswith("$$"):
            buf = line
            while not buf.endswith("$$") or len(buf) < 4:
                i += 1
                buf += " " + lines[i].strip()
            body = buf.strip("$").strip()
            par = doc.add_paragraph()
            par.alignment = WD_ALIGN_PARAGRAPH.CENTER
            par.paragraph_format.space_before = Pt(6)
            par.paragraph_format.space_after = Pt(10)
            add_math_runs(par, body)
            i += 1
            continue
        # image
        m = re.match(r"!\[.*?\]\((.+?)\)", line)
        if m:
            path = OUT / m.group(1)
            if path.exists():
                doc.add_picture(str(path), width=Cm(15.5))
                par = doc.paragraphs[-1]
                par.alignment = WD_ALIGN_PARAGRAPH.CENTER
                # keep the caption on the same page as the picture
                par.paragraph_format.keep_with_next = True
            i += 1
            continue

        # table block
        if line.startswith("|"):
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i].strip())
                i += 1
            rows = [
                [c.strip() for c in r.strip("|").split("|")]
                for r in block
                if not re.fullmatch(r"\|[\s:\-|]+\|", r)
            ]
            if not rows:
                continue
            ncol = max(len(r) for r in rows)
            table = doc.add_table(rows=0, cols=ncol)
            table.style = "Table Grid"
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            for ri, row in enumerate(rows):
                cells = table.add_row().cells
                for ci in range(ncol):
                    txt = row[ci] if ci < len(row) else ""
                    cell = cells[ci]
                    cell.paragraphs[0].text = ""
                    par = cell.paragraphs[0]
                    par.paragraph_format.space_after = Pt(2)
                    par.paragraph_format.space_before = Pt(2)
                    if ci > 0:
                        par.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                    add_runs(par, txt)
                    for run in par.runs:
                        run.font.size = Pt(9.5)
                        if ri == 0:
                            run.bold = True
                # keep the whole table on one page
                if ri < len(rows) - 1:
                    for cell in cells:
                        for cp in cell.paragraphs:
                            cp.paragraph_format.keep_with_next = True
            # fixed layout: wide label column, 2.15 cm for each numeric column
            NUM = 2.15
            if ncol >= 2:
                cw = [max(3.5, 16.0 - NUM * (ncol - 1))] + [NUM] * (ncol - 1)
            else:
                cw = [16.0]
            table.autofit = False
            from docx.oxml import OxmlElement
            from docx.oxml.ns import qn
            layout = OxmlElement("w:tblLayout")
            layout.set(qn("w:type"), "fixed")
            table._tbl.tblPr.append(layout)
            for ci, w in enumerate(cw):
                table.columns[ci].width = Cm(w)
                for row in table.rows:
                    row.cells[ci].width = Cm(w)

            doc.add_paragraph().paragraph_format.space_after = Pt(4)
            continue

        # headings
        if line.startswith("#### "):
            h = doc.add_heading(level=4)
            add_runs(h, line[5:])
        elif line.startswith("### "):
            h = doc.add_heading(level=3)
            add_runs(h, line[4:])
        elif line.startswith("## "):
            h = doc.add_heading(level=2)
            add_runs(h, line[3:])
        elif line.startswith("# "):
            h = doc.add_heading(level=1)
            h.alignment = WD_ALIGN_PARAGRAPH.CENTER
            add_runs(h, line[2:])
        else:
            par = doc.add_paragraph()
            add_runs(par, line)
            # bold-only caption lines get centred
            if line.startswith("**Table") or line.startswith("**Figure"):
                par.alignment = WD_ALIGN_PARAGRAPH.LEFT
                par.paragraph_format.space_before = Pt(10)
                par.paragraph_format.space_after = Pt(4)
                if line.startswith("**Table"):
                    par.paragraph_format.keep_with_next = True
        i += 1

    # Guard: every "$" in the source that is followed by a digit is a currency
    # amount and must survive literally; no other dollar sign should survive.
    want = len(re.findall(r"\$\d", SRC.read_text()))
    got = 0
    for par in doc.paragraphs:
        got += sum(r.text.count("$") for r in par.runs)
    for tbl in doc.tables:
        for row in tbl.rows:
            for cell in row.cells:
                for par in cell.paragraphs:
                    got += sum(r.text.count("$") for r in par.runs)
    assert got == want, f"dollar signs mangled: {got} in output, {want} expected"
    print(f"dollar signs preserved: {got}")

    doc.save(DST)
    words = len(re.findall(r"\b\w+\b", SRC.read_text()))
    print(f"wrote {DST}")
    print(f"source words (incl. tables): {words}")


if __name__ == "__main__":
    build()
