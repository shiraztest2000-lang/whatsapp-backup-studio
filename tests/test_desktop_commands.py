from __future__ import annotations

import pytest


def test_android_args_include_dry_run_and_optional_media_root() -> None:
    from wab_desktop.commands import build_archiver_args

    args = build_archiver_args(
        "android",
        "C:/Backup/msgstore.db.crypt15",
        "C:/Archive",
        e2e_key="a" * 64,
        wa_root="C:/Backup/WhatsApp",
    )
    assert args[:2] == ["archive", "--msgstore"]
    assert "--e2e-key" in args
    assert "--wa-root" in args
    assert args[-1] == "--dry-run"


def test_ios_args_are_supported_without_android_key() -> None:
    from wab_desktop.commands import build_archiver_args

    args = build_archiver_args("ios", "C:/iPhoneBackup", "C:/Archive", dry_run=False)
    assert args[:2] == ["archive", "--ios-backup"]
    assert "--dry-run" not in args


@pytest.mark.parametrize("key", ["", "x" * 64, "a" * 63, "a" * 65])
def test_android_rejects_invalid_encryption_key(key: str) -> None:
    from wab_desktop.commands import build_archiver_args

    with pytest.raises(ValueError):
        build_archiver_args("android", "msgstore.db.crypt15", "archive", e2e_key=key)


def test_rejects_missing_paths_and_unknown_platform() -> None:
    from wab_desktop.commands import build_archiver_args

    with pytest.raises(ValueError):
        build_archiver_args("android", "", "archive", e2e_key="a" * 64)
    with pytest.raises(ValueError):
        build_archiver_args("ios", "backup", "")
    with pytest.raises(ValueError):
        build_archiver_args("other", "backup", "archive")


def test_restore_args_default_to_dry_run_and_target_archive() -> None:
    from wab_desktop.commands import build_restore_args

    args = build_restore_args("C:/Archive")
    assert args == ["restore", "--output", "C:/Archive", "--dry-run"]


def test_restore_real_run_requires_explicit_dry_run_false() -> None:
    from wab_desktop.commands import build_restore_args

    args = build_restore_args("C:/Archive", dry_run=False)
    assert args == ["restore", "--output", "C:/Archive"]


def test_restore_rejects_empty_archive_path() -> None:
    from wab_desktop.commands import build_restore_args

    with pytest.raises(ValueError):
        build_restore_args(" ")


def test_adb_parser_returns_only_authorized_devices() -> None:
    from wab_desktop.commands import parse_authorized_adb_devices

    output = (
        "List of devices attached\n"
        "emulator-5554\tdevice\n"
        "phone-unauthorized\tunauthorized\n"
        "phone-offline\toffline\n"
    )
    assert parse_authorized_adb_devices(output) == ["emulator-5554"]


def test_adb_parser_handles_no_connected_devices() -> None:
    from wab_desktop.commands import parse_authorized_adb_devices

    assert parse_authorized_adb_devices("List of devices attached\n") == []


def test_android_requires_whatsapp_root_containing_media() -> None:
    from wab_desktop.commands import build_archiver_args

    with pytest.raises(ValueError, match="containing the Media"):
        build_archiver_args(
            "android",
            "C:/Backup/msgstore.db.crypt15",
            "C:/Archive",
            e2e_key="a" * 64,
        )
