import os
from math import ceil
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSlider,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import QObject, QThread, Signal, Slot

import core


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Video clip compressor")

        central = QWidget()
        self.setCentralWidget(central)

        body = QVBoxLayout(central)
        self.setLayout(body)

        layout = QGridLayout()

        input_label = QLabel("Input")
        self.input_zone = QLineEdit()
        input_browse = QPushButton("Browse")
        input_browse.clicked.connect(self.browse_input)

        output_label = QLabel("Output")
        self.output_zone = QLineEdit()
        output_browse = QPushButton("Browse")
        output_browse.clicked.connect(self.browse_output)

        size_label = QLabel("Target size (MB)")
        self.size_spinbox = QSpinBox(minimum=1, maximum=300)
        self.size_spinbox.setValue(20)

        fps_label = QLabel("Higher framerate*")
        fps_label.setToolTip(
            "If checked, the output framerate will be maximum(60, <original framerate>).\nHigher framerate will decrease output quality."
        )
        self.fps_checkbox = QCheckBox()

        res_label = QLabel("Resolution*")
        res_label.setToolTip(
            "Default is 720p.\nHigher resolution will decrease output quality."
        )
        self.res_combobox = QComboBox()
        self.res_combobox.addItems(
            [f"{width}:{height}" for (width, height) in core.RESOLUTIONS]
        )
        self.res_combobox.setCurrentText("1280:720")

        compat_label = QLabel("Enable compatibility*")
        compat_label.setToolTip(
            "Enabling this option will use older, lower quality codecs (H.264 video and AAC audio).\nOnly use if you have compatibility issues."
        )
        self.compat_checkbox = QCheckBox()

        layout.addWidget(input_label, 0, 0)
        layout.addWidget(self.input_zone, 0, 1)
        layout.addWidget(input_browse, 0, 2)

        layout.addWidget(output_label, 1, 0)
        layout.addWidget(self.output_zone, 1, 1)
        layout.addWidget(output_browse, 1, 2)

        layout.addWidget(size_label, 2, 0)
        layout.addWidget(self.size_spinbox, 2, 1)

        layout.addWidget(fps_label, 3, 0)
        layout.addWidget(self.fps_checkbox, 3, 1)

        layout.addWidget(res_label, 4, 0)
        layout.addWidget(self.res_combobox, 4, 1)

        layout.addWidget(compat_label, 5, 0)
        layout.addWidget(self.compat_checkbox, 5, 1)

        body.addLayout(layout)

        run_button = QPushButton("Run")
        run_button.clicked.connect(self.run)

        test_button = QPushButton("Preview FFMPEG commands")
        test_button.clicked.connect(self.test)

        self.progressbar = QProgressBar()
        self.progressbar.setMaximum(100)

        body.addWidget(run_button)
        body.addWidget(test_button)
        body.addWidget(self.progressbar)

        # self.run_metric()

    def set_progressbar(self, value: int):
        self.progressbar.setValue(value)

    def browse_input(self):
        fileName = QFileDialog.getOpenFileName(
            self, "Open Video", "", "Video Files (*.mkv *.mp4 *.ivf *.webm)"
        )

        self.input_zone.setText(fileName[0])

    def browse_output(self):
        fileName = QFileDialog.getSaveFileName(
            self, "Open Video", "", "Video Files (*.mkv *.mp4 *.ivf *.webm)"
        )

        self.output_zone.setText(fileName[0])

    def check_overwrite(self):
        # add force_overwrite checkbox
        if (path := Path(self.output_zone.text())).exists() and path.is_file:
            print(1)
            messagebox = QMessageBox()
            messagebox.setIcon(QMessageBox.Icon.Warning)
            messagebox.setWindowTitle("Overwrite")
            messagebox.setText(
                "The output file already exists, are you sure you want to overwrite it?"
            )
            messagebox.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            print(2)
            button = messagebox.exec()
            print(3)

            return button == QMessageBox.StandardButton.Yes
        return True

    def run(self) -> None:
        """
        Checks if file overwrite, creates the work and runs it
        """
        allow_overwrite = self.check_overwrite()

        if not allow_overwrite:
            return

        work = core.Work(
            self.input_zone.text(),
            self.output_zone.text(),
            self.fps_checkbox.isChecked(),
            self.res_combobox.currentText(),
            self.size_spinbox.value(),
            compatibility=self.compat_checkbox.isChecked(),
            callback=self.set_progressbar,
        )
        work.run()

    def test(self):
        try:
            work = core.Work(
                self.input_zone.text(),
                self.output_zone.text(),
                self.fps_checkbox.isChecked(),
                self.res_combobox.currentText(),
                self.size_spinbox.value(),
                compatibility=self.compat_checkbox.isChecked(),
                callback=self.set_progressbar,
            )

            pass1, pass2 = work.make_ffmpeg_commands()

            messagebox = QMessageBox()
            messagebox.setIcon(QMessageBox.Icon.Information)
            messagebox.setWindowTitle("FFMPEG Commands")
            messagebox.setText(
                f"First pass FFMPEG command:\n{' '.join(pass1)}\n\nSecond pass FFMPEG command:\n{' '.join(pass2)}"
            )
            messagebox.exec()
        except Exception:
            return


app = QApplication()

window = MainWindow()
window.show()

app.exec()
