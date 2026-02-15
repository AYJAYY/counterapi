ICON_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAA4AAAAOCAYAAAAfSC3RAAACkUlEQVR42m2RTUgUYRyHf/933tlx"
    "dnd0XdwPTTcwMyK1RKpDkkEFhZcC8eStWx4i6BIRBEldArt0qEg69HGvDh1KKvuSImsVxVSyTM1s"
    "3d3Gdp2dmfffJaGg3/n5HR4ewn/GzCkAWz3PC0gpQ47jFAzDGBFCm1ODjyX27fPpL9gASo2eJzYQ"
    "UVQpZ1rXg9sAtAC4tvpzpe+XnX+frK0/DwCCmYmZEwAuA4E9UsqMpmk5XQ/SePp550B/b8/d62eb"
    "w+XR3Kqd2ftpcuQcM1cSANi2HQ+Hw22Z5blduqbFZmfGds9Oj26Rumkp5YH9NTS1HVwyg9ZVVmqm"
    "OtX48B+3dHrywNj799PDzx7waDp9h5l7mDmTWZy48ubJnVvMXLPO0h+/EJylAWAx4xREt+5/qxTk"
    "5G8+SnA8Vh6NVVUOQjM/bkwIEa8K9xKRt35MIjc0h+xFCXcTUJiC7ym0nTkMw9DR1pxCenIF/Wf3"
    "Z3Zur6sjoqJgZgGgCyHTVytuSYkYw2qFRxG4qowTyVqUBSv8t6PfS5YVCQHoBAAJzEWAurhnu0Up"
    "3QiKE6zcHAwjihNHbJpfmIFaFaLvWFgrN3LfAGvj/Px8UBaLVWHTRHahuGn5+KWjkYogsQwESJKH"
    "GydHgIoGoJRXUGMaEqFFAIWaGisoTNPMuq6rUhviL1q278DXrCU2b2nxxz8rrOUBLx/0veVFzdW7"
    "PWjRYcD1AcsWRGQD+ksAPy6c6rh/qKN+7drtV5rr+iydKZaFe5qsPljQY133AJUD9KdE5EhmJiJ6"
    "w8wA0HS6t2O5tSnV+C493U5JA0i2v4LR8gHAECBGiWiSmWk9hyAiZdt2nChQGwoFGgDkAOgAQihl"
    "JxDAF6Jofp39DXbbMO/Ag17MAAAAAElFTkSuQmCC"
)


def render_badge(label: str, count: int, color: str = "#007ec6", icon: bool = False) -> str:
    """Render a shields.io-style SVG badge."""
    count_text = f"{count:,}"

    # Approximate text widths (6.5px per character for the font used)
    char_width = 6.5
    icon_space = 17 if icon else 0  # extra width for the 14px icon + padding
    label_width = len(label) * char_width + 10 + icon_space
    count_width = len(count_text) * char_width + 10
    total_width = label_width + count_width

    label_text_x = (icon_space + label_width) / 2
    icon_svg = ""
    if icon:
        icon_svg = (
            f'  <image x="4" y="3" width="14" height="14" '
            f'href="data:image/png;base64,{ICON_B64}"/>\n'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{total_width}" height="20">
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
    <text x="{label_text_x}" y="15" fill="#010101" fill-opacity=".3">{label}</text>
    <text x="{label_text_x}" y="14">{label}</text>
    <text x="{label_width + count_width / 2}" y="15" fill="#010101" fill-opacity=".3">{count_text}</text>
    <text x="{label_width + count_width / 2}" y="14">{count_text}</text>
  </g>
{icon_svg}</svg>"""
