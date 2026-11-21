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
        raise ValueError("Select a backup source.")
    if not output:
        raise ValueError("Select an output folder.")

    args = ["archive"]
    if platform == "android":
        key = e2e_key.strip()
        if not re.fullmatch(r"[0-9a-fA-F]{64}", key):
            raise ValueError(
                "The Android encryption key must be exactly 64 hexadecimal characters."
            )
        if not wa_root.strip():
            raise ValueError("Select the WhatsApp folder containing the Media/ directory.")
        args.extend(["--msgstore", source, "--e2e-key", key, "--wa-root", wa_root.strip()])
    else:
        args.extend(["--ios-backup", source])

    args.extend(["--output", output])
    if dry_run:
        args.append("--dry-run")
    return args


def build_restore_args(archive_path: str, *, dry_run: bool = True) -> list[str]:
    """Build argv for the upstream Android media restore command."""
    archive = archive_path.strip()
    if not archive:
        raise ValueError("Select an archive folder.")
    args = ["restore", "--output", archive]
    if dry_run:
        args.append("--dry-run")
    return args


def parse_authorized_adb_devices(output: str) -> list[str]:
    """Return serials for ADB devices in the authorized 'device' state."""
    return [
        fields[0]
        for line in output.splitlines()[1:]
        if len(fields := line.split()) >= 2 and fields[1] == "device"
    ]
