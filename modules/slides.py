from pathlib import Path


def load_slides(root_path):
    shots_dir = Path(root_path) / "static" / "img" / "screenshots"
    if not shots_dir.exists():
        return []

    slides = []
    for path in shots_dir.iterdir():
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
            continue
        stem = path.stem
        num = int(stem) if stem.isdigit() else None
        slides.append(
            {
                "filename": f"img/screenshots/{path.name}",
                "key": stem,
                "num": num,
            }
        )

    slides.sort(
        key=lambda item: (
            item["num"] is None,
            item["num"] if item["num"] is not None else item["key"],
        )
    )
    return slides
