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

import krita # pylint: disable=import-error
from .exportoco import OCOExporter

class OCOExport(krita.Extension):

    def __init__(self, parent):
        super(OCOExport, self).__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        action = window.createAction("oco_export", i18n("OCO Export")) # pylint: disable=undefined-variable
        action.setToolTip(i18n("Export cut-out assets from a document.")) # pylint: disable=undefined-variable
        action.triggered.connect(self.initialize)

    def initialize(self):
        exporter = OCOExporter()
        exporter.initialize()
