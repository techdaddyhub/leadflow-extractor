"""
Generates high-resolution multi-size Windows icon (.ico) for LeadFlow.
"""

from pathlib import Path
from PIL import Image, ImageDraw

def create_leadflow_icon(output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    images = []

    for width, height in sizes:
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Draw rounded card background (Deep Indigo gradient simulated with solid electric violet)
        bg_color = (99, 102, 241, 255)  # #6366f1
        border_color = (129, 140, 248, 255)  # #818cf8
        radius = int(width * 0.22)
        margin = max(1, int(width * 0.05))

        draw.rounded_rectangle(
            [margin, margin, width - margin, height - margin],
            radius=radius,
            fill=bg_color,
            outline=border_color,
            width=max(1, int(width * 0.03))
        )

        # Draw envelope shape
        env_x0 = int(width * 0.20)
        env_y0 = int(height * 0.28)
        env_x1 = int(width * 0.80)
        env_y1 = int(height * 0.72)
        line_w = max(1, int(width * 0.04))

        # Envelope rectangle
        draw.rounded_rectangle(
            [env_x0, env_y0, env_x1, env_y1],
            radius=max(2, int(width * 0.05)),
            fill=(255, 255, 255, 245),
            outline=(240, 240, 255, 255),
            width=line_w
        )

        # Envelope flap lines
        mid_x = width // 2
        flap_y = int(height * 0.52)
        draw.line([(env_x0, env_y0), (mid_x, flap_y)], fill=(99, 102, 241, 255), width=line_w)
        draw.line([(env_x1, env_y0), (mid_x, flap_y)], fill=(99, 102, 241, 255), width=line_w)

        # Small bright accent dot (emerald green flow signal)
        signal_r = max(2, int(width * 0.07))
        signal_x = int(width * 0.74)
        signal_y = int(height * 0.26)
        draw.ellipse(
            [signal_x - signal_r, signal_y - signal_r, signal_x + signal_r, signal_y + signal_r],
            fill=(16, 185, 129, 255),  # #10b981
            outline=(255, 255, 255, 255),
            width=max(1, int(width * 0.02))
        )

        images.append(img)

    images[0].save(
        output_path,
        format="ICO",
        sizes=[(im.width, im.height) for im in images],
        append_images=images[1:]
    )
    print(f"Generated {output_path} successfully.")

if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "assets" / "icon.ico"
    create_leadflow_icon(out)

