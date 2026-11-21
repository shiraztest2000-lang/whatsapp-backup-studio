"""Safe command construction for the desktop front end."""

from __future__ import annotations

import re


def build_archiver_args(
    platform: str,
    source_path: str,
    output_path: str,
    *,
    e2e_key: str = "",
    wa_root: str = "",
    dry_run: bool = True,
) -> list[str]:
    """Build argv for the upstream archiver without invoking a shell."""
    source = source_path.strip()
    output = output_path.strip()
    if platform not in {"android", "ios"}:
        raise ValueError("platform must be 'android' or 'ios'")
    if not source:
        raise ValueError("مسیر فایل/پوشه بکاپ را انتخاب کنید.")
    if not output:
        raise ValueError("مسیر پوشه خروجی را انتخاب کنید.")

    args = ["-m", "wab_archiver", "archive"]
    if platform == "android":
        key = e2e_key.strip()
        if not re.fullmatch(r"[0-9a-fA-F]{64}", key):
            raise ValueError("کلید بکاپ اندروید باید دقیقاً ۶۴ رقم هگزادسیمال باشد.")
        args.extend(["--msgstore", source, "--e2e-key", key])
        if wa_root.strip():
            args.extend(["--wa-root", wa_root.strip()])
    else:
        args.extend(["--ios-backup", source])

    args.extend(["--output", output])
    if dry_run:
        args.append("--dry-run")
    return args
