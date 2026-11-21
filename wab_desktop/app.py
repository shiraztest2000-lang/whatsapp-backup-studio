"""Cross-platform desktop UI for WhatsApp Backup Tools."""

from __future__ import annotations

import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from .commands import build_archiver_args, build_restore_args, parse_authorized_adb_devices

TEXT = {
    "en": {
        "title": "WhatsApp Backup Studio",
        "heading": "WhatsApp Backup Studio",
        "note": "Your backup data stays on this computer. Work on a COPY of your phone backup, never on live device files.",
        "language": "Language",
        "android": "Android backup",
        "ios": "iPhone / iOS backup",
        "restore": "Restore (Android only)",
        "db": "Encrypted msgstore database",
        "media": "WhatsApp media folder (optional)",
        "key": "64-character encryption key",
        "ios_backup": "Local iPhone backup folder",
        "archive": "Archive output folder",
        "restore_source": "Existing Android archive folder",
        "choose": "Browse…",
        "preview": "1. Preview (Dry Run)",
        "run": "2. Create Backup",
        "restore_preview": "1. Preview Restore",
        "restore_run": "2. Restore Media",
        "viewer": "Open Chat Viewer",
        "ready": "Ready",
        "running": "Working…",
        "done": "Operation completed successfully.",
        "failed": "The operation failed. Review the log.",
        "confirm_backup": "The preview completed. This will now write files into the selected archive folder. Continue?",
        "confirm_restore": "This reconstructs the Android Media/ tree inside the selected archive. Existing files are not overwritten. Continue?",
        "missing": "Missing or invalid information",
        "not_found": "Selected path does not exist.",
        "select_folder": "Select folder",
        "select_file": "Select backup database",
        "log_hint": "Operation details appear here.",
        "viewer_missing": "Select an existing archive folder first.",
        "restore_note": "Restore reconstructs the Android Media/ folder and msgstore.db inside the archive. It does not install data into a live phone or restore iOS backups. Copy the resulting Media folder to your phone only after reviewing it.",
        "restore_help": "The upstream restore feature supports Android media reconstruction only. Chat database injection into a live WhatsApp installation is intentionally not automated.",
        "transfer": "Copy restored media to phone (ADB)",
        "transfer_confirm": "Copy the restored Media folder to a separate staging folder in Android Downloads? This will not overwrite the live WhatsApp media folder.",
        "transfer_done": "Media copied to Android Downloads / WhatsApp-Restore-Preview. Review it on the phone, then move files manually if needed.",
        "adb_missing": "ADB is unavailable. Keep the platform-tools folder beside the portable application, or install Android platform-tools for a development run.",
        "adb_device": "Connect and authorize exactly one Android phone with USB debugging enabled, then try again.",
        "python_needed": "The desktop interface requires PySide6. Install with: python -m pip install 'whatsapp-backup-tools[desktop]'",
        "process_error": "Could not start the backup tool. Check the portable package files or Python installation.",
        "finished": "Finished",
        "viewer_error": "Could not start the chat viewer.",
        "restore_title": "Confirm restore",
        "backup_title": "Confirm backup",
        "browse_archive": "Select archive folder",
        "restore_done": "Restore completed. Review the Media folder before transferring it to a phone.",
    },
    "fa": {
        "title": "استودیو پشتیبان واتساپ",
        "heading": "استودیو پشتیبان واتساپ",
        "note": "اطلاعات بکاپ روی همین رایانه می‌ماند. همیشه از یک کپی بکاپ استفاده کنید، نه فایل‌های زنده گوشی.",
        "language": "زبان",
        "android": "پشتیبان اندروید",
        "ios": "پشتیبان آیفون / iOS",
        "restore": "بازگردانی (فقط اندروید)",
        "db": "فایل دیتابیس رمزگذاری‌شده msgstore",
        "media": "پوشه رسانه واتساپ (اختیاری)",
        "key": "کلید رمزگذاری ۶۴ کاراکتری",
        "ios_backup": "پوشه بکاپ محلی آیفون",
        "archive": "پوشه مقصد پشتیبان",
        "restore_source": "پوشه آرشیو اندروید موجود",
        "choose": "انتخاب…",
        "preview": "۱. پیش‌نمایش (Dry Run)",
        "run": "۲. ایجاد پشتیبان",
        "restore_preview": "۱. پیش‌نمایش بازگردانی",
        "restore_run": "۲. بازگردانی رسانه",
        "viewer": "نمایش گفتگوها",
        "ready": "آماده",
        "running": "در حال اجرا…",
        "done": "عملیات با موفقیت پایان یافت.",
        "failed": "عملیات ناموفق بود. گزارش را بررسی کنید.",
        "confirm_backup": "پیش‌نمایش موفق بود. اکنون فایل‌ها در پوشه انتخاب‌شده نوشته می‌شوند. ادامه می‌دهید؟",
        "confirm_restore": "ساختار Media اندروید داخل آرشیو انتخاب‌شده بازسازی می‌شود. فایل‌های موجود بازنویسی نمی‌شوند. ادامه می‌دهید؟",
        "missing": "اطلاعات ناقص یا نامعتبر",
        "not_found": "مسیر انتخاب‌شده وجود ندارد.",
        "select_folder": "انتخاب پوشه",
        "select_file": "انتخاب فایل دیتابیس",
        "log_hint": "جزئیات عملیات در این قسمت نمایش داده می‌شود.",
        "viewer_missing": "ابتدا یک پوشه آرشیو موجود انتخاب کنید.",
        "restore_note": "بازگردانی، پوشه Media و فایل msgstore.db را داخل آرشیو بازسازی می‌کند. این عملیات اطلاعات را مستقیماً در گوشی نصب نمی‌کند و بکاپ iOS را بازگردانی نمی‌کند. پس از بررسی، پوشه Media را به گوشی منتقل کنید.",
        "restore_help": "قابلیت اصلی فقط بازسازی رسانه‌های اندروید را پشتیبانی می‌کند. تزریق دیتابیس گفتگو به واتساپ فعال روی گوشی عمداً خودکار نشده است.",
        "transfer": "انتقال رسانه بازسازی‌شده به گوشی (ADB)",
        "transfer_confirm": "پوشه Media در یک پوشه موقت و جداگانه در Downloads گوشی کپی شود؟ پوشه رسانه فعال واتساپ بازنویسی نمی‌شود.",
        "transfer_done": "رسانه‌ها در Downloads / WhatsApp-Restore-Preview گوشی کپی شدند. آن‌ها را در گوشی بررسی و در صورت نیاز دستی منتقل کنید.",
        "adb_missing": "ADB در دسترس نیست. پوشه platform-tools را کنار برنامه پرتابل نگه دارید یا برای اجرای توسعه، Android platform-tools را نصب کنید.",
        "adb_device": "دقیقاً یک گوشی اندرویدی را با USB debugging متصل و مجوز اتصال را تأیید کنید، سپس دوباره تلاش کنید.",
        "python_needed": "رابط دسکتاپ به PySide6 نیاز دارد. نصب: python -m pip install 'whatsapp-backup-tools[desktop]'",
        "process_error": "اجرای ابزار ممکن نشد. فایل‌های بسته پرتابل یا نصب Python را بررسی کنید.",
        "finished": "پایان عملیات",
        "viewer_error": "اجرای نمایشگر گفتگوها ممکن نشد.",
        "restore_title": "تأیید بازگردانی",
        "backup_title": "تأیید پشتیبان‌گیری",
        "browse_archive": "انتخاب پوشه آرشیو",
        "restore_done": "بازگردانی انجام شد. پیش از انتقال به گوشی، پوشه Media را بررسی کنید.",
    },
}


def _frozen_helper(name: str) -> str | None:
    if not getattr(sys, "frozen", False):
        return None
    exe_name = f"{name}.exe" if sys.platform == "win32" else name
    return str(Path(sys.executable).resolve().parent.parent / name / exe_name)


def main() -> None:
    try:
        from PySide6.QtCore import QProcess, Qt
        from PySide6.QtGui import QTextCursor
        from PySide6.QtWidgets import (
            QApplication,
            QComboBox,
            QFileDialog,
            QFormLayout,
            QHBoxLayout,
            QLabel,
            QLineEdit,
            QMainWindow,
            QMessageBox,
            QPlainTextEdit,
            QPushButton,
            QTabWidget,
            QVBoxLayout,
            QWidget,
        )
    except ImportError as exc:
        raise SystemExit(TEXT["en"]["python_needed"]) from exc

    class StudioWindow(QMainWindow):
        def __init__(self) -> None:
            super().__init__()
            self.language = "en"
            self.preview_completed = False
            self.restore_preview_completed = False
            self._last_action = "archive"
            self.process = QProcess(self)
            self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
            self.process.readyReadStandardOutput.connect(self._read_output)
            self.process.finished.connect(self._finished)
            self.process.errorOccurred.connect(self._process_error)

            root = QWidget()
            layout = QVBoxLayout(root)
            top = QHBoxLayout()
            self.heading = QLabel()
            self.heading.setStyleSheet("font-size: 22px; font-weight: 700; padding: 8px;")
            top.addWidget(self.heading, 1)
            self.language_label = QLabel()
            self.language_combo = QComboBox()
            self.language_combo.addItem("English", "en")
            self.language_combo.addItem("فارسی", "fa")
            self.language_combo.currentIndexChanged.connect(self._change_language)
            top.addWidget(self.language_label)
            top.addWidget(self.language_combo)
            layout.addLayout(top)

            self.note = QLabel()
            self.note.setWordWrap(True)
            layout.addWidget(self.note)

            self.tabs = QTabWidget()
            self.android = self._make_android_tab()
            self.ios = self._make_ios_tab()
            self.restore = self._make_restore_tab()
            self.tabs.addTab(self.android, "")
            self.tabs.addTab(self.ios, "")
            self.tabs.addTab(self.restore, "")
            layout.addWidget(self.tabs)

            self.output_row, self.output_path = self._path_row("archive folder", True)
            layout.addWidget(self.output_row)
            for field in (
                self.android_db,
                self.android_root,
                self.android_key,
                self.ios_backup,
                self.output_path,
                self.restore_source,
            ):
                field.textChanged.connect(self._invalidate_previews)
            self.tabs.currentChanged.connect(self._invalidate_previews)

            actions = QHBoxLayout()
            self.preview_button = QPushButton()
            self.run_button = QPushButton()
            self.restore_preview_button = QPushButton()
            self.restore_run_button = QPushButton()
            self.viewer_button = QPushButton()
            self.preview_button.clicked.connect(lambda: self._run_archive(True))
            self.run_button.clicked.connect(lambda: self._run_archive(False))
            self.restore_preview_button.clicked.connect(lambda: self._run_restore(True))
            self.restore_run_button.clicked.connect(lambda: self._run_restore(False))
            self.viewer_button.clicked.connect(self._open_viewer)
            for button in (
                self.preview_button,
                self.run_button,
                self.restore_preview_button,
                self.restore_run_button,
                self.viewer_button,
            ):
                actions.addWidget(button)
            layout.addLayout(actions)

            self.status = QLabel()
            layout.addWidget(self.status)
            self.log = QPlainTextEdit()
            self.log.setReadOnly(True)
            layout.addWidget(self.log, 1)
            self.setCentralWidget(root)
            self._translate()
            self._set_busy(False)

        def tr(self, key: str) -> str:
            return TEXT[self.language][key]

        def _path_row(self, placeholder: str, directory: bool):
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            edit = QLineEdit()
            edit.setPlaceholderText(placeholder)
            button = QPushButton()
            button.clicked.connect(lambda: self._choose_path(edit, directory))
            row_layout.addWidget(edit, 1)
            row_layout.addWidget(button)
            return row, edit

        def _choose_path(self, edit, directory: bool) -> None:
            if directory:
                selected = QFileDialog.getExistingDirectory(self, self.tr("select_folder"))
            else:
                selected, _ = QFileDialog.getOpenFileName(self, self.tr("select_file"))
            if selected:
                edit.setText(selected)

        def _make_android_tab(self):
            page = QWidget()
            form = QFormLayout(page)
            row, self.android_db = self._path_row("msgstore.db.crypt14 / crypt15", False)
            form.addRow("", row)
            row, self.android_root = self._path_row("WhatsApp/Media", True)
            form.addRow("", row)
            self.android_key = QLineEdit()
            self.android_key.setEchoMode(QLineEdit.EchoMode.Password)
            form.addRow("", self.android_key)
            return page

        def _make_ios_tab(self):
            page = QWidget()
            form = QFormLayout(page)
            row, self.ios_backup = self._path_row("Finder / Apple Devices / iTunes backup", True)
            form.addRow("", row)
            return page

        def _make_restore_tab(self):
            page = QWidget()
            form = QVBoxLayout(page)
            row, self.restore_source = self._path_row("Existing archive folder", True)
            form.addWidget(row)
            self.restore_note = QLabel()
            self.restore_note.setWordWrap(True)
            form.addWidget(self.restore_note)
            self.restore_help = QLabel()
            self.restore_help.setWordWrap(True)
            form.addWidget(self.restore_help)
            self.transfer_button = QPushButton()
            self.transfer_button.clicked.connect(self._copy_media_to_phone)
            form.addWidget(self.transfer_button)
            return page

        def _translate(self):
            self.setWindowTitle(self.tr("title"))
            self.heading.setText(self.tr("heading"))
            self.note.setText(self.tr("note"))
            self.language_label.setText(self.tr("language"))
            self.tabs.setTabText(0, self.tr("android"))
            self.tabs.setTabText(1, self.tr("ios"))
            self.tabs.setTabText(2, self.tr("restore"))
            self.android_db.setPlaceholderText(self.tr("db"))
            self.android_root.setPlaceholderText(self.tr("media"))
            self.android_key.setPlaceholderText(self.tr("key"))
            self.ios_backup.setPlaceholderText(self.tr("ios_backup"))
            self.output_path.setPlaceholderText(self.tr("archive"))
            self.restore_source.setPlaceholderText(self.tr("restore_source"))
            for row in (
                self.android_db.parentWidget(),
                self.android_root.parentWidget(),
                self.ios_backup.parentWidget(),
                self.output_path.parentWidget(),
                self.restore_source.parentWidget(),
            ):
                button = row.findChild(QPushButton)
                if button:
                    button.setText(self.tr("choose"))
            self.restore_note.setText(self.tr("restore_note"))
            self.restore_help.setText(self.tr("restore_help"))
            self.transfer_button.setText(self.tr("transfer"))
            self.preview_button.setText(self.tr("preview"))
            self.run_button.setText(self.tr("run"))
            self.restore_preview_button.setText(self.tr("restore_preview"))
            self.restore_run_button.setText(self.tr("restore_run"))
            self.viewer_button.setText(self.tr("viewer"))
            self.status.setText(self.tr("ready"))
            self.log.setPlaceholderText(self.tr("log_hint"))
            self.setLayoutDirection(
                Qt.LayoutDirection.RightToLeft
                if self.language == "fa"
                else Qt.LayoutDirection.LeftToRight
            )

        def _change_language(self, _index: int):
            self.language = self.language_combo.currentData()
            self._translate()

        def _invalidate_previews(self, *_args):
            self.preview_completed = False
            self.restore_preview_completed = False
            self._set_busy(self.process.state() != QProcess.ProcessState.NotRunning)

        def _set_busy(self, busy: bool):
            archive_tab = self.tabs.currentIndex() in (0, 1)
            restore_tab = self.tabs.currentIndex() == 2
            self.tabs.setEnabled(not busy)
            self.output_path.setEnabled(not busy)
            self.preview_button.setVisible(archive_tab)
            self.run_button.setVisible(archive_tab)
            self.restore_preview_button.setVisible(restore_tab)
            self.restore_run_button.setVisible(restore_tab)
            self.transfer_button.setVisible(restore_tab)
            self.viewer_button.setVisible(not busy)
            self.preview_button.setEnabled(not busy)
            self.run_button.setEnabled(not busy and self.preview_completed)
            self.restore_preview_button.setEnabled(not busy)
            self.restore_run_button.setEnabled(not busy and self.restore_preview_completed)
            self.transfer_button.setEnabled(not busy)

        def _start(self, args: list[str], action: str, dry_run: bool):
            if getattr(sys, "frozen", False):
                helper = _frozen_helper("wab-archiver")
                if not helper or not Path(helper).is_file():
                    QMessageBox.critical(self, self.tr("failed"), self.tr("process_error"))
                    self._set_busy(False)
                    return
                program, arguments = helper, args
            else:
                program, arguments = sys.executable, ["-m", "wab_archiver", *args]
            self._last_action = action
            self._last_run_was_dry_run = dry_run
            self.log.clear()
            self.status.setText(self.tr("running"))
            self._set_busy(True)
            self.process.start(program, arguments)

        def _run_archive(self, dry_run: bool):
            if self.process.state() != QProcess.ProcessState.NotRunning:
                return
            platform = "android" if self.tabs.currentIndex() == 0 else "ios"
            source = (
                self.android_db.text().strip()
                if platform == "android"
                else self.ios_backup.text().strip()
            )
            output = self.output_path.text().strip()
            try:
                args = build_archiver_args(
                    platform,
                    source,
                    output,
                    e2e_key=self.android_key.text() if platform == "android" else "",
                    wa_root=self.android_root.text() if platform == "android" else "",
                    dry_run=dry_run,
                )
            except ValueError as exc:
                QMessageBox.warning(self, self.tr("missing"), str(exc))
                return
            valid = Path(source).is_file() if platform == "android" else Path(source).is_dir()
            if not valid:
                QMessageBox.warning(self, self.tr("missing"), self.tr("not_found"))
                return
            if (
                platform == "android"
                and self.android_root.text().strip()
                and not Path(self.android_root.text().strip()).is_dir()
            ):
                QMessageBox.warning(self, self.tr("missing"), self.tr("not_found"))
                return
            if not dry_run:
                answer = QMessageBox.question(
                    self,
                    self.tr("backup_title"),
                    self.tr("confirm_backup"),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if answer != QMessageBox.StandardButton.Yes:
                    return
            self._start(args, "archive", dry_run)

        def _run_restore(self, dry_run: bool):
            if self.process.state() != QProcess.ProcessState.NotRunning:
                return
            archive = self.restore_source.text().strip()
            try:
                args = build_restore_args(archive, dry_run=dry_run)
            except ValueError as exc:
                QMessageBox.warning(self, self.tr("missing"), str(exc))
                return
            if (
                not Path(archive).is_dir()
                or not (Path(archive) / ".wa_media_archiver.db").is_file()
                or not (Path(archive) / "Whatsapp Databases" / "msgstore.db").is_file()
            ):
                QMessageBox.warning(self, self.tr("missing"), self.tr("not_found"))
                return
            if not dry_run:
                answer = QMessageBox.question(
                    self,
                    self.tr("restore_title"),
                    self.tr("confirm_restore"),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if answer != QMessageBox.StandardButton.Yes:
                    return
            self._start(args, "restore", dry_run)

        def _copy_media_to_phone(self):
            archive = self.restore_source.text().strip()
            media = Path(archive) / "Media"
            if not media.is_dir():
                QMessageBox.warning(self, self.tr("missing"), self.tr("not_found"))
                return
            if getattr(sys, "frozen", False):
                adb_path = (
                    Path(sys.executable).resolve().parent.parent / "platform-tools" / "adb.exe"
                )
                adb = str(adb_path) if adb_path.is_file() else None
            else:
                adb = shutil.which("adb")
            if not adb:
                QMessageBox.warning(self, self.tr("missing"), self.tr("adb_missing"))
                return
            try:
                completed = subprocess.run(
                    [adb, "devices"],
                    capture_output=True,
                    text=True,
                    timeout=12,
                    check=True,
                    creationflags=(subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0),
                )
            except (OSError, subprocess.SubprocessError):
                QMessageBox.warning(self, self.tr("missing"), self.tr("adb_device"))
                return
            devices = parse_authorized_adb_devices(completed.stdout)
            if len(devices) != 1:
                QMessageBox.warning(self, self.tr("missing"), self.tr("adb_device"))
                return
            destination = "/sdcard/Download/WhatsApp-Restore-Preview/" + datetime.now().strftime(
                "%Y%m%d-%H%M%S"
            )
            answer = QMessageBox.question(
                self,
                self.tr("restore_title"),
                self.tr("transfer_confirm") + "\n\n" + destination,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
            self._adb_program = adb
            self._adb_serial = devices[0]
            self._adb_media = str(media)
            self._adb_destination = destination
            self._last_action = "adb_mkdir"
            self.log.clear()
            self.status.setText(self.tr("running"))
            self._set_busy(True)
            self.process.start(
                adb,
                ["-s", self._adb_serial, "shell", "mkdir", "-p", destination],
            )

        def _read_output(self):
            raw = bytes(self.process.readAllStandardOutput()).decode("utf-8", errors="replace")
            if raw:
                self.log.moveCursor(QTextCursor.MoveOperation.End)
                self.log.insertPlainText(raw)
                self.log.ensureCursorVisible()

        def _finished(self, exit_code: int, _exit_status):
            if self._last_action == "adb_mkdir" and exit_code == 0:
                self._last_action = "adb_push"
                self.process.start(
                    self._adb_program,
                    [
                        "-s",
                        self._adb_serial,
                        "push",
                        self._adb_media,
                        self._adb_destination + "/",
                    ],
                )
                return
            if self._last_action == "adb_push":
                self._set_busy(False)
                if exit_code == 0:
                    self.status.setText(self.tr("done"))
                    QMessageBox.information(self, self.tr("finished"), self.tr("transfer_done"))
                else:
                    self.status.setText(self.tr("failed"))
                    QMessageBox.warning(self, self.tr("failed"), self.tr("failed"))
                return
            if exit_code == 0:
                if self._last_action == "archive":
                    self.preview_completed = self._last_run_was_dry_run
                elif self._last_action == "restore":
                    self.restore_preview_completed = self._last_run_was_dry_run
            self._set_busy(False)
            self.status.setText(self.tr("done") if exit_code == 0 else self.tr("failed"))
            if exit_code == 0:
                message = (
                    self.tr("restore_done")
                    if self._last_action == "restore" and not self._last_run_was_dry_run
                    else self.tr("done")
                )
                QMessageBox.information(self, self.tr("finished"), message)
            else:
                QMessageBox.warning(self, self.tr("failed"), self.tr("failed"))

        def _process_error(self, _error):
            self._set_busy(False)
            self.status.setText(self.tr("failed"))
            self.log.appendPlainText(self.tr("process_error"))

        def _open_viewer(self):
            archive = self.output_path.text().strip()
            if not archive or not Path(archive).is_dir():
                archive = self.restore_source.text().strip()
            if not archive or not Path(archive).is_dir():
                QMessageBox.warning(self, self.tr("missing"), self.tr("viewer_missing"))
                return
            if getattr(sys, "frozen", False):
                helper = _frozen_helper("wab-viewer")
                if not helper or not Path(helper).is_file():
                    QMessageBox.warning(self, self.tr("failed"), self.tr("viewer_error"))
                    return
                program, args = helper, [archive]
            else:
                program, args = sys.executable, ["-m", "wab_viewer", archive]
            ok = QProcess.startDetached(program, args)
            if isinstance(ok, tuple):
                ok = ok[0]
            if not ok:
                QMessageBox.warning(self, self.tr("failed"), self.tr("viewer_error"))

    if "--self-test" in sys.argv:
        app = QApplication([])
        window = StudioWindow()
        assert window.language == "en"
        assert window.tabs.tabText(0) == TEXT["en"]["android"]
        window.language_combo.setCurrentIndex(1)
        assert window.language == "fa"
        window.language_combo.setCurrentIndex(0)
        assert window.language == "en"
        return

    app = QApplication(sys.argv)
    app.setApplicationName("WhatsApp Backup Studio")
    app.setOrganizationName("ShirazTipsy")
    window = StudioWindow()
    window.show()
    sys.exit(app.exec())
