def render_badge(label: str, count: int, color: str = "#007ec6") -> str:
    """Render a shields.io-style SVG badge."""
    count_text = f"{count:,}"

    # Approximate text widths (6.5px per character for the font used)
    char_width = 6.5
    label_width = len(label) * char_width + 10
    count_width = len(count_text) * char_width + 10
    total_width = label_width + count_width

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="20">
  <linearGradient id="smooth" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="round">
    <rect width="{total_width}" height="20" rx="3" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#round)">
    <rect width="{label_width}" height="20" fill="#555"/>
    <rect x="{label_width}" width="{count_width}" height="20" fill="{color}"/>
    <rect width="{total_width}" height="20" fill="url(#smooth)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
    <text x="{label_width / 2}" y="15" fill="#010101" fill-opacity=".3">{label}</text>
    <text x="{label_width / 2}" y="14">{label}</text>
    <text x="{label_width + count_width / 2}" y="15" fill="#010101" fill-opacity=".3">{count_text}</text>
    <text x="{label_width + count_width / 2}" y="14">{count_text}</text>
  </g>
</svg>"""
