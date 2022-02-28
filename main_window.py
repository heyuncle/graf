import subprocess, sys, os, shutil, csv, ast
import xml.etree.ElementTree as et

from window import Ui_MainWindow
from tex_from_url import tex_from_url

from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
from latex2sympy2 import latex2sympy
from sympy.utilities.lambdify import lambdastr
from sympy import symbols
#from qt_material import apply_stylesheet, QtStyleTools
import qdarkstyle

# from error import Ui_Dialog as errorDialog # TODO - what was this for

class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, *args, **kwargs):
        self.objectID = 0
        super(MainWindow, self).__init__(*args, **kwargs)
        for i in sys.argv[1:]:
            self.open_mmtr(i)

        with open("objectProperties.csv","r") as f:
            self.objPropCsv = csv.reader(f)
            self.objProp = {i[0]:(i[1],i[4],i[5],i[6]) for i in self.objPropCsv} # manim name, shared, groupbox

        self.setWindowIcon(QIcon('icons/logo.ico'))
        self.setupUi(self)

        #self.setAttribute(Qt.WA_TranslucentBackground)
        #self.centralwidget.setStyleSheet("border-bottom-left-radius:20px; border-bottom-right-radius:20px;")
        #self.mainSplitter.setStyleSheet("border-bottom-left-radius:5px; border-bottom-right-radius:5px;") # rounded window corners lol

        # self.setStyleSheet(PyQt5_stylesheets.load_stylesheet_pyqt5(style="style_Dark")) # qrainbowtheme option
        # self.setStyleSheet(qdarktheme.load_stylesheet("dark")) # pyqtdarktheme option
        # apply_stylesheet(self, theme='dark_blue.xml')  # qmaterial
        self.setStyleSheet(qdarkstyle.load_stylesheet())
        
        self.lastSelection = []
        self.thisSelection = self.treeWidget.selectedItems()
        self.file_path = os.getcwd()

        self.loadVideoPlayer()
        self.show()
        self.retranslateUi(MainWindow)
        
        self.newObjButton.clicked.connect(lambda _: self.addObject(self.treeItem(self.testDuplicateName("MyObject", True),"Object","(None)")))
        self.newGroupButton.clicked.connect(lambda _: self.addObject(self.treeItem(self.testDuplicateName("New Group", False), "Group")))
        self.newSceneButton.clicked.connect(lambda _: self.addObject(self.treeItem(self.testDuplicateName("Scene " + str(1 + len(self.treeWidget.findItems("Scene", Qt.MatchContains, 0))), False), "Scene")))
        self.treeWidget.itemClicked.connect(lambda _: (self.updatePropPanel(), self.loadProp()))
        self.treeWidget.itemSelectionChanged.connect(self.saveLast)
        self.treeWidget.itemDoubleClicked.connect(self.edit)
        self.effectAddButton.clicked.connect(self.add_effect)
        self.animInComboBox.currentTextChanged.connect(self.toggle_grow)
        try:
            self.treeWidget.currentItemChanged.connect(self.testDuplicateName(self.thisSelection[0].text(0), True))
        except:
            print("failed")
        self.animList = ["Indicate", "Wiggle", "Move", "Move along path", "Transform", "Wave", "Flash", "Focus", "Circumscribe"]
        self.objTypeComboBox.currentTextChanged.connect(self.changeObjType)
        self.colorPushButton.clicked.connect(self.changeColor)
        self.urlPushButton.clicked.connect(self.loadToLaTeX)
        self.playPushButton.clicked.connect(self.playVideo)
        self.video_player.stateChanged.connect(self.changeMediaIcon)
        #self.updateObjPropButton.clicked.connect(self.saveProp)
        # self.addRowButton.clicked.connect(self.matrixTableWidget.insertRow(self.matrixTableWidget.rowCount()))
        # self.removeRowButton.clicked.connect(self.matrixTableWidget.removeRow(self.matrixTableWidget.rowCount()))
        # self.addColButton.clicked.connect(self.matrixTableWidget.insertColumn(self.matrixTableWidget.columnCount()))
        # self.remColButton.clicked.connect(self.matrixTableWidget.removeColumn(self.matrixTableWidget.columnCount()))
        self.actionOpen.triggered.connect(self.open_from_dir)
        self.actionSave.triggered.connect(self.save_mmtr)
        self.actionSave_as.triggered.connect(self.save_mmtr_as)
        #self.actionPreferences.triggered.connect(self.openPreferences)
        self.actionDelete.triggered.connect(self.delItem)
        self.actionMP.triggered.connect(lambda _: self.renderScene(False)) #TODO add other file types
        self.actionGenerate_Preview.triggered.connect(lambda _: self.renderScene(True))


        self.effectWidget.hide()
        self.mainObjWidget.hide()
        self.timeLineLayout = QtWidgets.QVBoxLayout(self)

        # Test project
        newScene = self.treeItem("Scene 1","Scene")
        self.treeWidget.addTopLevelItem(newScene)
        self.treeWidget.setCurrentItem(newScene)

        self.updatePropPanel()

    def loadVideoPlayer(self):
        self.video_frame = QVideoWidget(self.prevWidget)
        self.video_frame.setContentsMargins(10,10,10,10)
        self.verticalLayout_3.addWidget(self.video_frame)
        self.video_player = QMediaPlayer(flags=QMediaPlayer.VideoSurface)
        self.video_player.setVideoOutput(self.video_frame)
        self.video_player.setMedia(QMediaContent(QUrl.fromLocalFile("/Users/heyuncle/Desktop/test.mp4")))

    def playVideo(self):
        if self.video_player.state() == QMediaPlayer.PlayingState:
            self.video_player.pause()
        else:
            self.video_player.play()

    def changeMediaIcon(self):
        if self.video_player.state() == QMediaPlayer.PlayingState:
            self.playPushButton.setIcon(QIcon("icons/pause-button-light.png"))
        else:
            self.playPushButton.setIcon(QIcon("icons/play-button-light.png"))

    def loadToLaTeX(self):
        self.latexTextEdit.setPlainText(tex_from_url(self.urlLineEdit.text())[3:-3])

    def saveLast(self):
        self.lastSelection = self.thisSelection
        self.thisSelection = self.treeWidget.selectedItems()
        print("last: " + str(self.lastSelection))
        if not all(i in self.thisSelection for i in self.lastSelection):
            self.saveProp()

    def treeItem(self, name, type, subtype="", properties="{'duration':0.0}", animations="[]"):
        item = QTreeWidgetItem()
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        item.setText(0,self.testDuplicateName(name, False))
        item.setText(1,type)
        item.setText(2,subtype)
        item.setText(3,properties)
        item.setText(5,animations)
        if type == "Object":
            item.setText(4,str(self.objectID))
        item.setIcon(0,QIcon("icons/camera-solid-light.ico" if type=="Scene" else "icons/equation-light.ico" if type=="Object" else "icons/object-group-solid-light.ico"))
        return item

    def edit(self):
        item = self.treeWidget.currentItem()
        self.treeWidget.editItem(item)
        item.setText(0,self.testDuplicateName(item.text(0), True)) # TODO somehow wait until editing finished before doing this

    def changeObjType(self):
        newType = self.objTypeComboBox.currentText()
        default = self.objProp[newType][3] if newType != "(None)" else "{}"
        for i in self.treeWidget.selectedItems():
            i.setText(2,newType)
            i.setText(3,default)
        self.updatePropPanel()
        self.loadProp()

    def getObjID(self, name):
        if (name != "(None)"):
            return int(self.treeWidget.findItems(name, Qt.MatchFixedString | Qt.MatchRecursive, 0)[0].text(4))
        else:
            return None

    def loadProp(self):
        currentTab = self.tabWidget.currentIndex()
        if self.treeWidget.currentItem().text(3)=="":
            self.objTypeComboBox.setCurrentText("(None)")
            return
        prop = ast.literal_eval(self.treeWidget.currentItem().text(3))
        self.tabWidget.setCurrentIndex(0) # switch to properties tab
        for i in self.propScrollAreaWidget.findChildren(QtWidgets.QGroupBox):
            if i.isVisible():
                if i.objectName() == "objTypeGroupBox":
                    self.objTypeComboBox.setCurrentText(self.treeWidget.currentItem().text(2))
                if i.objectName() == "rectGroupBox":
                    self.rectHeightSpinBox.setValue(prop["height"])
                    self.rectWidthSpinBox.setValue(prop["width"])
                    self.xGridSpinBox.setValue(prop["grid_xstep"])
                    self.yGridSpinBox.setValue(prop["grid_ystep"])
                elif i.objectName() == "ulGroupBox":
                    try: # put in try loop incase object is deleted between saving and loading
                        self.ulObjComboBox.setCurrentText([i*(i.text(4) == str(prop["object"])) for i in (self.treeWidget.findItems("", Qt.MatchContains | Qt.MatchRecursive, 0)[0])][0].text(0))
                    except:
                        self.ulObjComboBox.setCurrentText("(None)")
                    self.ulBuffSpinBox.setValue(prop["buff"])
                elif i.objectName() == "arcGroupBox":
                    self.radiusSpinBox.setValue(prop["radius"])
                    self.stAngleSpinBox.setValue(prop["start_angle"])
                    self.angleSpinBox.setValue(prop["angle"])
                elif i.objectName() == "arrowGroupBox":
                    self.arStrokeSpinBox.setValue(prop["stroke_width"])
                    self.arBuffSpinBox.setValue(prop["buff"])
                elif i.objectName() == "braceGroupBox":
                    try:
                        self.braceObjSelectComboBox.setCurrentText([i*(i.text(4) == str(prop["object"])) for i in (self.treeWidget.findItems("", Qt.MatchContains | Qt.MatchRecursive, 0)[0])][0].text(0))
                    except:
                        self.braceObjSelectComboBox.setCurrentText("(None)")
                    self.bracePlainTextEdit.setPlainText(prop["text"])
                elif i.objectName() == "colorGroupBox":
                    try:
                        self.colorFrame.setStyleSheet("background-color: "+prop["color"])
                    except KeyError:
                        self.colorFrame.setStyleSheet("background-color: #ffffff")
                elif i.objectName() == "directionGroupBox":
                    try:
                        self.dirStartComboBox.setCurrentText(prop["start"])
                    except:
                        self.dirStartComboBox.setCurrentText("(None)")
                    try:
                        self.dirEndComboBox.setCurrentText(prop["start"])
                    except:
                        self.dirEndComboBox.setCurrentText("(None)")
                elif i.objectName() == "dotGroupBox":
                    self.coordLineEdit.setText(prop["point"])
                    self.widthSpinBox.setValue(prop["stroke_width"])
                    self.opacitySpinBox.setValue(int(100*prop["fill_opacity"]))
                elif i.objectName() == "functionGroupBox":
                    self.latexTextEdit.setPlainText(prop["function"])
                elif i.objectName() == "latexGroupBox":
                    self.latexSizeSpinBox.setValue(prop["font_size"])
                elif i.objectName() == "lineGroupBox":
                    self.startCorLineEdit.setText(prop["start"])
                    self.endCorLineEdit.setText(prop["end"])
                    self.lineThickSpinBox.setValue(prop["buff"])
                elif i.objectName() == "matrixGroupBox": # TODO: figure out what is going on with this
                    # j.setText(3,str(eval(j.text(3)) | {
                    #     "matrix": self.matrixTableWidget.items()
                    # }))
                    # for i in range(0, len(prop["matrix"])):
                    #     for k in range(0, len(prop["matrix"][i])):
                    #         self.matrixTableWidget.setItem(i, k, prop["matrix"][i][k])
                    pass
                elif i.objectName() == "numPlaneGroupBox":
                    self.numXMinSpinBox.setValue(prop["x_min"])
                    self.numXMaxSpinBox.setValue(prop["x_max"])
                    self.numYMinSpinBox.setValue(prop["y_min"])
                    self.numYMaxSpinBox.setValue(prop["y_max"])
                elif i.objectName() == "positionGroupBox":
                    self.xSpinBox.setValue(prop["x_shift"])
                    self.ySpinBox.setValue(prop["y_shift"])
                elif i.objectName() == "paramFuncGroupBox":
                    self.minTSpinBox.setValue(prop["t_start"])
                    self.maxTSpinBox.setValue(prop["t_end"])
                elif i.objectName() == "regPolyGroupBox":
                    self.regPolyVertSpinBox.setValue(prop["n"])
                elif i.objectName() == "surRectGroupBox":
                    try:
                        self.surrObjComboBox.setCurrentText(i*(i.text(4) == str(prop["object"])) for i in (self.treeWidget.findItems("", Qt.MatchContains | Qt.MatchRecursive, 0)[0]).text(0))
                    except:
                        self.surrObjComboBox.setCurrentText("(None)")
                    self.surrBuffSpinBox.setValue(prop["buff"])
                    self.surrRadiusSpinBox.setValue(prop["corner_radius"])
                elif i.objectName() == "textGroupBox":
                    self.textPlainTextEdit.setPlainText(prop["text"])
                    self.textSizeSpinBox.setValue(prop["font_size"])
                    self.textOpacitySpinBox.setValue(int(100*prop["fill_opacity"]))
                    self.italicCheckBox.setChecked(prop["slant"]=="ITALIC")
                    self.textBoldCheckBox.setChecked(prop["weight"]=="BOLD")
                    self.textStrokeSpinBox.setValue(prop["stroke_width"])
                elif i.objectName() == "polyGroupBox":
                    for i in prop["vertices"]:
                        self.polyVertListWidget.addItem(i)
                elif i.objectName() == "durationGroupBox":
                    self.durationSpinBox.setValue(prop["duration"])
        self.tabWidget.setCurrentIndex(1) # switch to animation tab
        for i in self.animScrollAreaContents.findChildren(QtWidgets.QGroupBox):
            if i.isVisible():
                if i.objectName() == "animInGroupBox":
                    self.animInComboBox.setCurrentText(prop["animIn"])
                elif i.objectName() == "animOutGroupBox":
                    self.animOutComboBox.setCurrentText(prop["animOut"])
                elif i.objectName() == "growGroupBox":
                    self.growOriginComboBox.currentText(prop["growConfig"])
        self.tabWidget.setCurrentIndex(currentTab) # switch to last tab

    def toggle_grow(self):
        if (self.animInComboBox.currentValue() == "Grow"):
            self.growGroupBox.show()
        else:
            self.growGroupBox.hide()

    def saveProp(self):
        currentTab = self.tabWidget.currentIndex()
        if ("Scene" or "Group") in [i.text(1) for i in self.lastSelection]:
            return
        self.tabWidget.setCurrentIndex(0) # switch to properties tab
        for i in self.propScrollAreaWidget.findChildren(QtWidgets.QGroupBox):
            if i.isVisible():
                if i.objectName() == "rectGroupBox":
                    for j in self.lastSelection:
                        j.setText(3,str(eval(j.text(3)) | {
                            "height": self.rectHeightSpinBox.value(),
                            "width": self.rectWidthSpinBox.value(),
                            "grid_xstep": self.xGridSpinBox.value(),
                            "grid_ystep": self.yGridSpinBox.value()
                        }))
                elif i.objectName() == "ulGroupBox":
                    for j in self.lastSelection:
                        j.setText(3,str(eval(j.text(3)) | {
                            "object": self.getObjID(self.ulObjComboBox.currentText()),
                            "buff": self.ulBuffSpinBox.value()
                        }))
                elif i.objectName() == "arcGroupBox":
                    for j in self.lastSelection:
                        j.setText(3,str(eval(j.text(3)) | {
                            "radius": self.radiusSpinBox.value(),
                            "start_angle": self.stAngleSpinBox.value(),
                            "angle": self.angleSpinBox.value()
                        }))
                elif i.objectName() == "arrowGroupBox":
                    for j in self.lastSelection:
                        j.setText(3,str(eval(j.text(3)) | {
                            "stroke_width": self.arStrokeSpinBox.value(),
                            "buff": self.arBuffSpinBox.value()
                        }))
                elif i.objectName() == "braceGroupBox":
                    for j in self.lastSelection:
                        j.setText(3,str(eval(j.text(3)) | {
                            "object": self.getObjID(self.braceObjSelectComboBox.currentText()),
                            "text": self.bracePlainTextEdit.toPlainText()
                        }))
                elif i.objectName() == "colorGroupBox":
                    for j in self.lastSelection:
                        j.setText(3,str(eval(j.text(3)) | {
                            "color": self.colorFrame.styleSheet().split()[-1]
                        }))
                elif i.objectName() == "directionGroupBox":
                    for j in self.lastSelection:
                        j.setText(3,str(eval(j.text(3)) | {
                            "start": (self.dirStartComboBox.currentText() if self.dirStartComboBox.currentText() != "(None)" else None),
                            "end": (self.dirEndComboBox.currentText() if self.dirEndComboBox.currentText() != "(None)" else None)
                        }))
                elif i.objectName() == "dotGroupBox":
                    for j in self.lastSelection:
                        j.setText(3,str(eval(j.text(3)) | {
                            "point": self.coordLineEdit.text(),
                            "stroke_width": self.widthSpinBox.value(),
                            "fill_opacity": self.opacitySpinBox.value()/100
                        }))
                elif i.objectName() == "functionGroupBox":
                    for j in self.lastSelection:
                        j.setText(3,str(eval(j.text(3)) | {
                            "function": self.latexTextEdit.toPlainText()
                        }))
                elif i.objectName() == "latexGroupBox":
                    for j in self.lastSelection:
                        j.setText(3,str(eval(j.text(3)) | {
                            "font_size": self.latexSizeSpinBox.value()
                        }))
                elif i.objectName() == "lineGroupBox":
                    for j in self.lastSelection:
                        j.setText(3,str(eval(j.text(3)) | {
                            "start": self.startCorLineEdit.text(),
                            "end": self.endCorLineEdit.text(),
                            "buff": self.lineThickSpinBox.value()
                        }))
                elif i.objectName() == "matrixGroupBox":
                    for j in self.lastSelection:
                        j.setText(3,str(eval(j.text(3)) | {
                            "matrix": self.matrixTableWidget.items()
                        }))
                elif i.objectName() == "numPlaneGroupBox":
                    for j in self.lastSelection:
                        j.setText(3,str(eval(j.text(3)) | {
                            "x_min": self.numXMinSpinBox.value(),
                            "x_max": self.numXMaxSpinBox.value(),
                            "y_min": self.numYMinSpinBox.value(),
                            "y_max": self.numYMaxSpinBox.value()
                        }))
                elif i.objectName() == "positionGroupBox":
                    for j in self.lastSelection:
                        j.setText(3,str(eval(j.text(3)) | {
                            "x_shift": self.xSpinBox.value(),
                            "y_shift": self.ySpinBox.value()
                        }))
                elif i.objectName() == "paramFuncGroupBox":
                    for j in self.lastSelection:
                        j.setText(3,str(eval(j.text(3)) | {
                            "t_start": self.minTSpinBox.value(),
                            "t_end": self.maxTSpinBox.value()
                        }))
                elif i.objectName() == "regPolyGroupBox":
                    for j in self.lastSelection:
                        j.setText(3,str(eval(j.text(3)) | {
                            "n": self.regPolyVertSpinBox.value()
                        }))
                elif i.objectName() == "surRectGroupBox":
                    for j in self.lastSelection:
                        j.setText(3,str(eval(j.text(3)) | {
                            "object": self.getObjID(self.surrObjComboBox.currentText()),
                            "buff": self.surrBuffSpinBox.value(),
                            "corner_radius": self.surrRadiusSpinBox.value()
                        }))
                elif i.objectName() == "textGroupBox":
                    for j in self.lastSelection:
                        j.setText(3,str(eval(j.text(3)) | {
                            "text": self.textPlainTextEdit.toPlainText(),
                            "font_size": self.textSizeSpinBox.value(),
                            "fill_opacity": self.textOpacitySpinBox.value()/100,
                            "slant": "ITALIC" if self.italicCheckBox.isChecked() else "NORMAL",
                            "weight": "BOLD" if self.textBoldCheckBox.isChecked() else "NORMAL",
                            "stroke_width": self.textStrokeSpinBox.value()
                        }))
                elif i.objectName() == "polyGroupBox":
                    for j in self.lastSelection:
                        j.setText(3,str(eval(j.text(3)) | {
                            "vertices": self.polyVertListWidget.items()
                        }))
                elif i.objectName() == "durationGroupBox":
                    for j in self.lastSelection:
                        j.setText(3, str(eval(j.text(3)) | {
                            "duration": self.durationSpinBox.value()
                        }))
        self.tabWidget.setCurrentIndex(1) # switch to animation tab
        for i in self.animScrollAreaContents.findChildren(QtWidgets.QGroupBox):
            if i.isVisible():
                if i.objectName() == "animInGroupBox":
                    for j in self.lastSelection:
                        j.setText(3, str(eval(j.text(3)) | {
                            "animIn": self.animInComboBox.currentText()
                        }))
                elif i.objectName() == "animOutGroupBox":
                    for j in self.lastSelection:
                        j.setText(3, str(eval(j.text(3)) | {
                            "animOut": self.animOutComboBox.currentText()
                        }))
                elif i.objectName() == "growGroupBox":
                    for j in self.lastSelection:
                        j.setText(3, str(eval(j.text(3)) | {
                            "growConfig": self.growOriginComboBox.currentText()
                        }))
        self.tabWidget.setCurrentIndex(currentTab) # switch back to last tab

    def changeColor(self):
        self.colorFrame.setStyleSheet("background-color: " + QtWidgets.QColorDialog.getColor().name())

    def setObjComboBoxes(self):
        objList = []
        for i in self.treeWidget.findItems("", Qt.MatchContains | Qt.MatchRecursive, 0):
            if i.text(1) == "Object" or i.text(1) == "Group":
                objList.append(i)
        selectedObjList = self.treeWidget.selectedItems()
        objList = [objVal.text(0) for objVal in objList if objVal not in selectedObjList]
        boxes = [self.ulObjComboBox, self.surrObjComboBox, self.relAlignComboBox, self.circumShapeComboBox, self.braceObjSelectComboBox, self.transformTargetComboBox, self.movePathTargetComboBox]
        objList.insert(0, "(None)")
        for j in boxes:
            j.clear()
            j.addItems(objList)

    def updatePropPanel(self):
        self.setObjComboBoxes()
        def showSharedProp(sharedProp):
            for i in [self.colorGroupBox,self.positionGroupBox]:
                i.show() if sharedProp % 2 == 1 else i.hide()
                sharedProp >>= 1
        def showUniqueProp(objType):
            for i in self.objProp[objType][2].split():
                exec("self."+i+".show()")
        def combineObjProp(objects):
            self.objTypeGroupBox.show()
            combinedProp = 3
            try:
                for i in objects:
                    combinedProp &= int(self.objProp[i.text(2)][1])
                showSharedProp(combinedProp)
                if len(list(set([i.text(2) for i in objects]))) == 1: #TODO make cleaner
                    showUniqueProp(self.treeWidget.currentItem().text(2))
            except:
                print("object not found error")
        def recursiveSelection(sel):
            new_sel = []
            for i in sel:
                if i.text(1)=="Object":
                    new_sel.append(i)
                elif i.text(1)=="Group":
                    new_sel += recursiveSelection([i.child(j) for j in range(i.childCount())])
            return new_sel


        for i in self.propScrollAreaWidget.findChildren(QtWidgets.QGroupBox) + self.animScrollAreaContents.findChildren(QtWidgets.QGroupBox):
            i.hide()
        
        if len(self.treeWidget.selectedItems()) == 1:
            if self.treeWidget.currentItem().text(1)=="Object":
                self.objTypeGroupBox.show()
                objType = self.treeWidget.currentItem().text(2)
                try:
                    showSharedProp(int(self.objProp[objType][1]))
                    showUniqueProp(objType)
                except:
                    print("object not found error")
            elif self.treeWidget.currentItem().text(1)=="Group":
                combineObjProp(recursiveSelection(self.treeWidget.selectedItems()))
            else:
                self.durationGroupBox.show()
        else:
            if len(list(set([i.text(1) for i in self.treeWidget.selectedItems()]))) == 1:
                if self.treeWidget.currentItem().text(1) in ["Object","Group"]:
                    combineObjProp(recursiveSelection(self.treeWidget.selectedItems()))
                else:
                    self.durationGroupBox.show()
            else:
                print("multiple object types selected")

    def testDuplicateName(self, name, exists):
        allNames = [i.text(0) for i in self.treeWidget.findItems("", Qt.MatchContains | Qt.MatchRecursive, 0)]
        tempName = name
        if (name in allNames and exists):
            allNames.remove(name) # search includes the object currently, remove 1 of it to test for duplicates
        if (name in allNames):
            i = 1
            while (tempName in allNames):
                tempName = name + " (" + str(i) + ")" # TODO this is super clean but it breaks past 10
                i += 1
            return tempName
        else:
            return name #TODO fix

    def open_mmtr(self, file):
        self.objList.clear()
        self.animList.clear()
        with open(file, "r+") as f:
            output = f.readlines()
            self.objSave = eval(output[0])
            self.animSave = eval(output[1])
            for i in self.objSave:
                try:
                    self.objList.addItem(display_names[i[0]] + " (" + i[2] + ")")
                except:
                    self.objList.addItem(i[0] + " (" + i[2] + ")")
            for i in self.animSave:
                try:
                    self.animList.addItem(display_names[i[0]])
                except:
                    self.animList.addItem(i[0])
        self.objNames = [i[2] for i in self.objSave]
        self.file_path = file.replace("\\", "/")
        self.setWindowTitle("graf - " + self.file_path.split("/")[-1])

    def addObject(self, object):
        if self.treeWidget.currentItem().text(1) in ["Group","Scene"]: #aiden was here
            self.objectID += 1
            if (object.text(1) == "Scene"):
                self.treeWidget.addTopLevelItem(object)
            else:
                self.treeWidget.currentItem().addChild(object)
                self.obj_timeline_add(object)
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText('Invalid selection')
            msg.setWindowTitle("Error")
            msg.exec_()

    def delItem(self):
        if (self.listWidget.selectedItems()) == 0: # if animations are not being edited
            for i in self.treeWidget.selectedItems():
                try:
                    i.parent().removeChild(i)
                except: pass
        else:
            for i in self.listWidget.selectedItems():
                try:
                    self.listWidget.takeItem(self.listWidget.row(i))
                    self.thisSelection.setText(5, str(eval(self.thisSelection.text(5).pop(self.listWidget.row(i)))))
                except: pass

    def convert_to_manim(self):
        with open("manim.py", "w+") as f:
            f.write("import math\nfrom manim import *\nclass MyScene(Scene):\n    def construct(self):\n")
            showList = []
            def clean(name):
                return name.replace(")","").replace("(","").replace(" ","_")
            def write_obj(i):
                param_string = ""
                objDict = eval(i.text(3))
                if i.text(2) == "(None)":
                    pass
                showList.append(i.text(0))
                if i.text(2) == "Coordinate Plane":
                    f.write("        "+clean(i.text(0))+"=NumberPlane(x_range=("+str(objDict["x_min"])+","+str(objDict["x_max"])+"),y_range=("+str(objDict["y_min"])+","+str(objDict["y_max"])+"),color='"+objDict["color"]+"')\n")
                else:
                    showList.append(i.text(0))
                    for prop,val in objDict.items():
                        if prop in ["x_shift", "y_shift", "duration", "animIn", "animOut", "growConfig"]:
                            pass
                        # elif prop == "show": #TODO show at start property
                        #     if val == True:
                        #         showList.append(i.text(0))
                        else:
                            try:
                                float(val)
                                param_string += prop + "=" + str(val) + ","
                            except:
                                # If number is not float or int (can't be converted to float)
                                if prop == "color":
                                    param_string += prop + "='" + val + "'," #TODO fix color saving
                                elif i.text(2) == "LaTeX":
                                    param_string += "r'" + val + "',"
                                elif i.text(2) == "Polygon":
                                    param_string += val + ","
                                elif i.text(2) == "Point Label":
                                    if prop == "text":
                                        param_string += "text=r'" + val + "',"
                                    else:
                                        param_string += prop + "=" + val + ","
                                elif i.text(2) == "Text":
                                    param_string += prop + "=r'" + val + "',"
                                elif i.text(2) == "Function Graph":
                                    param_string += lambdastr(symbols('x'), latex2sympy(val)) + ","
                                else:
                                    param_string += prop + "=" + val + ","
                    objLine = "        " + clean(i.text(0)) + "=" + self.objProp[i.text(2)][0] + "(" + param_string[:-1] + ")" #TODO ensure name has no spaces
                    try:
                        objLine += ".shift(RIGHT*" + str(objDict["x_shift"]) + "+UP*" + str(objDict["y_shift"]) + ")"
                    except:
                        pass
                    f.write(objLine + "\n")
            def recursive_load(obj):
                for i in obj:
                    if i.text(1) == "Group":
                        recur = recursive_load([self.treeWidget.currentItem().child(i) for i in range(self.treeWidget.currentItem().childCount())])
                        objLine = "        " + clean(i.text(0)) + "=Group(" + ",".join(clean(j) for j in recur) + ")"
                        try:
                            objLine += ".shift(RIGHT*" + str(eval(i.text(3))["x_shift"]) + "+UP*" + str(eval(i.text(3))["y_shift"]) + ")"
                        except:
                            pass
                    else:
                        write_obj(i)
            recursive_load([self.treeWidget.currentItem().child(i) for i in range(self.treeWidget.currentItem().childCount())])
            f.write("        self.add(" + ",".join([i for i in showList[::-1]]) + ")\n")
            # for i in self.animSave:
            #     param_string = ""
            #     if i[0] == "Move":
            #         f.write(
            #             "        self.play(" + i[1]["mobject"] +
            #             ".shift,RIGHT*" + str(i[1]["x"]) +
            #             "+UP*" + str(i[1]["y"]) + ")\n")
            #     else:
            #         for j in i[1].items():
            #             param_string += j[0] + "=" + str(j[1]) + ","
            #         f.write("        self.play(" + i[0] + "(" + param_string[:-1] + "))\n")
            f.write("        self.wait()")

    def renderScene(self, preview):
        # if not self.save_mmtr():
        #    return None
        file_path = QtWidgets.QFileDialog.getSaveFileName(filter="Video (*.mp4)")[0]
        if file_path == "": return
        os.chdir("/".join(file_path.split("/")[:-1]))
        self.convert_to_manim()
        subprocess.run("manim manim.py MyScene" + " -ql" if preview else "", shell=True)
        try:
            os.replace("./media/videos/manim/"+ ("480p15" if preview else "1080p60") +"/MyScene.mp4", "./"+file_path.split("/")[-1])
            shutil.rmtree('media')
            shutil.rmtree('__pycache__')
        except:
           pass
        if preview:
            self.video_player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
        os.chdir(self.file_path)

    def save_mmtr_as(self):
        try:
            self.file_path = QtWidgets.QFileDialog.getSaveFileName(filter="Manimator (*.mmtr)")[0]
            self.save_mmtr()
        except:
            return
        self.setWindowTitle("graf - " + self.file_path.split("/")[-1])

    def save_mmtr(self):
        if self.file_path == '':
            return self.save_mmtr_as()
        else:
            with open(self.file_path, "w+") as f:
                f.write(str(self.objSave) + "\n" + str(self.animSave))

    def open_from_dir(self):
        try:
            self.open_mmtr(QtWidgets.QFileDialog.getOpenFileName(filter="Manimator (*.mmtr)")[0])
        except:
            pass

    def load_effect(self):
        if len(self.listWidget.selectedItems()) == 1:
            anim = eval(self.thisSelection.text(5))[(self.listWidget.row(self.listWidget.selectedItems()[0]) - 1)]
            if (self.listWidget.selectedItems()[0].text() == "Indicate"):
                self.indScaleSpinBox.setValue(anim["scale_factor"])
                try:
                    self.indColorFrame.setStyleSheet("background-color: "+anim["color"])
                except KeyError:
                    self.indColorFrame.setStyleSheet("background-color: #ffffff")
                self.thisSelection.setText(5, str(anim))
            elif (self.listWidget.selectedItems()[0].text() == "Wiggle"):
                self.wiggleScaleSpinBox.setValue(anim["scale_factor"])
                self.wiggleAngleSpinBox.setValue(anim["angle"])
                self.wiggleNumSpinBox.setValue(anim["n"])
            elif (self.listWidget.selectedItems()[0].text() == "Move"):
                self.moveHorizSpinBox.setValue(anim["hor_shift"])
                self.moveVertSpinBox.setValue(anim["ver_shift"])
            elif (self.listWidget.selectedItems()[0].text() == "Move along path"):
                try:
                    self.movePathTargetComboBox.setCurrentText([i*(i.text(4) == str(anim["target"])) for i in (self.treeWidget.findItems("", Qt.MatchContains | Qt.MatchRecursive, 0)[0])][0].text(0))
                except:
                    self.movePathTargetComboBox.setCurrentText("(None)")
            elif (self.listWidget.selectedItems()[0].text() == "Transform"):
                try:
                    self.transformTargetComboBox.setCurrentText([i*(i.text(4) == str(anim["target"])) for i in (self.treeWidget.findItems("", Qt.MatchContains | Qt.MatchRecursive, 0)[0])][0].text(0))
                except:
                    self.transformTargetComboBox.setCurrentText("(None)")
            elif (self.listWidget.selectedItems()[0].text() == "Wave"):
                self.waveDirComboBox.setCurrentText(anim["direction"])
                self.waveAmpSpinBox.setValue(anim["amplitude"])
                self.waveRipSpinBox.setValue(anim["ripples"])
            elif (self.listWidget.selectedItems()[0].text() == "Flash"):
                self.flashLenSpinBox.setValue(anim["line_length"])
                self.flashNumLinesSpinBox.setValue(anim["n"])
                self.flashRadiusSpinBox.setValue(anim["radius"])
                self.flashStrokeSpinBox.setValue(anim["stroke_width"])
                try:
                    self.flashColorFrame.setStyleSheet("background-color: "+anim["color"])
                except KeyError:
                    self.flashColorFrame.setStyleSheet("background-color: #ffffff")
            elif (self.listWidget.selectedItems()[0].text() == "Focus"):
                self.focusOpacitySpinBox.setValue(anim["opacity"])
                try:
                    self.focusColorFrame.setStyleSheet("background-color: "+anim["color"])
                except KeyError:
                    self.focusColorFrame.setStyleSheet("background-color: #ffffff")
            elif (self.listWidget.selectedItems()[0].text() == "Circumscribe"):
                self.circumShapeComboBox.setCurrentText(anim["shape"])
                self.circumDistSpinBox.setValue(anim["distance"])
                self.circumFadeInCheckBox.setChecked(anim["fade_in"])
                self.circumFadeOutCheckBox.setChecked(anim["fade_out"])
                try:
                    self.circumColorFrame.setStyleSheet("background-color: "+anim["color"])
                except KeyError:
                    self.circumColorFrame.setStyleSheet("background-color: #ffffff")

    def save_effect(self): # "Indicate" "Wiggle" "Move" "Move along path" "Transform" "Wave" "Flash" "Focus" "Circumscribe"
        if len(self.listWidget.selectedItems()) == 1:
            anim = eval(self.thisSelection.text(5))
            if (self.listWidget.selectedItems()[0].text() == "Indicate"):
                anim[(self.listWidget.row(self.listWidget.selectedItems()[0]) - 1)] = {
                    "scale_factor" : self.indScaleSpinBox.value(),
                    "color" : self.indColorFrame.styleSheet().split()[-1]
                }
                self.thisSelection.setText(5, str(anim))
            elif (self.listWidget.selectedItems()[0].text() == "Wiggle"):
                anim[(self.listWidget.row(self.listWidget.selectedItems()[0]) - 1)] = {
                    "scale_factor" : self.wiggleScaleSpinBox.value(),
                    "angle" : self.wiggleAngleSpinBox.value(),
                    "n" : self.wiggleNumSpinBox.value()
                }
                self.thisSelection.setText(5, str(anim))
            elif (self.listWidget.selectedItems()[0].text() == "Move"):
                anim[(self.listWidget.row(self.listWidget.selectedItems()[0]) - 1)] = {
                    "hor_shift" : self.moveHorizSpinBox.value(),
                    "ver_shift" : self.moveVertSpinBox.value()
                }
                self.thisSelection.setText(5, str(anim))
            elif (self.listWidget.selectedItems()[0].text() == "Move along path"):
                anim[(self.listWidget.row(self.listWidget.selectedItems()[0]) - 1)] = {
                    "target" : self.getObjID(self.movePathTargetComboBox.currentText())
                }
                self.thisSelection.setText(5, str(anim))
            elif (self.listWidget.selectedItems()[0].text() == "Transform"):
                anim[(self.listWidget.row(self.listWidget.selectedItems()[0]) - 1)] = {
                    "target" : self.getObjID(self.transformTargetComboBox.currentText())
                }
                self.thisSelection.setText(5, str(anim))
            elif (self.listWidget.selectedItems()[0].text() == "Wave"):
                anim[(self.listWidget.row(self.listWidget.selectedItems()[0]) - 1)] = {
                    "direction" : self.waveDirComboBox.currentText(),
                    "amplitude" : self.waveAmpSpinBox.value(),
                    "ripples" : self.waveRipSpinBox.value()
                }
                self.thisSelection.setText(5, str(anim))
            elif (self.listWidget.selectedItems()[0].text() == "Flash"):
                anim[(self.listWidget.row(self.listWidget.selectedItems()[0]) - 1)] = {
                    "line_length" : self.flashLenSpinBox.value(),
                    "n" : self.flashNumLinesSpinBox.value(),
                    "radius" : self.flashRadiusSpinBox.value(),
                    "stroke_width" : self.flashStrokeSpinBox.value(),
                    "color" : self.flashColorFrame.styleSheet().split()[-1]
                }
                self.thisSelection.setText(5, str(anim))
            elif (self.listWidget.selectedItems()[0].text() == "Focus"):
                anim[(self.listWidget.row(self.listWidget.selectedItems()[0]) - 1)] = {
                    "opacity" : self.focusOpacitySpinBox.value(),
                    "color" : self.focusColorFrame.styleSheet().split()[-1]
                }
                self.thisSelection.setText(5, str(anim))
            elif (self.listWidget.selectedItems()[0].text() == "Circumscribe"):
                anim[(self.listWidget.row(self.listWidget.selectedItems()[0]) - 1)] = {
                    "shape" : self.circumShapeComboBox.currentText(),
                    "distance" : self.circumDistSpinBox.value(),
                    "color" : self.circumColorFrame.styleSheet().split()[-1],
                    "fade_in" : self.circumFadeInCheckBox.isChecked(),
                    "fade_out" : self.circumFadeOutCheckBox.isChecked()
                }
                self.thisSelection.setText(5, str(anim))

    def obj_timeline_add(self, object):
        if object in self.listWidget.findItems("", Qt.MatchContains):
            effectWidget = QtWidgets.QWidget(self.timeLineWidget)
            effectWidget.setObjectName(object.text())
            horizontalLayout_74 = QtWidgets.QHBoxLayout(effectWidget)
            horizontalLayout_74.setObjectName("horizontalLayout_74")
            widget = QtWidgets.QWidget(effectWidget)
            widget.setMaximumSize(QtCore.QSize(100, 16777215))
            widget.setObjectName("widget")
            horizontalLayout_77 = QtWidgets.QHBoxLayout(widget)
            horizontalLayout_77.setObjectName("horizontalLayout_77")
            effectNestLine = QtWidgets.QFrame(widget)
            effectNestLine.setFrameShape(QtWidgets.QFrame.VLine)
            effectNestLine.setFrameShadow(QtWidgets.QFrame.Sunken)
            effectNestLine.setObjectName("effectNestLine")
            horizontalLayout_77.addWidget(effectNestLine)
            effectLabel = QtWidgets.QLabel(widget)
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(effectLabel.sizePolicy().hasHeightForWidth())
            effectLabel.setSizePolicy(sizePolicy)
            effectLabel.setMaximumSize(QtCore.QSize(45, 16777215))
            effectLabel.setObjectName("effectLabel")
            horizontalLayout_77.addWidget(effectLabel)
            effectLine = QtWidgets.QFrame(widget)
            effectLine.setFrameShape(QtWidgets.QFrame.VLine)
            effectLine.setFrameShadow(QtWidgets.QFrame.Sunken)
            effectLine.setObjectName("effectLine")
            horizontalLayout_77.addWidget(effectLine)
            horizontalLayout_74.addWidget(widget)
            effectScrollBarWidget = QtWidgets.QScrollBar(effectWidget)
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(effectScrollBarWidget.sizePolicy().hasHeightForWidth())
            effectScrollBarWidget.setSizePolicy(sizePolicy)
            effectScrollBarWidget.setMaximum(100)
            effectScrollBarWidget.setPageStep(1)
            effectScrollBarWidget.setTracking(True)
            effectScrollBarWidget.setOrientation(QtCore.Qt.Horizontal)
            effectScrollBarWidget.setInvertedAppearance(False)
            effectScrollBarWidget.setInvertedControls(True)
            effectScrollBarWidget.setObjectName("effectScrollBarWidget")
            horizontalLayout_74.addWidget(effectScrollBarWidget)
            self.verticalLayout_17.addWidget(effectWidget)
        else:
            objWidget = QtWidgets.QWidget(self.timeLineWidget)
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(widget.sizePolicy().hasHeightForWidth())
            widget.setSizePolicy(sizePolicy)
            widget.setObjectName(object.text(0) + "mainObjWidget")
            horizontalLayout_42 = QtWidgets.QHBoxLayout(widget)
            horizontalLayout_42.setObjectName("horizontalLayout_42")
            objTitleWidget = QtWidgets.QWidget(widget)
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(objWidget.sizePolicy().hasHeightForWidth())
            objTitleWidget.setSizePolicy(sizePolicy)
            objTitleWidget.setMaximumSize(QtCore.QSize(100, 16777215))
            objTitleWidget.setObjectName(object.text(0) + "TitleWidget")
            horizontalLayout_76 = QtWidgets.QHBoxLayout(objTitleWidget)
            horizontalLayout_76.setObjectName("horizontalLayout_76")
            mainObjLabel = QtWidgets.QLabel(objTitleWidget)
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(mainObjLabel.sizePolicy().hasHeightForWidth())
            mainObjLabel.setSizePolicy(sizePolicy)
            mainObjLabel.setObjectName(object.text(0))
            horizontalLayout_76.addWidget(mainObjLabel)
            mainObjLine = QtWidgets.QFrame(objTitleWidget)
            mainObjLine.setFrameShape(QtWidgets.QFrame.VLine)
            mainObjLine.setFrameShadow(QtWidgets.QFrame.Sunken)
            mainObjLine.setObjectName(object.text(0) + "Line")
            horizontalLayout_76.addWidget(mainObjLine)
            horizontalLayout_42.addWidget(objTitleWidget)
            mainObjScrollBar = QtWidgets.QScrollBar(widget)
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(mainObjScrollBar.sizePolicy().hasHeightForWidth())
            mainObjScrollBar.setSizePolicy(sizePolicy)
            mainObjScrollBar.setMaximum(100)
            mainObjScrollBar.setPageStep(1)
            mainObjScrollBar.setTracking(True)
            mainObjScrollBar.setOrientation(QtCore.Qt.Horizontal)
            mainObjScrollBar.setInvertedAppearance(False)
            mainObjScrollBar.setInvertedControls(True)
            mainObjScrollBar.setObjectName(object.text(0) + "ScrollBar")
            horizontalLayout_42.addWidget(mainObjScrollBar)
        self.verticalLayout_17.addWidget(widget)

    def add_effect(self):
        if (self.effectComboBox.currentText() == "(None)"):
            pass
        else:
            self.listWidget.addItem(self.effectComboBox.currentText())
            self.thisSelection.setText(5, str(eval(self.thisSelection.text(5)).append({})))
            self.obj_timeline_add() # get the last added item here. not sure how with duplicate names

    def get_scroll_length(self):
        while self.thisSelection.parent():
            scene = self.thisSelection.parent()
        sceneLength = eval(scene.text(3))["duration"] # get duration of scene
        defaultEffectLength = 1.0 / sceneLength #DEFAULT_ANIMATION_RUN_TIME is 1.0s 
        objList = [(i*(i.text(1) == "Object")) for i in self.treeWidget.findItems("", Qt.MatchContains | Qt.MatchRecursive, 0)]
        for i in range(0, len(objList)): # get all objects, get their lengths
            objList[i] = (objList[i] / sceneLength)*self.fullVideoPreviewSlider.frameGeometry().width() # get length of each object's scrollbar
        self.fullVideoPreviewSlider.setMaximum(4*sceneLength) # smoother movement



    def get_start_times(self, scrollWidget):
        startTime = scrollWidget.value() # time in seconds