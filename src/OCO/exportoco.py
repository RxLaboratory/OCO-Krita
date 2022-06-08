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

import os, json
import krita # pylint: disable=import-error
from PyQt5.QtWidgets import (QMessageBox, QProgressDialog)
from PyQt5.QtCore import (Qt, QRect)
from .dukrif import (DuKRIF_utils, DuKRIF_animation, DuKRIF_json, DuKRIF_io, DuKRIF_nodes) # pylint: disable=import-error
from .ocodialog import OCODialog
from .ocopy import oco

KRITA = krita.Krita.instance()

class OCOExporter(object):

    def __init__(self):

        self.__documentsList = []
        # Store Animation info whem exporting
        self.__docInfo = {}
        # Store Export dir
        self.__exportDir = ''

        self.__kWindow = KRITA.activeWindow()
        if self.__kWindow:
            self.__kWindow = self.__kWindow.qwindow()

        self.__dialog = OCODialog()
        self.exportPath = ""
        self.exportDir = ""
        self.exportReferenceLayers = True
        self.exportInvisibleLayers = False
        self.cropLayers = False
        self.width = 1920
        self.height = 1080

    def initialize(self):
        # Check if there's an active document
        document = KRITA.activeDocument()

        if not document:
            QMessageBox.information(self.__kWindow, "No active document", "You must have an active document to export it to OCO.\nPlease, open a document first.") 
            return
        
        # Set default path next to doc
        dir = os.path.dirname(document.fileName())
        self.__dialog.setPath(dir)
        self.__dialog.setResolution(document.width(), document.height())

        ok = self.__dialog.exec_()
        if not ok:
            return

        self.exportPath = self.__dialog.path()
        self.exportReferenceLayers = self.__dialog.exportReferenceLayers()
        self.exportInvisibleLayers = self.__dialog.exportInvisibleLayers()
        self.cropLayers = self.__dialog.cropLayers()
        self.width = self.__dialog.width()
        self.height = self.__dialog.height()

        # Export !

        self.export(document)

        QMessageBox.information(self.__kWindow, "Finished", "Export to OCO completed.") 

    def export(self, document):
        Application.setBatchmode(True) # pylint: disable=undefined-variable

        # Let's duplicate the document first
        document = document.clone()

        document.setBatchmode(True)
        documentName = document.fileName() if document.fileName() else 'Untitled'  # noqa: E501
        fileName, extension = os.path.splitext(os.path.basename(documentName)) # pylint: disable=unused-variable
        
        self.exportDir = fileName + '.oco'
        exportDir = os.path.join(self.exportPath, fileName + '.oco')
        self.mkdir(exportDir)

        self.progressdialog = QProgressDialog("Exporting cut-out asset...", "Cancel", 0, 100)
        self.progressdialog.setWindowModality(Qt.WindowModality.WindowModal)

        # Collect doc info
        self.__docinfo = DuKRIF_json.getDocInfo(document)
        self.__docinfo['ocoVersion'] = oco.VERSION
        documentDir = os.path.join(exportDir, self.__docinfo['name'])
        self.mkdir(documentDir)

        nodes = self.exportLayers(
                document,
                document.rootNode(),
                #self.formatsComboBox.currentText(),
                'png',
                documentDir
            )
        self.__docinfo['layers'] = nodes

        # Write doc info
        infoFile = open( os.path.join(exportDir, fileName) + '.oco',  "w")
        infoFile.write( json.dumps(self.__docinfo, indent=4) )
        infoFile.close()

        self.progressdialog.close()

        # close document
        document.close()
        Application.setBatchmode(False) # pylint: disable=undefined-variable
        document.setBatchmode(False)

        print("Finished exporting OCO to " + exportDir)

    def mkdir(self, directory):
        if (os.path.exists(directory)
                and os.path.isdir(directory)):
            return

        try:
            os.makedirs(directory)
        except OSError as e:
            raise e

    def exportLayers(self, document, parentNode, fileFormat, parentDir):
        """ This method get all sub-nodes from the current node and export them in
            the defined format."""

        nodes = []

        for i, node in enumerate(parentNode.childNodes()):

            if (self.progressdialog.wasCanceled()):
                break

            newDir = ''
            nodeName = node.name().strip().replace('/','-').replace('*', ' ')

            # ignore filters
            if 'filter' in node.type():
                continue
            # ignore invisible
            if not self.exportInvisibleLayers and not node.visible():
                continue
            # ignore reference
            if not self.exportReferenceLayers and "_reference_" in nodeName:
                continue
            # ignore _ignore_
            if "_ignore_" in nodeName:
                continue

            merge = "_merge_" in nodeName

            if merge:
                DuKRIF_nodes.disableIgnoreNodes(node)
                node = DuKRIF_nodes.flattenNode(document, node, i, parentNode)

            nodeInfo = DuKRIF_json.getNodeInfo(document, node, useDocumentSize=(not self.cropLayers))
            nodeInfo['fileType'] = fileFormat
            nodeInfo['reference'] = "_reference_" in nodeName
            if not self.cropLayers:
                nodeInfo['width'] = document.width()
                nodeInfo['height'] = document.height()
                nodeInfo['position'] = [ document.width() / 2, document.height() / 2 ]

            # translate blending mode to OCA
            if nodeInfo['blendingMode'] in oco.OCOBlendingModes:
                nodeInfo['blendingMode'] = oco.OCOBlendingModes[nodeInfo['blendingMode']]
            else:
                nodeInfo['blendingMode'] = 'normal'

            # if it's a group
            if node.type() == 'grouplayer':
                newDir = os.path.join(parentDir, nodeName)
                self.mkdir(newDir)
            # if not a group
            else:
                self.exportNode(document, node, nodeInfo, fileFormat, parentDir)
            
            # if there are children and not merged, export them
            if node.childNodes() and not merge:
                childNodes = self.exportLayers(document, node, fileFormat, newDir)
                nodeInfo['childLayers'] = childNodes

            nodes.append(nodeInfo)

        return nodes

    def exportNode(self, document, node, nodeInfo, fileFormat, parentDir):
        nodeName = node.name().strip().replace('/','-').replace('*', ' ')

        self.progressdialog.setLabelText(i18n("Exporting") + " " + nodeName) # pylint: disable=undefined-variable

        _fileFormat = fileFormat
        if '[jpeg]' in nodeName:
            _fileFormat = 'jpeg'
        elif '[png]' in nodeName:
            _fileFormat = 'png'
        elif '[exr]' in nodeName:
            _fileFormat = 'exr'

        frame = self.__docinfo['startTime']

        if node.animated() or node.type() == 'grouplayer':
            nodeDir = os.path.join(parentDir, nodeName)
            prevFrameNumber = -1
            self.mkdir(nodeDir)
            while frame <= self.__docinfo['endTime']:
                self.progressdialog.setValue(frame)
                if (self.progressdialog.wasCanceled()):
                    break
                if DuKRIF_animation.hasKeyframeAtTime(node, frame):
                    frameInfo = self.exportNodeFrame(document, node, _fileFormat, frame, nodeDir)
                    if prevFrameNumber >= 0:
                        nodeInfo['frames'][-1]['duration'] = frame - prevFrameNumber
                    nodeInfo['frames'].append(frameInfo)
                    prevFrameNumber = frame
                frame = frame + 1

            # set the last frame duration
            if len(nodeInfo['frames']) > 0:
                f = nodeInfo['frames'][-1]
                f['duration'] = document.fullClipRangeEndTime() - f['frameNumber']

        else:
            frameInfo = self.exportNodeFrame(document, node, _fileFormat, frame, parentDir)
            frameInfo['duration'] = document.playBackEndTime() - document.playBackStartTime()
            nodeInfo['frames'].append(frameInfo)
            
    def exportNodeFrame(self, document, node, fileFormat, frameNumber, parentDir):

        DuKRIF_animation.setCurrentFrame(document, frameNumber)

        if node.bounds().width() == 0:
            frameInfo = DuKRIF_json.createKeyframeInfo("_blank", "", frameNumber)
            return frameInfo

        nodeName = node.name().strip().replace('/','-').replace('*', ' ')
        imageName = '{0}_{1}'.format( nodeName, DuKRIF_utils.intToStr(frameNumber))
        imagePath = '{0}/{1}.{2}'.format( parentDir, imageName, fileFormat)
        imageFileName = imagePath

        if self.cropLayers:
            bounds = QRect()
        else:
            bounds = QRect(0, 0, self.width, self.height)

        opacity = node.opacity()
        node.setOpacity(255)

        node.save(imageFileName, 1, 1, krita.InfoObject(), bounds)

        node.setOpacity(opacity)
        
        # TODO check if the file was correctly exported. The Node.save() method always reports False :/

        frameInfo = DuKRIF_json.getKeyframeInfo(document, node, frameNumber, useDocumentSize=(not self.cropLayers))
        frameInfo['fileName'] = self.getRelativePath(imagePath)

        return frameInfo

    def getRelativePath(self, path):
        return path.replace(os.path.join(self.exportPath, self.exportDir) + '/', '')

