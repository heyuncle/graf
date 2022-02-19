import subprocess, sys, os, shutil
import xml.etree.ElementTree as et

from preferences import Ui_Dialog

from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qt_material import apply_stylesheet, QtStyleTools


# from error import Ui_Dialog as errorDialog # TODO - what was this for

class MainWindow(QMainWindow, QtStyleTools):
    objNames = []
    objSave = []
    animSave = []
    file_path = ''

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        for i in sys.argv[1:]:
            self.open_mmtr(i)

        self.setWindowIcon(QIcon('etc/logo.ico'))
        # self.setStyleSheet(PyQt5_stylesheets.load_stylesheet_pyqt5(style="style_Dark")) # qrainbowtheme option
        # self.setStyleSheet(qdarktheme.load_stylesheet("dark")) # pyqtdarktheme option
        self.main = uic.loadUi('ui/window.ui', self)
        self.apply_stylesheet(self.main, theme='dark_blue.xml')  # qmaterial
        self.show()
        #self.retranslateUi(MainWindow)
        
        self.newObjButton.clicked.connect(self.addItem)
        self.treeWidget.itemClicked.connect(self.changeProperties)
        self.treeWidget.itemDoubleClicked.connect(self.edit)
        self.surrObjComboBox.currentTextChanged.connect(self.changeObjType)
        self.colorPushButton.clicked.connect(self.changeColor)

        self.actionOpen.triggered.connect(self.open_from_dir)
        self.actionSave.triggered.connect(self.save_mmtr)
        self.actionSave_as.triggered.connect(self.save_mmtr_as)
        self.actionPreferences.triggered.connect(self.openPreferences)
        self.actionDelete.triggered.connect(self.delItem) #TODO fix
        self.actionMP.triggered.connect(lambda _: self.renderScene(True)) #TODO fix

        # Test project
        newScene = QTreeWidgetItem()
        newScene.setText(0,self.testDuplicateName("Scene 1")) # TODO fix testDuplicateName
        newScene.setText(1,"Scene")
        self.treeWidget.addTopLevelItem(newScene)
        newObject = QTreeWidgetItem()
        newObject.setText(0,self.testDuplicateName("MyRectangle"))
        newObject.setText(1,"Object")
        newObject.setText(2,"Rectangle")
        newObject2 = QTreeWidgetItem()
        newObject2.setText(0,self.testDuplicateName("MyUnderline"))
        newObject2.setText(1,"Object")
        newObject2.setText(2,"Underline")
        newScene.addChild(newObject)
        newScene.addChild(newObject2)
        self.changeProperties()

    def edit(self):
        self.treeWidget.editItem(self.treeWidget.currentItem())

    def changeObjType(self):
        for i in self.treeWidget.selectedItems():
            i.setText(2,self.surrObjComboBox.currentText())

    def changeColor(self):
        self.colorFrame.setStyleSheet("background-color: " + QtWidgets.QColorDialog.getColor().name())

    def changeProperties(self):
        def showSharedProp(sharedProp):
            for i in [self.colorGroupBox,self.positionGroupBox]:
                i.show() if sharedProp % 2 == 1 else i.hide()
                sharedProp >>= 1
        
        shared = {"Rectangle":3,"Underline":1}
        for i in self.scrollAreaWidgetContents_2.findChildren(QtWidgets.QGroupBox):
            i.hide()
        
        if len(self.treeWidget.selectedItems()) == 1:
            if self.treeWidget.currentItem().text(1)=="Object":
                self.objTypeComboBox.show()
                objType = self.treeWidget.currentItem().text(2)
                showSharedProp(shared[objType])
                if objType == "Rectangle":
                    self.rectGroupBox.show()
                if objType == "Underline":
                    self.ulGroupBox.show()
            else:
                pass # TODO Single-select properties for scene, split for group
        else:
            if len(list(dict.fromkeys([i.text(1) for i in self.treeWidget.selectedItems()]))) == 1:
                if self.treeWidget.currentItem().text(1)=="Object":
                        self.objTypeComboBox.show()
                        combinedProp = 3
                        for i in self.treeWidget.selectedItems():
                            combinedProp &= shared[i.text(2)]
                        showSharedProp(combinedProp)
                else:
                    pass # TODO Multi-select properties for scene, split for group
            else:
                print("multiple object types selected")

    def testDuplicateName(self, name):
        if name in self.objNames:
            return self.testDuplicateName(name + "_")
        return name

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

    def addItem(self):
        if self.treeWidget.currentItem().text(1) in ["Group","Scene"]:
            newItem = QTreeWidgetItem()
            newItem.setText(0,self.testDuplicateName("MyObject"))
            newItem.setText(1,"Object")
            newItem.setText(2,"Rectangle")
            self.treeWidget.currentItem().addChild(newItem)
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