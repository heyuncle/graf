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
            self.objProp = {i[0]:(i[1],i[4],i[5]) for i in self.objPropCsv} # manim name, shared, groupbox


        self.setWindowIcon(QIcon('icons/logo.ico'))
        self.setupUi(self)
        # self.setStyleSheet(PyQt5_stylesheets.load_stylesheet_pyqt5(style="style_Dark")) # qrainbowtheme option
        # self.setStyleSheet(qdarktheme.load_stylesheet("dark")) # pyqtdarktheme option
        self.apply_stylesheet(self, theme='dark_blue.xml')  # qmaterial
        self.show()
        self.retranslateUi(MainWindow)
        
        self.newObjButton.clicked.connect(lambda _: self.addObject(self.treeItem("MyObject","Object","(None)")))
        self.treeWidget.itemClicked.connect(self.updatePropPanel)
        self.treeWidget.itemDoubleClicked.connect(self.edit)
        self.objTypeComboBox.currentTextChanged.connect(self.changeObjType)
        self.colorPushButton.clicked.connect(self.changeColor)
        self.updateObjPropButton.clicked.connect(self.saveProp)
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
        self.addObject(self.treeItem("MyObject","Object","Rectangle","{'height':1.0,'width':1.0,'grid_xstep':1.0,'grid_ystep':1.0}"))
        self.updatePropPanel()

    def treeItem(self, name, type, subtype="", properties="{}"):
        item = QTreeWidgetItem()
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        item.setText(0,self.testDuplicateName(name)) # TODO fix testDuplicateName
        item.setText(1,type)
        item.setText(2,subtype)
        item.setText(3,properties)
        item.setText(4,str(self.objectID))
        item.setIcon(0,QIcon("icons/camera-solid.ico" if type=="Scene" else "icons/equation.ico" if type=="Object" else "icons/object-group-solid.ico"))
        return item


    def edit(self):
        self.treeWidget.editItem(self.treeWidget.currentItem())
        print(self.testDuplicateName("MyObject"))

    def changeObjType(self):
        for i in self.treeWidget.selectedItems():
            i.setText(2,self.objTypeComboBox.currentText())
        self.updatePropPanel()
        self.loadProp("shit") #TODO default properties per obj

    def getObjID(self, name):
        if (name != "(None)"):
            return int(self.treeWidget.findItems(name, Qt.MatchFixedString | Qt.MatchRecursive, 0)[0].text(4))
        else:
            return None

    def loadProp(self, prop):
        for i in self.propScrollAreaWidget.findChildren(QtWidgets.QGroupBox):
            if i.isVisible():
                if i.objectName() == "rectGroupBox":
                    for j in self.treeWidget.selectedItems():
                        j = ast.literal_eval(j) # convert string to dict
                        self.rectHeightSpinBox.setValue(float(j["height"]))
                        self.rectWidthSpinBox.setValue(j["width"])
                        self.xGridSpinBox.setValue(j["grid_xstep"])
                        self.yGridSpinBox.setValue(j["grid_ystep"])
                elif i.objectName() == "ulGroupBox":
                    for j in self.treeWidget.selectedItems():
                        j = ast.literal_eval(j)
                        try: # put in try loop incase object is deleted between saving and loading
                            self.ulObjComboBox.setCurrentText(self.treeWidget.findItems(str(j["object"]), Qt.MatchFixedString | Qt.MatchRecursive, 4)[0].text(0))
                        except:
                            self.ulObjComboBox.setCurrentText("(None)")
                        self.ulBuffSpinBox.setValue(j["buff"])
                elif i.objectName() == "arcGroupBox":
                    for j in self.treeWidget.selectedItems():
                        j = ast.literal_eval(j)
                        self.radiusSpinBox.setValue(j["radius"])
                        self.stAngleSpinBox.setValue(j["start_angle"])
                        self.angleSpinBox.setValue(j["angle"])
                elif i.objectName() == "arrowGroupBox":
                    for j in self.treeWidget.selectedItems():
                        j = ast.literal_eval(j)
                        self.arStrokeSpinBox.setValue(j["stroke_width"])
                        self.arBuffSpinBox.setValue(j["buff"])
                elif i.objectName() == "braceGroupBox":
                    for j in self.treeWidget.selectedItems():
                        j = ast.literal_eval(j)
                        try:
                            self.braceObjSelectComboBox.setCurrentText(self.treeWidget.findItems(str(j["object"]), Qt.MatchFixedString | Qt.MatchRecursive, 4)[0].text(0))
                        except:
                            self.braceObjSelectComboBox.setCurrentText("(None)")
                        self.bracePlainTextEdit.setPlainText(j["text"])
                elif i.objectName() == "colorGroupBox":
                    for j in self.treeWidget.selectedItems(): # TODO: load color in
                        j = ast.literal_eval(j)
                        j.setText(3,str(eval(j.text(3)) | {
                            "color": self.colorFrame.styleSheet().split()[-1]
                        }))
                elif i.objectName() == "directionGroupBox":
                    for j in self.treeWidget.selectedItems():
                        j = ast.literal_eval(j)
                        try:
                            self.dirStartComboBox.setCurrentText(j["start"])
                        except:
                            self.dirStartComboBox.setCurrentText("(None)")
                        try:
                            self.dirEndComboBox.setCurrentText(j["start"])
                        except:
                            self.dirEndComboBox.setCurrentText("(None)")
                elif i.objectName() == "dotGroupBox":
                    for j in self.treeWidget.selectedItems():
                        j = ast.literal_eval(j)
                        self.coordLineEdit.setText(j["point"])
                        self.widthSpinBox.setValue(j["stroke_width"])
                        self.opacitySpinBox.setValue(j["fill_opacity"])
                elif i.objectName() == "functionGroupBox":
                    for j in self.treeWidget.selectedItems(): # TODO: load image back in, maybe save the filepath?
                        j = ast.literal_eval(j)
                        j.setText(3,str(eval(j.text(3)) | {
                            "function": None
                        }))
                elif i.objectName() == "latexGroupBox":
                    for j in self.treeWidget.selectedItems():
                        j = ast.literal_eval(j)
                        self.latexSizeSpinBox.setValue(j["font_size"])
                elif i.objectName() == "lineGroupBox":
                    for j in self.treeWidget.selectedItems():
                        j = ast.literal_eval(j)
                        self.startCorLineEdit.setText(j["start"])
                        self.endCorLineEdit.setText(j["end"])
                        self.lineThickSpinBox.setValue(j["buff"])
                elif i.objectName() == "matrixGroupBox": # TODO: figure out what is going on with this
                    for j in self.treeWidget.selectedItems():
                        j = ast.literal_eval(j)
                        j.setText(3,str(eval(j.text(3)) | {
                            "matrix": self.matrixTableWidget.items()
                        }))
                        for i in range(0, len(j["matrix"])):
                            for k in range(0, len(j["matrix"][i])):
                                self.matrixTableWidget.setItem(i, k, j["matrix"][i][k])
                elif i.objectName() == "numPlaneGroupBox":
                    for j in self.treeWidget.selectedItems():
                        j = ast.literal_eval(j)
                        self.numXMinSpinBox.setValue(j["x_min"])
                        self.numXMaxSpinBox.setValue(j["x_max"])
                        self.numYMinSpinBox.setValue(j["y_min"])
                        self.numYMaxSpinBox.setValue(j["y_max"])
                        self.numXLengthSpinBox.setValue(j["x_length"])
                        self.numYLengthSpinBox.setValue(j["y_length"])
                elif i.objectName() == "positionGroupBox":
                    for j in self.treeWidget.selectedItems():
                        j = ast.literal_eval(j)
                        self.xSpinBox.setValue(j["x_shift"])
                        self.ySpinBox.setValue(j["y_shift"])
                elif i.objectName() == "paramFuncGroupBox":
                    for j in self.treeWidget.selectedItems():
                        j = ast.literal_eval(j)
                        self.minTSpinBox.setValue(j["t_start"])
                        self.maxTSpinBox.setValue(j["t_end"])
                elif i.objectName() == "regPolyGroupBox":
                    for j in self.treeWidget.selectedItems():
                        j = ast.literal_eval(j)
                        self.regPolyVertSpinBox.setValue(j["n"])
                elif i.objectName() == "surRectGroupBox":
                    for j in self.treeWidget.selectedItems():
                        j = ast.literal_eval(j)
                        try:
                            self.surrObjComboBox.setCurrentText(self.treeWidget.findItems(str(j["object"]), Qt.MatchFixedString | Qt.MatchRecursive, 4)[0].text(0))
                        except:
                            self.surrObjComboBox.setCurrentText("(None)")
                        self.surrBuffSpinBox.setValue(j["buff"])
                        self.surrRadiusSpinBox.setValue(j["corner_radius"])
                elif i.objectName() == "textGroupBox":
                    for j in self.treeWidget.selectedItems():
                        j = ast.literal_eval(j)
                        j.setText(3,str(eval(j.text(3)) | {
                            "text": self.textPlainTextEdit.toPlainText(),
                            "font_size": self.textSizeSpinBox.value(),
                            "fill_opacity": self.textOpacitySpinBox.value(),
                            "slant": self.italicCheckBox.isChecked(),
                            "weight": self.textBoldCheckBox.isChecked(),
                            "stroke_width": self.textStrokeSpinBox.value()
                        }))
                        self.textPlainTextEdit.setPlainText(j["text"])
                        self.textSizeSpinBox.setValue(j["font_size"])
                        self.textOpacitySpinBox.setValue(j["fill_opacity"])
                        self.italicCheckBox.setChecked(j["slant"])
                        self.textBoldCheckBox.setChecked(j["weight"])
                        self.textStrokeSpinBox.setValue(j["stroke_width"])
                elif i.objectName() == "polyGroupBox":
                    for j in self.treeWidget.selectedItems():
                        j = ast.literal_eval(j)
                        for i in j["vertices"]:
                            self.polyVertListWidget.addItem(i)

    def saveProp(self):
        for i in self.propScrollAreaWidget.findChildren(QtWidgets.QGroupBox):
            if i.isVisible():
                if i.objectName() == "rectGroupBox":
                    for j in self.treeWidget.selectedItems():
                        j.setText(3,str(eval(j.text(3)) | {
                            "height": self.rectHeightSpinBox.value(),
                            "width": self.rectWidthSpinBox.value(),
                            "grid_xstep": self.xGridSpinBox.value(),
                            "grid_ystep": self.yGridSpinBox.value()
                        }))
                elif i.objectName() == "ulGroupBox":
                    for j in self.treeWidget.selectedItems():
                        j.setText(3,str(eval(j.text(3)) | {
                            "object": self.getObjID(self.ulObjComboBox.currentText()),
                            "buff": self.ulBuffSpinBox.value()
                        }))
                elif i.objectName() == "arcGroupBox":
                    for j in self.treeWidget.selectedItems():
                        j.setText(3,str(eval(j.text(3)) | {
                            "radius": self.radiusSpinBox.value(),
                            "start_angle": self.stAngleSpinBox.value(),
                            "angle": self.angleSpinBox.value()
                        }))
                elif i.objectName() == "arrowGroupBox":
                    for j in self.treeWidget.selectedItems():
                        j.setText(3,str(eval(j.text(3)) | {
                            "stroke_width": self.arStrokeSpinBox.value(),
                            "buff": self.arBuffSpinBox.value()
                        }))
                elif i.objectName() == "braceGroupBox":
                    for j in self.treeWidget.selectedItems():
                        j.setText(3,str(eval(j.text(3)) | {
                            "object": self.getObjID(self.braceObjSelectComboBox.currentText()),
                            "text": self.bracePlainTextEdit.toPlainText()
                        }))
                elif i.objectName() == "colorGroupBox":
                    for j in self.treeWidget.selectedItems():
                        j.setText(3,str(eval(j.text(3)) | {
                            "color": self.colorFrame.styleSheet().split()[-1]
                        }))
                elif i.objectName() == "directionGroupBox":
                    for j in self.treeWidget.selectedItems():
                        j.setText(3,str(eval(j.text(3)) | {
                            "start": (self.dirStartComboBox.currentText() if self.dirStartComboBox.currentText() != "(None)" else None),
                            "end": (self.dirEndComboBox.currentText() if self.dirEndComboBox.currentText() != "(None)" else None)
                        }))
                elif i.objectName() == "dotGroupBox":
                    for j in self.treeWidget.selectedItems():
                        j.setText(3,str(eval(j.text(3)) | {
                            "point": self.coordLineEdit.text(),
                            "stroke_width": self.widthSpinBox.value(),
                            "fill_opacity": self.opacitySpinBox.value()
                        }))
                elif i.objectName() == "functionGroupBox":
                    for j in self.treeWidget.selectedItems():
                        j.setText(3,str(eval(j.text(3)) | {
                            "function": None
                        }))
                elif i.objectName() == "latexGroupBox":
                    for j in self.treeWidget.selectedItems():
                        j.setText(3,str(eval(j.text(3)) | {
                            "font_size": self.latexSizeSpinBox.value()
                        }))
                elif i.objectName() == "lineGroupBox":
                    for j in self.treeWidget.selectedItems():
                        j.setText(3,str(eval(j.text(3)) | {
                            "start": self.startCorLineEdit.text(),
                            "end": self.endCorLineEdit.text(),
                            "buff": self.lineThickSpinBox.value()
                        }))
                elif i.objectName() == "matrixGroupBox":
                    for j in self.treeWidget.selectedItems():
                        j.setText(3,str(eval(j.text(3)) | {
                            "matrix": self.matrixTableWidget.items()
                        }))
                elif i.objectName() == "numPlaneGroupBox":
                    for j in self.treeWidget.selectedItems():
                        j.setText(3,str(eval(j.text(3)) | {
                            "x_min": self.numXMinSpinBox.value(),
                            "x_max": self.numXMaxSpinBox.value(),
                            "y_min": self.numYMinSpinBox.value(),
                            "y_max": self.numYMaxSpinBox.value(),
                            "x_length": self.numXLengthSpinBox.value(),
                            "y_length": self.numYLengthSpinBox.value()
                        }))
                elif i.objectName() == "positionGroupBox":
                    for j in self.treeWidget.selectedItems():
                        j.setText(3,str(eval(j.text(3)) | {
                            "x_shift": self.xSpinBox.value(),
                            "y_shift": self.ySpinBox.value()
                        }))
                elif i.objectName() == "paramFuncGroupBox":
                    for j in self.treeWidget.selectedItems():
                        j.setText(3,str(eval(j.text(3)) | {
                            "t_start": self.minTSpinBox.value(),
                            "t_end": self.maxTSpinBox.value()
                        }))
                elif i.objectName() == "regPolyGroupBox":
                    for j in self.treeWidget.selectedItems():
                        j.setText(3,str(eval(j.text(3)) | {
                            "n": self.regPolyVertSpinBox.value()
                        }))
                elif i.objectName() == "surRectGroupBox":
                    for j in self.treeWidget.selectedItems():
                        j.setText(3,str(eval(j.text(3)) | {
                            "object": self.getObjID(self.surrObjComboBox.currentText()),
                            "buff": self.surrBuffSpinBox.value(),
                            "corner_radius": self.surrRadiusSpinBox.value()
                        }))
                elif i.objectName() == "textGroupBox":
                    for j in self.treeWidget.selectedItems():
                        j.setText(3,str(eval(j.text(3)) | {
                            "text": self.textPlainTextEdit.toPlainText(),
                            "font_size": self.textSizeSpinBox.value(),
                            "fill_opacity": self.textOpacitySpinBox.value(),
                            "slant": self.italicCheckBox.isChecked(),
                            "weight": self.textBoldCheckBox.isChecked(),
                            "stroke_width": self.textStrokeSpinBox.value()
                        }))
                elif i.objectName() == "polyGroupBox":
                    for j in self.treeWidget.selectedItems():
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

    def testDuplicateName(self, name):
        allNames = [i.text(0) for i in self.treeWidget.findItems("Object", Qt.MatchFixedString | Qt.MatchRecursive, 1)] + [i.text(0) for i in self.treeWidget.findItems("Group", Qt.MatchFixedString | Qt.MatchRecursive, 1)] + [i.text(0) for i in self.treeWidget.findItems("Scene", Qt.MatchFixedString | Qt.MatchRecursive, 1)]
        if (name in allNames):
            allNames.remove(name) # search includes the object currently, remove 1 of it to test for duplicates
        if (name in allNames):
            tempName = name + " (1)"
            while (tempName in allNames):
                tempName = name + " (" + str(int(tempName[-2]) + 1) + ")"
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
                    for j in eval(i.text(3)).items():
                        if j[0] in ["x_shift", "y_shift", "color"]: # color temporary
                            pass
                        # elif j[0] == "show": #TODO show at start property
                        #     if j[1] == True:
                        #         showList.append(i.text(0))
                        else:
                            try:
                                float(j[1])
                                param_string += j[0] + "=" + str(j[1]) + ","
                            except:
                                # If number is not float or int (can't be converted to float)
                                # if j[0] == "color":
                                #     param_string += j[0] + "='" + j[1] + "'," #TODO fix color saving
                                if i.text(2) == "LaTex":
                                    param_string += "r'" + j[1] + "',"
                                elif i.text(2) == "Polygon":
                                    param_string += j[1] + ","
                                elif i.text(2) == "Point Label":
                                    if j[0] == "text":
                                        param_string += "text=r'" + j[1] + "',"
                                    else:
                                        param_string += j[0] + "=" + j[1] + ","
                                elif i.text(2) == "Text":
                                    param_string += j[0] + "=r'" + j[1] + "',"
                                elif i.text(2) == "Function Graph":
                                    param_string += "lambda x: " + j[1] \
                                        .replace("^", "**") \
                                        .replace("cos", "np.cos") \
                                        .replace("sin", "np.sin") + ","
                                else:
                                    param_string += j[0] + "=" + j[1] + ","
                    objLine = "        " + i.text(0) + "=" + i.text(2) + "(" + param_string[:-1] + ")" #TODO ensure name has no spaces
                    try:
                        objLine += ".shift(RIGHT*" + str(i[1]["x_shift"]) + "+UP*" + str(i[1]["y_shift"]) + ")"
                    except:
                        pass
                    f.write(objLine + "\n")
            f.write("        self.add(" + ",".join([i for i in showList[::-1]]) + ")\n")
            # f.write("        self.wait()\n") # NOTE previously commented
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
        os.chdir("/".join(self.file_path.split("/")[:-1]))
        self.convert_to_manim()
        subprocess.run("manim manim.py MyScene")
        try:
            os.replace("./media/videos/manim_export/1080p60/MyScene.mp4", "./"+self.file_path.split("/")[-1])
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