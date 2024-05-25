import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt.labs.platform 1.1

Rectangle {
    id: main_window
    width: 500
    height: 200
    visible: true
    // title: "$RASCHEL_WINDOW_TITLE"
    ColumnLayout {
        id: columnLayout
        anchors.fill: parent

        anchors.margins: 0, 40, 0, 40

        RowLayout {
            Layout.alignment: Qt.AlignHCenter
            Text {
                id: text
                text: "Path"
            }
            TextField {
                id: file_path
                Layout.fillWidth: true
                text: fileModel.path
                readOnly: true
            }
            Button {
                text: "Open"
                onClicked: folderDialog.open()
            }
            FolderDialog {
                id: folderDialog
                currentFolder: fileModel.path
                folder: StandardPaths.writableLocation(StandardPaths.DocumentsLocation)
                onAccepted: {
                    fileModel.dbg(folderDialog.folder)
                    file_path.text = folderDialog.folder;
                    listFiles.from_path(folderDialog.folder)
                }
            }
        }
        RowLayout {
            ListView {
                id: fileList
            }
        }
    }
}
