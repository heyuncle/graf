import subprocess, sys, os, shutil, csv
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
        super(MainWindow, self).__init__(*args, **kwargs)
        for i in sys.argv[1:]:
            self.open_mmtr(i)
        
        with open("objectProperties.csv","r") as f:
            self.objPropCsv = csv.reader(f)
            self.objProp = {i[0]:(i[1],i[4],i[5]) for i in self.objPropCsv} # manim name, shared, groupbox


        self.setWindowIcon(QIcon('etc/logo.ico'))
        self.setupUi(self)
        # self.setStyleSheet(PyQt5_stylesheets.load_stylesheet_pyqt5(style="style_Dark")) # qrainbowtheme option
        # self.setStyleSheet(qdarktheme.load_stylesheet("dark")) # pyqtdarktheme option
        self.apply_stylesheet(self, theme='dark_blue.xml')  # qmaterial
        self.show()
        self.retranslateUi(MainWindow)
        
        self.newObjButton.clicked.connect(self.addItem)
        self.treeWidget.itemClicked.connect(self.updatePropPanel)
        self.treeWidget.itemDoubleClicked.connect(self.edit)
        self.objTypeComboBox.currentTextChanged.connect(self.changeObjType)
        self.colorPushButton.clicked.connect(self.changeColor)

        self.actionOpen.triggered.connect(self.open_from_dir)
        self.actionSave.triggered.connect(self.save_mmtr)
        self.actionSave_as.triggered.connect(self.save_mmtr_as)
        self.actionPreferences.triggered.connect(self.openPreferences)
        self.actionDelete.triggered.connect(self.delItem) #TODO fix
        self.actionMP.triggered.connect(lambda _: self.renderScene(True)) #TODO fix

        # Test project
        newScene = self.treeItem("Scene 1","Scene")
        self.treeWidget.addTopLevelItem(newScene)
        newScene.addChild(self.treeItem("MyRectangle","Object","Rectangle"))
        newScene.addChild(self.treeItem("MyUnderline","Object","Underline"))
        self.updatePropPanel()

    def treeItem(self, name, type, subtype="", properties=""):
        item = QTreeWidgetItem()
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        item.setText(0,self.testDuplicateName(name)) # TODO fix testDuplicateName
        item.setText(1,type)
        item.setText(2,subtype)
        item.setText(3,properties)
        return item


    def edit(self):
        self.treeWidget.editItem(self.treeWidget.currentItem())

    def changeObjType(self):
        for i in self.treeWidget.selectedItems():
            i.setText(2,self.objTypeComboBox.currentText())
        self.updatePropPanel()

    def changeColor(self):
        self.colorFrame.setStyleSheet("background-color: " + QtWidgets.QColorDialog.getColor().name())

    def updatePropPanel(self):
        def showSharedProp(sharedProp):
            for i in [self.colorGroupBox,self.positionGroupBox]:
                i.show() if sharedProp % 2 == 1 else i.hide()
                sharedProp >>= 1
        def showUniqueProp(objType):
            for i in self.objProp[objType][2].split():
                exec("self."+i+".show()")
            

        for i in self.scrollAreaWidgetContents_2.findChildren(QtWidgets.QGroupBox):
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
        return name #TODO fix

    def open_mmtr(self, file):
        # display_names = {'NumberPlane': 'Coordinate Plane', 'ParametricFunction': 'Parametric Function',
        #                  'Arc': 'Circle', 'RegularPolygon': 'Regular Polygon', 'SurroundingRectangle': 'Box',
        #                  'BraceLabel': 'Brace', 'Tex': 'LaTeX', 'ShowCreation': 'Show Creation',
        #                  'Write': 'Write Text', 'FadeIn': 'Fade In', 'FadeOut': 'Fade Out',
        #                  'GrowFromCenter': 'Grow', 'Flash': 'Spark', 'Indicate': 'Highlight',
        #                  'MoveAlongPath': 'Move Along Path', 'ReplacementTransform': 'Transform'}
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

    def addItem(self):
        if self.treeWidget.currentItem().text(1) in ["Group","Scene"]:
            self.treeWidget.currentItem().addChild(self.treeItem("MyObject","Object","Rectangle"))
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText('More information')
            msg.setWindowTitle("Error")
            msg.exec_()

    def delItem(self):
        for i in self.treeWidget.selectedItems():
            self.treeWidget.delete


    def convert_to_manim(self, type):
        with open("manim_" + type + ".py", "w+") as f:
            f.write("from manim import *\nclass MyScene(Scene):\n    def construct(self):\n")
            showList = []
            for i in self.objSave:
                param_string = ""
                if i[0] == "ParametricFunction":
                    param_string += "function=lambda t: np.array((" + i[1]["xt"] \
                        .replace("^", "**") \
                        .replace("cos", "np.cos") \
                        .replace("sin", "np.sin") + "," + i[1]["yt"] \
                                        .replace("^", "**") \
                                        .replace("cos", "np.cos") \
                                        .replace("sin", "np.sin") + ",0)),"
                if i[0] == "":
                    pass
                else:
                    for j in i[1].items():
                        if j[0] in ["x", "y", "xt",
                                    "yt"]:  # How to deal with normal params of parametric without doing this?
                            pass
                        elif j[0] == "show":
                            if j[1] == True:
                                showList.append(i[2])
                        else:
                            try:
                                float(j[1])
                                param_string += j[0] + "=" + str(j[1]) + ","
                            except:
                                # If number is not float or int (can't be converted to float)
                                if j[0] == "color":
                                    param_string += j[0] + "='" + j[1] + "',"
                                elif i[0] == "Tex":
                                    param_string += "r'" + j[1] + "',"
                                elif i[0] == "Polygon":
                                    param_string += j[1] + ","
                                elif i[0] == "BraceLabel":
                                    if j[0] == "text":
                                        param_string += "text=r'" + j[1] + "',"
                                    else:
                                        param_string += j[0] + "=" + j[1] + ","
                                elif i[0] == "Text":
                                    param_string += j[0] + "=r'" + j[1] + "',"
                                elif i[0] == "FunctionGraph":
                                    param_string += "lambda x: " + j[1] \
                                        .replace("^", "**") \
                                        .replace("cos", "np.cos") \
                                        .replace("sin", "np.sin") + ","
                                else:
                                    param_string += j[0] + "=" + j[1] + ","
                    objLine = "        " + i[2] + "=" + i[0] + "(" + param_string[:-1] + ")"
                    try:
                        objLine += ".shift(RIGHT*" + str(i[1]["x"]) + "+UP*" + str(i[1]["y"]) + ")"
                    except:
                        pass
                    f.write(objLine + "\n")
            f.write("        self.add(" + ",".join([i for i in showList[::-1]]) + ")\n")
            # f.write("        self.wait()\n")
            for i in self.animSave:
                param_string = ""
                if i[0] == "Move":
                    f.write(
                        "        self.play(" + i[1]["mobject"] +
                        ".shift,RIGHT*" + str(i[1]["x"]) +
                        "+UP*" + str(i[1]["y"]) + ")\n")
                else:
                    for j in i[1].items():
                        param_string += j[0] + "=" + str(j[1]) + ","
                    f.write("        self.play(" + i[0] + "(" + param_string[:-1] + "))\n")
            f.write("        self.wait()")
            f.close()

    def renderScene(self, full):
        if not self.save_mmtr():
            return None
        os.chdir("/".join(self.file_path.split("/")[:-1]))
        self.convert_to_manim("export" if full else "preview")
        subprocess.run("manim manim_preview.py MyScene -ql" if full else "manim manim_export.py MyScene")
        try:
            if full:
                os.replace("./media/videos/a/1080p60/MyScene.mp4", "./Export.mp4")
            else:
                os.replace("./media/videos/manim_preview/480p15/MyScene.mp4", "./Preview.mp4")
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