import subprocess, sys, os, shutil, csv, ast
import xml.etree.ElementTree as et

from window import Ui_MainWindow
from preferences import Ui_Dialog

from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from qt_material import apply_stylesheet, QtStyleTools

# from error import Ui_Dialog as errorDialog # TODO - what was this for

class MainWindow(QMainWindow, Ui_MainWindow, QtStyleTools):
    file_path = ''

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
        self.apply_stylesheet(self, theme='dark_blue.xml')  # qmaterial
        
        self.lastSelection = []
        self.thisSelection = self.treeWidget.selectedItems()

        self.show()
        self.retranslateUi(MainWindow)
        
        self.newObjButton.clicked.connect(lambda _: self.addObject(self.treeItem("MyObject","Object","(None)")))
        #self.treeWidget.itemClicked.connect(lambda _: (self.saveProp(), self.updatePropPanel(), self.loadProp()))
        self.treeWidget.itemClicked.connect(self.saveAndLoad)
        self.treeWidget.itemSelectionChanged.connect(self.updateLastSelection)
        self.treeWidget.itemDoubleClicked.connect(self.edit)
        self.objTypeComboBox.currentTextChanged.connect(self.changeObjType)
        self.colorPushButton.clicked.connect(self.changeColor)
        #self.updateObjPropButton.clicked.connect(self.saveProp)
        # self.addRowButton.clicked.connect(self.matrixTableWidget.insertRow(self.matrixTableWidget.rowCount()))
        # self.removeRowButton.clicked.connect(self.matrixTableWidget.removeRow(self.matrixTableWidget.rowCount()))
        # self.addColButton.clicked.connect(self.matrixTableWidget.insertColumn(self.matrixTableWidget.columnCount()))
        # self.remColButton.clicked.connect(self.matrixTableWidget.removeColumn(self.matrixTableWidget.columnCount()))

        self.actionOpen.triggered.connect(self.open_from_dir)
        self.actionSave.triggered.connect(self.save_mmtr)
        self.actionSave_as.triggered.connect(self.save_mmtr_as)
        self.actionPreferences.triggered.connect(self.openPreferences)
        self.actionDelete.triggered.connect(self.delItem)
        self.actionMP.triggered.connect(self.renderScene) #TODO add other file types

        # Test project
        newScene = self.treeItem("Scene 1","Scene")
        self.treeWidget.addTopLevelItem(newScene)
        self.treeWidget.setCurrentItem(newScene)
        #self.addObject(self.treeItem("MyObject","Object","Rectangle","{'x_shift':0.0,'y_shift':0.0,'height':1.0,'width':1.0,'grid_xstep':1.0,'grid_ystep':1.0}"))

        self.updatePropPanel()

    def saveAndLoad(self):
        self.saveProp()
        self.updatePropPanel()
        self.loadProp()

    def updateLastSelection(self):
        self.lastSelection = self.thisSelection
        self.thisSelection = self.treeWidget.selectedItems()
        print(self.lastSelection)
        if self.thisSelection == []:
            self.saveProp()

    def treeItem(self, name, type, subtype="", properties=""):
        item = QTreeWidgetItem()
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        item.setText(0,self.testDuplicateName(name, False))
        item.setText(1,type)
        item.setText(2,subtype)
        item.setText(3,properties)
        if type == "Object":
            item.setText(4,str(self.objectID))
        item.setIcon(0,QIcon("icons/camera-solid.ico" if type=="Scene" else "icons/equation.ico" if type=="Object" else "icons/object-group-solid.ico"))
        return item

    def edit(self):
        item = self.treeWidget.currentItem()
        self.treeWidget.editItem(item)
        item.setText(0,self.testDuplicateName(item.text(0), True)) # TODO somehow wait until editing finished before doing this

    def changeObjType(self):
        newType = self.objTypeComboBox.currentText()
        default = self.objProp[newType][3] if newType != "(None)" else ""
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
        if self.treeWidget.currentItem().text(3)=="":
            self.objTypeComboBox.setCurrentText("(None)")
            return
        prop = ast.literal_eval(self.treeWidget.currentItem().text(3))
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
                        self.ulObjComboBox.setCurrentText(self.treeWidget.findItems(str(prop["object"]), Qt.MatchFixedString | Qt.MatchRecursive, 4)[0].text(0))
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
                        self.braceObjSelectComboBox.setCurrentText(self.treeWidget.findItems(str(prop["object"]), Qt.MatchFixedString | Qt.MatchRecursive, 4)[0].text(0))
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
                elif i.objectName() == "functionGroupBox": # TODO: load image back in, maybe save the filepath?
                    # j.setText(3,str(eval(j.text(3)) | {
                    #     "function": None
                    # }))
                    pass
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
                    self.numXLengthSpinBox.setValue(prop["x_length"])
                    self.numYLengthSpinBox.setValue(prop["y_length"])
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
                        self.surrObjComboBox.setCurrentText(self.treeWidget.findItems(str(prop["object"]), Qt.MatchFixedString | Qt.MatchRecursive, 4)[0].text(0))
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

    def saveProp(self):
        if ("Scene" or "Group") in [i.text(1) for i in self.lastSelection]:
            return
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
                            "function": None
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
                            "y_max": self.numYMaxSpinBox.value(),
                            "x_length": self.numXLengthSpinBox.value(),
                            "y_length": self.numYLengthSpinBox.value()
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

    def changeColor(self):
        self.colorFrame.setStyleSheet("background-color: " + QtWidgets.QColorDialog.getColor().name())

    def setObjComboBoxes(self):
        objList = self.treeWidget.findItems("Object", Qt.MatchFixedString | Qt.MatchRecursive, 1)
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

        for i in self.propScrollAreaWidget.findChildren(QtWidgets.QGroupBox):
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
            else:
                pass # TODO Single-select properties for scene, split for group
        else:
            if len(list(dict.fromkeys([i.text(1) for i in self.treeWidget.selectedItems()]))) == 1:
                if self.treeWidget.currentItem().text(1)=="Object":
                        self.objTypeGroupBox.show()
                        combinedProp = 3
                        try:
                            for i in self.treeWidget.selectedItems():
                                combinedProp &= int(self.objProp[i.text(2)][1])
                            showSharedProp(combinedProp)
                            if len(list(dict.fromkeys([i.text(2) for i in self.treeWidget.selectedItems()]))) == 1: #TODO make cleaner
                                showUniqueProp(self.treeWidget.currentItem().text(2))
                        except:
                            print("object not found error")
                else:
                    pass # TODO Multi-select properties for scene, split for group
            else:
                print("multiple object types selected")

    def testDuplicateName(self, name, exists):
        allNames = [i.text(0) for i in self.treeWidget.findItems("Object", Qt.MatchFixedString | Qt.MatchRecursive, 1)] + [i.text(0) for i in self.treeWidget.findItems("Group", Qt.MatchFixedString | Qt.MatchRecursive, 1)] + [i.text(0) for i in self.treeWidget.findItems("Scene", Qt.MatchFixedString | Qt.MatchRecursive, 1)]
        if (name in allNames and exists):
            allNames.remove(name) # search includes the object currently, remove 1 of it to test for duplicates
        if (name in allNames):
            tempName = name + " (1)"
            while (tempName in allNames):
                tempName = name + " (" + str(int(tempName[-2]) + 1) + ")" # TODO this is super clean but it breaks past 10
            print(tempName)
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
        self.setWindowTitle("Manimator - " + self.file_path.split("/")[-1])

    def openPreferences(self):
        def submitPreferences():
            #apply_stylesheet()
            pass
        self.prefWindow = QtWidgets.QDialog()
        self.preferences = Ui_Dialog()
        self.preferences.setupUi(self.prefWindow)
        self.prefWindow.setStyleSheet(self.styleSheet())
        self.prefWindow.show()
        if self.prefWindow.comboBox.currentText()=="Red":
            self.apply_stylesheet(self, "dark_red.xml")

    def addObject(self, object):
        if self.treeWidget.currentItem().text(1) in ["Group","Scene"]:
            self.objectID += 1
            self.treeWidget.currentItem().addChild(object)
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText('More information')
            msg.setWindowTitle("Error")
            msg.exec_()

    def delItem(self):
        for i in self.treeWidget.selectedItems():
            try:
                i.parent().removeChild(i)
            except: pass


    def convert_to_manim(self):
        with open("manim.py", "w+") as f:
            f.write("from manim import *\nclass MyScene(Scene):\n    def construct(self):\n")
            showList = []
            children = [self.treeWidget.currentItem().child(i) for i in range(self.treeWidget.currentItem().childCount())]
            for i in children:
                param_string = ""
                if i.text(2) == "(None)":
                    pass
                if i.text(2) == "Parametric Function":
                    param_string += "function=lambda t: np.array((" + i[1]["xt"] \
                        .replace("^", "**") \
                        .replace("cos", "np.cos") \
                        .replace("sin", "np.sin") + "," + i[1]["yt"] \
                                        .replace("^", "**") \
                                        .replace("cos", "np.cos") \
                                        .replace("sin", "np.sin") + ",0)),"
                else:
                    showList.append(i.text(0))
                    objDict = eval(i.text(3))
                    for prop,val in objDict.items():
                        if prop in ["x_shift", "y_shift"]:
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
                                    param_string += "lambda x: " + val \
                                        .replace("^", "**") \
                                        .replace("cos", "np.cos") \
                                        .replace("sin", "np.sin") + ","
                                else:
                                    param_string += prop + "=" + val + ","
                    objLine = "        " + i.text(0) + "=" + self.objProp[i.text(2)][0] + "(" + param_string[:-1] + ")" #TODO ensure name has no spaces
                    try:
                        objLine += ".shift(RIGHT*" + str(objDict["x_shift"]) + "+UP*" + str(objDict["y_shift"]) + ")"
                    except:
                        pass
                    f.write(objLine + "\n")
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
            f.close()

    def renderScene(self):
        # if not self.save_mmtr():
        #    return None
        self.file_path = QtWidgets.QFileDialog.getSaveFileName(filter="Video (*.mp4)")[0]
        if self.file_path == "": return
        os.chdir("/".join(self.file_path.split("/")[:-1]))
        self.convert_to_manim()
        subprocess.run("manim manim.py MyScene")
        try:
            os.replace("./media/videos/manim/1080p60/MyScene.mp4", "./"+self.file_path.split("/")[-1])
            shutil.rmtree('media')
            shutil.rmtree('__pycache__')
        except:
           pass

    def save_mmtr_as(self):
        if None in self.objSave or len(self.objSave) == 0:  # Partially useless right now
            return None
        try:
            self.file_path = QtWidgets.QFileDialog.getSaveFileName(filter="Manimator (*.mmtr)")[0]
            self.save_mmtr()
        except:
            return False
        self.setWindowTitle("Manimator - " + self.file_path.split("/")[-1])

    def save_mmtr(self):
        if None in self.objSave or len(self.objSave) == 0:  # Partially useless right now
            return False
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