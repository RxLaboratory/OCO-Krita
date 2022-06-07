# OCO Exporter for Krita
# Copyright (c) 2020-2022 - Nicolas Dufresne, RxLaboratory and contributors
# This script is licensed under the GNU General Public License v3
# https://rainboxlab.org
# 
# OCO was made using "Export Layers" for Krita, which is licensed CC 0 1.0  - public domain
#
# This file is part of OCO.
#   OCO is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    OCO is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with OCO. If not, see <http://www.gnu.org/licenses/>.

import os
from PyQt5.QtWidgets import ( # pylint: disable=no-name-in-module #pylint: disable=import-error
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QPushButton,
    QLineEdit,
    QCheckBox,
    QDialogButtonBox,
    QFrame,
    QFileDialog
)
from PyQt5.QtCore import (
    Qt,
    ) 

class OCODialog(QDialog):

    def __init__(self, parent=None):
        super(OCODialog, self).__init__(parent)

        self.__version = "0.0.1"

        mainLayout = QVBoxLayout(self)
        formLayout = QFormLayout()
        directorySelectorLayout = QHBoxLayout()
        optionsLayout = QVBoxLayout()

        self.__refreshButton = QPushButton(i18n("Refresh")) # pylint: disable=undefined-variable
        self.__directoryTextField = QLineEdit()
        self.__directoryDialogButton = QPushButton(i18n("...")) # pylint: disable=undefined-variable
        self.__exportReferenceCheckbox = QCheckBox(i18n("Export \"_reference_\" layers")) # pylint: disable=undefined-variable
        self.__exportInvisibleLayersCheckBox = QCheckBox(i18n("Export invisible layers")) # pylint: disable=undefined-variable

        self.__buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel )

        self.__directoryTextField.setReadOnly(True)
        self.__directoryDialogButton.clicked.connect(self.__selectDir)
        self.__refreshButton.clicked.connect(self.__refreshButtonClicked)
        self.__buttonBox.accepted.connect(self.accept)
        self.__buttonBox.rejected.connect(self.reject)

        directorySelectorLayout.addWidget(self.__directoryTextField)
        directorySelectorLayout.addWidget(self.__directoryDialogButton)

        optionsLayout.addWidget(self.__exportReferenceCheckbox)
        optionsLayout.addWidget(self.__exportInvisibleLayersCheckBox)
        self.__exportReferenceCheckbox.setChecked(True)

        formLayout.addRow(i18n("Destination:"), directorySelectorLayout) # pylint: disable=undefined-variable
        formLayout.addRow(i18n("Export options:"), optionsLayout) # pylint: disable=undefined-variable
        #self.formLayout.addRow(
        #    i18n("Images extensions:"), self.formatsComboBox)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        mainLayout.addLayout(formLayout)
        mainLayout.addWidget(line)
        mainLayout.addWidget(self.__buttonBox)

        self.resize(500, 100)
        self.setWindowTitle(i18n("OCO Export ") + " v" + self.__version) # pylint: disable=undefined-variable
        self.setSizeGripEnabled(True)

    def setPath(self, path):
        if os.path.isdir(path):
            self.__directoryTextField.setText(path)
        else:
            self.__directoryTextField.setText(os.path.expanduser("~"))

    def path(self):
        return self.__directoryTextField.text()

    def exportReferenceLayers(self):
        return self.__exportReferenceCheckbox.isChecked()

    def exportInvisibleLayers(self):
        return self.__exportInvisibleLayersCheckBox.isChecked()

    def __selectDir(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            i18n("Select a Folder"), # pylint: disable=undefined-variable
            self.__directoryTextField.text(),
            QFileDialog.ShowDirsOnly)
        if directory:
            self.__directoryTextField.setText(directory)

    def __refreshButtonClicked(self):
        pass
