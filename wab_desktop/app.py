"""PySide6 desktop application; all backup processing stays in upstream CLI."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from .commands import build_archiver_args


def main() -> None:
    try:
        from PySide6.QtCore import QProcess, Qt
        from PySide6.QtGui import QTextCursor
        from PySide6.QtWidgets import (
            QApplication,
            QFileDialog,
            QFormLayout,
            QHBoxLayout,
            QLabel,
            QLineEdit,
            QMainWindow,
            QMessageBox,
            QPushButton,
            QPlainTextEdit,
            QTabWidget,
            QVBoxLayout,
            QWidget,
        )
    except ImportError as exc:
        raise SystemExit(
            "رابط گرافیکی به PySide6 نیاز دارد. نصب کنید: "
            "python -m pip install 'whatsapp-backup-tools[desktop]'"
        ) from exc

    class StudioWindow(QMainWindow):
        def __init__(self) -> None:
            super().__init__()
            self.setWindowTitle("WhatsApp Backup Studio")
            self.resize(900, 680)
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            self.process = QProcess(self)
            self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
            self.process.readyReadStandardOutput.connect(self._read_output)
            self.process.finished.connect(self._finished)
            self.process.errorOccurred.connect(self._process_error)

            root = QWidget()
            layout = QVBoxLayout(root)
            heading = QLabel("مدیریت و آرشیو بکاپ واتساپ")
            heading.setStyleSheet("font-size: 22px; font-weight: 700; padding: 8px;")
            layout.addWidget(heading)
            note = QLabel(
                "پردازش روی همین رایانه انجام می‌شود. ابتدا پیش‌نمایش را اجرا کنید؛ "
                "برای ساخت آرشیو، اجرای واقعی را جداگانه تأیید کنید."
            )
            note.setWordWrap(True)
            layout.addWidget(note)

            self.tabs = QTabWidget()
            self.android = self._make_android_tab()
            self.ios = self._make_ios_tab()
            self.tabs.addTab(self.android, "اندروید")
            self.tabs.addTab(self.ios, "آیفون / iOS")
            layout.addWidget(self.tabs)

            actions = QHBoxLayout()
            self.preview_button = QPushButton("۱. پیش‌نمایش امن (Dry Run)")
            self.run_button = QPushButton("۲. اجرای واقعی آرشیو")
            self.viewer_button = QPushButton("باز کردن نمایشگر گفتگوها")
            self.preview_button.clicked.connect(lambda: self._run_archive(True))
            self.run_button.clicked.connect(lambda: self._run_archive(False))
            self.viewer_button.clicked.connect(self._open_viewer)
            actions.addWidget(self.preview_button)
            actions.addWidget(self.run_button)
            actions.addWidget(self.viewer_button)
            layout.addLayout(actions)

            self.status = QLabel("آماده")
            layout.addWidget(self.status)
            self.log = QPlainTextEdit()
            self.log.setReadOnly(True)
            self.log.setPlaceholderText("گزارش اجرای ابزار در این قسمت نمایش داده می‌شود.")
            layout.addWidget(self.log, 1)
            self.setCentralWidget(root)
            self._set_busy(False)

        def _path_row(self, placeholder: str, directory: bool) -> tuple[QWidget, QLineEdit]:
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            edit = QLineEdit()
            edit.setPlaceholderText(placeholder)
            button = QPushButton("انتخاب…")
            button.clicked.connect(
                lambda: self._choose_path(edit, directory)
            )
            row_layout.addWidget(edit, 1)
            row_layout.addWidget(button)
            return row, edit

        def _choose_path(self, edit: QLineEdit, directory: bool) -> None:
            if directory:
                selected = QFileDialog.getExistingDirectory(self, "انتخاب پوشه")
            else:
                selected, _ = QFileDialog.getOpenFileName(self, "انتخاب فایل بکاپ")
            if selected:
                edit.setText(selected)

        def _make_android_tab(self) -> QWidget:
            page = QWidget()
            form = QFormLayout(page)
            row, self.android_db = self._path_row(
                "مسیر msgstore.db.crypt14 / crypt15", False
            )
            form.addRow("فایل دیتابیس رمزگذاری‌شده:", row)
            row, self.android_root = self._path_row(
                "پوشه WhatsApp استخراج‌شده (اختیاری)", True
            )
            form.addRow("پوشه رسانه (اختیاری):", row)
            self.android_key = QLineEdit()
            self.android_key.setEchoMode(QLineEdit.EchoMode.Password)
            self.android_key.setPlaceholderText("کلید ۶۴ رقمی بکاپ؛ ذخیره نمی‌شود")
            form.addRow("کلید رمزگشایی:", self.android_key)
            return page

        def _make_ios_tab(self) -> QWidget:
            page = QWidget()
            form = QFormLayout(page)
            row, self.ios_backup = self._path_row(
                "پوشه بکاپ محلی Finder / Apple Devices / iTunes", True
            )
            form.addRow("پوشه بکاپ iOS:", row)
            return page

        def _make_output(self) -> str:
            if not hasattr(self, "output_row"):
                self.output_row, self.output_path = self._path_row(
                    "پوشه مقصد آرشیو", True
                )
                self.centralWidget().layout().insertWidget(2, self.output_row)
            return self.output_path.text().strip()

        def _run_archive(self, dry_run: bool) -> None:
            if self.process.state() != QProcess.ProcessState.NotRunning:
                return
            platform = "android" if self.tabs.currentIndex() == 0 else "ios"
            source = self.android_db.text() if platform == "android" else self.ios_backup.text()
            output = self._make_output()
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
                QMessageBox.warning(self, "اطلاعات ناقص یا نامعتبر", str(exc))
                return

            if platform == "android" and not Path(source).is_file():
                QMessageBox.warning(self, "فایل پیدا نشد", "فایل دیتابیس انتخاب‌شده وجود ندارد.")
                return
            if platform == "ios" and not Path(source).is_dir():
                QMessageBox.warning(self, "پوشه پیدا نشد", "پوشه بکاپ iOS انتخاب‌شده وجود ندارد.")
                return
            if platform == "android" and self.android_root.text().strip():
                if not Path(self.android_root.text().strip()).is_dir():
                    QMessageBox.warning(self, "پوشه پیدا نشد", "پوشه رسانه انتخاب‌شده وجود ندارد.")
                    return
            if not dry_run:
                answer = QMessageBox.question(
                    self,
                    "تأیید اجرای واقعی",
                    "پیش‌نمایش را بررسی کرده‌اید؟ اکنون فایل‌های رسانه در پوشه مقصد کپی می‌شوند. ادامه می‌دهید؟",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )
                if answer != QMessageBox.StandardButton.Yes:
                    return

            self.log.clear()
            self.status.setText("در حال اجرا…")
            self._set_busy(True)
            # No shell is used. The encryption key is never written to the log or a config file.
            self.process.start(sys.executable, args)

        def _read_output(self) -> None:
            raw = bytes(self.process.readAllStandardOutput()).decode("utf-8", errors="replace")
            if raw:
                self.log.moveCursor(QTextCursor.MoveOperation.End)
                self.log.insertPlainText(raw)
                self.log.ensureCursorVisible()

        def _finished(self, exit_code: int, _exit_status: object) -> None:
            self._set_busy(False)
            self.status.setText("پایان موفق" if exit_code == 0 else f"پایان با خطا (کد {exit_code})")
            if exit_code == 0:
                QMessageBox.information(self, "پایان عملیات", "عملیات با موفقیت پایان یافت.")
            else:
                QMessageBox.warning(self, "خطا", "اجرای ابزار با خطا پایان یافت. گزارش را بررسی کنید.")

        def _process_error(self, _error: object) -> None:
            self._set_busy(False)
            self.status.setText("اجرای فرایند ناموفق بود")
            self.log.appendPlainText("خطا در راه‌اندازی ابزار. نصب بودن وابستگی‌ها و Python را بررسی کنید.")

        def _set_busy(self, busy: bool) -> None:
            self.preview_button.setEnabled(not busy)
            self.run_button.setEnabled(not busy)

        def _open_viewer(self) -> None:
            archive = self._make_output()
            if not archive or not Path(archive).is_dir():
                QMessageBox.warning(self, "آرشیو پیدا نشد", "ابتدا پوشه آرشیو موجود را انتخاب کنید.")
                return
            result = QProcess.startDetached(sys.executable, ["-m", "wab_viewer", archive])
            ok = result[0] if isinstance(result, tuple) else result
            if not ok:
                QMessageBox.warning(self, "خطا", "اجرای نمایشگر گفتگوها ممکن نشد.")

    app = QApplication(sys.argv)
    app.setApplicationName("WhatsApp Backup Studio")
    window = StudioWindow()
    window.show()
    sys.exit(app.exec())
