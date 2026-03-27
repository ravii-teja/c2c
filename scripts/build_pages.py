from __future__ import annotations

import argparse
import html
from pathlib import Path

try:
    import markdown
except ImportError as exc:  # pragma: no cover - exercised in CI rather than unit tests.
    raise SystemExit(
        "The 'markdown' package is required to build the GitHub Pages site. "
        "Install it with 'python -m pip install markdown'."
    ) from exc


PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title}</title>
    <style>
      :root {{
        color-scheme: light;
        --bg: #f4f1ea;
        --surface: #fffdf8;
        --text: #1f1a17;
        --muted: #695a50;
        --accent: #8a4b2a;
        --border: #dfd2c1;
        --code-bg: #f1e7da;
      }}

      * {{
        box-sizing: border-box;
      }}

      body {{
        margin: 0;
        background:
          radial-gradient(circle at top left, rgba(138, 75, 42, 0.08), transparent 32%),
          linear-gradient(180deg, #f8f5ee 0%, var(--bg) 100%);
        color: var(--text);
        font-family: Georgia, "Times New Roman", serif;
        line-height: 1.7;
      }}

      .page {{
        max-width: 960px;
        margin: 0 auto;
        padding: 48px 20px 80px;
      }}

      .paper {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 48px;
        box-shadow: 0 24px 60px rgba(61, 40, 26, 0.08);
      }}

      .eyebrow {{
        margin: 0 0 12px;
        color: var(--muted);
        font-family: ui-sans-serif, system-ui, sans-serif;
        font-size: 0.95rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
      }}

      h1, h2, h3, h4 {{
        color: var(--text);
        line-height: 1.25;
      }}

      h1 {{
        font-size: clamp(2.2rem, 4vw, 3.4rem);
        margin-top: 0;
      }}

      h2 {{
        margin-top: 2.4rem;
        padding-top: 0.8rem;
        border-top: 1px solid var(--border);
      }}

      a {{
        color: var(--accent);
      }}

      code {{
        background: var(--code-bg);
        border-radius: 6px;
        padding: 0.1rem 0.35rem;
        font-size: 0.95em;
      }}

      pre {{
        overflow-x: auto;
        background: #221b17;
        color: #f8f4ed;
        border-radius: 14px;
        padding: 16px;
      }}

      pre code {{
        background: transparent;
        padding: 0;
        color: inherit;
      }}

      blockquote {{
        margin: 1.5rem 0;
        padding: 0.25rem 1rem;
        border-left: 4px solid var(--accent);
        color: var(--muted);
      }}

      table {{
        width: 100%;
        border-collapse: collapse;
        margin: 1.5rem 0;
      }}

      th, td {{
        border: 1px solid var(--border);
        padding: 0.75rem;
        text-align: left;
        vertical-align: top;
      }}

      .footer {{
        margin-top: 24px;
        color: var(--muted);
        font-family: ui-sans-serif, system-ui, sans-serif;
        font-size: 0.95rem;
      }}

      @media (max-width: 720px) {{
        .page {{
          padding: 24px 12px 48px;
        }}

        .paper {{
          padding: 24px 18px;
          border-radius: 16px;
        }}
      }}
    </style>
  </head>
  <body>
    <main class="page">
      <article class="paper">
        <p class="eyebrow">Chaos 2 Clarity Research Paper</p>
        {body}
        <p class="footer">
          Source markdown:
          <code>docs/research-paper.md</code>
        </p>
      </article>
    </main>
  </body>
</html>
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a GitHub Pages site from the research paper markdown."
    )
    parser.add_argument(
        "--source",
        default="docs/research-paper.md",
        help="Path to the markdown source file.",
    )
    parser.add_argument(
        "--output-dir",
        default="site",
        help="Directory where the Pages artifact should be written.",
    )
    return parser.parse_args()


def extract_title(markdown_text: str, fallback: str) -> str:
    for line in markdown_text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def build_html(markdown_text: str, title: str) -> str:
    body = markdown.markdown(
        markdown_text,
        extensions=["extra", "fenced_code", "tables", "toc", "sane_lists"],
    )
    return PAGE_TEMPLATE.format(title=html.escape(title), body=body)


def main() -> int:
    args = parse_args()
    source_path = Path(args.source)
    output_dir = Path(args.output_dir)

    markdown_text = source_path.read_text(encoding="utf-8")
    title = extract_title(markdown_text, "Chaos 2 Clarity Research Paper")
    html_text = build_html(markdown_text, title)

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "index.html").write_text(html_text, encoding="utf-8")
    (output_dir / ".nojekyll").write_text("", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
