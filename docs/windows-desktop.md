# Windows Desktop Interface

The repository now includes an optional Persian RTL desktop front end built with PySide6.
It delegates archive processing to the existing `wab-archiver` implementation; it does not
reimplement WhatsApp database parsing or decryption.

## Requirements

- Windows 10/11
- Python 3.11 or newer (3.12 recommended)
- A local Android or iOS WhatsApp backup prepared according to the platform guides

## Install from a clone

```powershell
git clone https://github.com/shiraztest2000-lang/whatsapp-backup-studio.git
cd whatsapp-backup-studio
py -m pip install -e ".[desktop]"
py -m wab_desktop
```

The `wab-studio` command is also installed by the editable package install.

## Workflow

1. Choose the Android or iOS tab.
2. Select the backup source and an output folder.
3. For Android, enter the 64-character hexadecimal end-to-end encryption key.
4. Run **Preview (Dry Run)** first and inspect the upstream archiver output.
5. Only after reviewing the preview, choose **Run Archive** and confirm the operation.
6. Use **Open Chat Viewer** to open an existing archive in the local viewer.

The Android media root is optional. If supplied, it must be the extracted WhatsApp media/root folder
expected by the upstream archiver. The GUI currently supports a selected Android msgstore database
and a local iOS device-backup directory; automated ADB acquisition and iOS backup creation remain
outside this first desktop interface.

## Security notes

- The GUI does not save the encryption key in settings, files, or logs.
- The key is passed to the upstream CLI process in its argument list because that is the current
  upstream interface. A process inspector running under the same Windows account may be able to
  observe command-line arguments while the operation is running. Do not run this on a shared or
  untrusted Windows session.
- Use a backup copy, never live device files.
- All archive processing remains local. Do not upload real WhatsApp databases, media, contact names,
  phone numbers, or logs containing personal information to GitHub.

## Current scope

This is the first desktop-interface increment, not a signed standalone installer. It requires Python
and the optional PySide6 dependency. A packaged Windows executable and installer will be added only
after the GUI is exercised on Windows and the upstream test suite passes.
