import importlib.metadata
import os
import sys
from pathlib import Path

from PySide6.QtCore import Property, QObject, QUrl, Signal, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuick import QQuickView
from PySide6.QtQuickControls2 import QQuickStyle


class FileModel(QObject):
    def __init__(self):
        QObject.__init__(self)
        self._path = ""

    def get_path(self) -> str:
        print(f"FileModel::get_path: {self._path}")
        return self._path

    @Slot(str)
    def dbg(self, s: str):
        print(f"FileModel::dbg({s})")

    def set_path(self, path: str):
        path = path.removeprefix("file:///")
        print(f"FileModel::set_path: {self._path} -> {path}")
        if self._path != path:
            self._path = path
            self.path_changed.emit()

    path_changed = Signal()
    path = Property(str, get_path, set_path, notify=path_changed)  # type: ignore

    @Slot(str)
    def set(self, path: str):
        self.path = path


class ListFiles(QObject):
    def __init__(self) -> None:
        QObject.__init__(self)
        self._files: list[str] = []

    def get_files(self) -> list[str]:
        return self._files

    def set_files(self, files: list[str]):
        if self._files != files:
            self._files = files
            self.files_changed.emit()

    files_changed = Signal()
    files = Property(list, get_files, set_files, notify=files_changed)  # type: ignore

    @Slot(str)
    def from_path(self, path: str):
        self.files = os.listdir(path.removeprefix("file:///"))
        print(self.files)


QML = None
with open(Path(__file__).parent / "view.qml") as file:
    QML = file.read()  # type: ignore
    version = importlib.metadata.metadata("raschel")["version"]
    if not version:
        raise ValueError("Version string empty.")
    window_title = f"raschel - {version}"
    QML = QML.replace("$RASCHEL_WINDOW_TITLE", window_title)  # type: ignore


if __name__ == "__main__":
    QQuickStyle.setStyle("Fusion")

    app = QGuiApplication(sys.argv)

    view = QQuickView()
    view.setTitle(window_title)
    qml_file = os.fspath(Path(__file__).resolve().parent / "view.qml")
    ctx = view.rootContext()

    folderModel = FileModel()
    listFiles = ListFiles()
    ctx.setContextProperty("fileModel", folderModel)
    ctx.setContextProperty("listFiles", listFiles)
    view.setSource(QUrl.fromLocalFile(qml_file))
    if view.status() == QQuickView.Error:  # type: ignore
        sys.exit(-1)

    view.show()
    res = app.exec()
    # Deleting the view before it goes out of scope is required to make sure all child QML instances
    # are destroyed in the correct order.
    del view
    sys.exit(res)
