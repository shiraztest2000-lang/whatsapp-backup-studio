# WhatsApp Backup Studio — Portable Windows Build

This is an extracted, portable application bundle. It does not need a Python installation or an installer.

## Run

1. Extract the complete ZIP file to a writable folder.
2. Open `WhatsAppBackupStudio/WhatsAppBackupStudio.exe`.
3. English is selected by default. Use the language selector to switch to فارسی.
4. Select a backup source and destination, run the preview, review the log, and then confirm the real backup.

Keep the entire extracted folder structure together. The archiver and viewer helper folders are required by the desktop application.

## Backup and restore scope

- Android: archive an encrypted msgstore database and an optional local WhatsApp media folder.
- iPhone/iOS: read a local Finder / Apple Devices / iTunes backup.
- Android restore: reconstructs the Media folder and database inside an existing archive.
- The bundled ADB transfer sends restored media to a timestamped staging folder under Android Downloads. It does not overwrite the live WhatsApp media folder; review and move files manually on the phone.
- The app does not inject a plaintext database into an installed WhatsApp app.

## Privacy and safety

- Processing is local; the application does not upload backup contents.
- Use copies of backups, not live device files.
- The Android end-to-end encryption key is not saved in settings or logs. The upstream command-line interface receives it as a process argument while running, so a process inspector under the same Windows account may be able to see it.
- Do not share archives, databases, logs, contacts, or media publicly.

## Troubleshooting

If the application does not start, extract the complete ZIP again and keep all three application/helper folders side by side. Do not move the main executable by itself.
