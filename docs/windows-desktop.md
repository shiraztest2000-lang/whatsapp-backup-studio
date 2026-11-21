# Windows Desktop Application

The desktop interface is English-first, with an in-app English / Persian language selector. Backup processing is delegated to the upstream archiver and viewer.

## Portable Windows build

The GitHub Actions workflow builds a ZIP bundle containing the GUI and its two helper applications. It is designed to run without installing Python or PySide6.

1. Open the repository's [Actions page](https://github.com/shiraztest2000-lang/whatsapp-backup-studio/actions/workflows/windows-portable.yml).
2. Open the latest successful **Windows Portable Build** run.
3. Download the `WhatsAppBackupStudio-Windows-Portable` artifact.
4. Extract the ZIP completely and run `WhatsAppBackupStudio/WhatsAppBackupStudio.exe`.

Keep the three application folders together. Do not move the GUI executable out of its folder.

## Backup workflow

1. Select Android or iPhone / iOS.
2. Choose the source backup and destination folder.
3. For Android encrypted backups, enter the 64-character hexadecimal key.
4. Run **Preview (Dry Run)** and inspect the output.
5. Confirm **Create Backup** only after reviewing the preview.

**Important:** the upstream Android decryption stage may write a decrypted database into the output folder even during dry-run. Use a protected output folder and treat it as sensitive.

## Restore workflow

The upstream restore command supports Android archives only. It reconstructs the `Media/` tree and `Databases/msgstore.db` locally inside the archive folder. It does not push files to a connected phone or install a database into a live WhatsApp instance. Review the reconstructed media and transfer it to the phone using the normal Android file-transfer process. iOS restore is not supported by the upstream project.

## Security

- The GUI does not save the encryption key in settings or logs.
- The upstream CLI accepts the key as a process argument. A process inspector running under the same Windows account may be able to observe it while the operation is running.
- Use backup copies, never live device files.
- Processing remains local. Do not commit real databases, phone numbers, contacts, media, or private logs.

## Developer installation

For development only:

```powershell
py -m pip install -e ".[desktop]"
py -m wab_desktop
```

The portable package is an extracted folder bundle, not an installer and not a digitally signed release.
