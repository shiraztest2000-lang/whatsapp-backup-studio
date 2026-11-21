from __future__ import annotations

import pytest

from wab_desktop.commands import build_archiver_args


def test_android_args_include_dry_run_and_optional_media_root() -> None:
    args = build_archiver_args(
        "android",
        "C:/Backup/msgstore.db.crypt15",
        "C:/Archive",
        e2e_key="a" * 64,
        wa_root="C:/Backup/WhatsApp",
    )
    assert args[:3] == ["-m", "wab_archiver", "archive"]
    assert "--msgstore" in args
    assert "--e2e-key" in args
    assert "--wa-root" in args
    assert args[-1] == "--dry-run"


def test_real_run_omits_dry_run_flag() -> None:
    args = build_archiver_args("ios", "C:/iPhoneBackup", "C:/Archive", dry_run=False)
    assert "--ios-backup" in args
    assert "--dry-run" not in args


@pytest.mark.parametrize("key", ["", "x" * 64, "a" * 63, "a" * 65])
def test_android_rejects_invalid_encryption_key(key: str) -> None:
    with pytest.raises(ValueError):
        build_archiver_args("android", "msgstore.db.crypt15", "archive", e2e_key=key)


def test_rejects_missing_paths_and_unknown_platform() -> None:
    with pytest.raises(ValueError):
        build_archiver_args("android", "", "archive", e2e_key="a" * 64)
    with pytest.raises(ValueError):
        build_archiver_args("ios", "backup", "")
    with pytest.raises(ValueError):
        build_archiver_args("other", "backup", "archive")
