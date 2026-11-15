# First pass — superseded, kept for the record

These are the outputs of the initial analysis, which used Czechia as the sole control and
leaned on a dose-response design. Both choices were wrong and are corrected in `final_analysis.py`:

- **Control.** Czechia was the most generous possible control: Czech yields rose 47 bp over the
  window while Hungary's fell 138 bp, so the Czech-only spread mechanically overstates the
  effect (−185 bp against the −157 bp peer-average headline) and makes the pre/post split look
  like 50/50 when it is really 35/65.
- **Identification.** The daily regression of spread changes on probability changes returns
  β ≈ 0. The first pass reported narrower windows that appeared to work; they were artefacts of
  window choice.

`FINDINGS.md` and `results.txt` here therefore contain numbers that disagree with the paper.
Do not cite them. `analyze.py` is the script that produced them.

Current pipeline: `final_analysis.py` → `out/final_results.txt`, figures, `out/paper.md` →
`build_docx.py` → `out/Pricing_Regime_Change.docx`.
