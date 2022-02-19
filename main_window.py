import subprocess, sys, os, shutil
import xml.etree.ElementTree as et

from window import Ui_MainWindow
from properties import Ui_Dialog

from PyQt5 import QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qt_material import apply_stylesheet


# from error import Ui_Dialog as errorDialog # TODO - what was this for

class MainWindow(QMainWindow, Ui_MainWindow):
    objNames = []
    objSave = []
    animSave = []
    file_path = ''

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        for i in sys.argv[1:]:
            self.open_mmtr(i)

        self.setWindowIcon(QIcon('logo.ico'))
        self.setupUi(self)
        # self.setStyleSheet(PyQt5_stylesheets.load_stylesheet_pyqt5(style="style_Dark")) # qrainbowtheme option
        # app.setStyleSheet(qdarktheme.load_stylesheet("dark")) # pyqtdarktheme option
        apply_stylesheet(self, theme='dark_blue.xml')  # qmaterial
        #self.insertCategory.setCurrentIndex(0)
        self.show()
        self.retranslateUi(MainWindow)
        
        self.newObjButton.clicked.connect(self.addItem)
        #self.buttonDelete.clicked.connect(self.delItem)
        self.treeWidget.itemClicked.connect(self.changeProperties)
        #self.previewRender.clicked.connect(lambda _: self.renderScene(False))
        #self.fqRender.clicked.connect(lambda _: self.renderScene(True))
        #self.categoryBox.currentIndexChanged['int'].connect(self.insertCategory.setCurrentIndex)
        #self.objList.currentRowChanged.connect(lambda _: self.animList.setCurrentRow(-1))
        #self.animList.currentRowChanged.connect(lambda _: self.objList.setCurrentRow(-1))

        #self.actionOpen.triggered.connect(self.open_from_dir)
        #self.actionSave.triggered.connect(self.save_mmtr)
        #self.actionSave_As.triggered.connect(self.save_mmtr_as)
        #self.actionPreview.triggered.connect(lambda _: self.renderScene(False))
        #self.actionRenderFull.triggered.connect(lambda _: self.renderScene(True))
        #self.actionDelete.triggered.connect(self.delItem)
        #self.actionMU.triggered.connect(self.move_up)
        #self.actionMD.triggered.connect(self.move_down)

        # Test project
        newScene = QTreeWidgetItem()
        newScene.setText(0,self.testDuplicateName("Scene 1"))
        newScene.setText(1,"Scene")
        self.treeWidget.addTopLevelItem(newScene)
        newObject = QTreeWidgetItem()
        newObject.setText(0,self.testDuplicateName("MyObject"))
        newObject.setText(1,"Object")
        newObject.setText(2,"Circle")
        newScene.addChild(newObject)

    def changeProperties():
        pass

    def testDuplicateName(self, name):
        if name in self.objNames:
            return self.testDuplicateName(name + "_")
        return name

    def open_mmtr(self, file):
        display_names = {'NumberPlane': 'Coordinate Plane', 'ParametricFunction': 'Parametric Function',
                         'Arc': 'Circle', 'RegularPolygon': 'Regular Polygon', 'SurroundingRectangle': 'Box',
                         'BraceLabel': 'Brace', 'Tex': 'LaTeX', 'ShowCreation': 'Show Creation',
                         'Write': 'Write Text', 'FadeIn': 'Fade In', 'FadeOut': 'Fade Out',
                         'GrowFromCenter': 'Grow', 'Flash': 'Spark', 'Indicate': 'Highlight',
                         'MoveAlongPath': 'Move Along Path', 'ReplacementTransform': 'Transform'}
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

    def openProperties(self, prop_type):
        def submitProperties():
            props = {}
            for i in self.properties.propertyStack.currentWidget().findChildren(QLineEdit):
                property_name = "_".join(i.objectName().split("_")[1:])
                if property_name in ["obj", "object", "mobject"]:
                    if i.text() not in self.objNames:
                        return None
                if i.text() == "":
                    props[property_name] = i.placeholderText()
                else:
                    props[property_name] = i.text()
            name = self.properties.nameEdit.text().replace(" ", "_")
            if name != self.objSave[self.objList.currentRow()][2]:
                name = self.testDuplicateName(name)
            if prop_type == "obj":
                props["show"] = self.properties.showCheckBox.isChecked()
                color = self.properties.currentColor.styleSheet().split()[-1]
                if color != "255);":
                    props["color"] = color
                self.objSave[self.objList.currentRow()] = [self.properties.propertyStack.currentWidget().objectName(), props,
                                                      name]
                self.objNames[self.objList.currentRow()] = name
                self.objList.currentItem().setText(self.objList.currentItem().text().split("(")[0] + "(" + name + ")")
            else:
                self.animSave[self.animList.currentRow()] = [self.properties.propertyStack.currentWidget().objectName(),
                                                        props]
            self.propWindow.close()
            print(self.objSave)
            print(self.animSave)

        def loadProperties(prop_type):
            possibleProp = {"Coordinate Plane": 0, "Function": 1, "Parametric Function": 2, "Circle": 3, "Arrow": 4,
                            "Polygon": 5, "Regular Polygon": 6, "Rectangle": 7, "Dot": 8, "Line": 9, "Matrix": 10,
                            "Box": 11, "Underline": 12, "Brace": 13, "LaTeX": 14, "Text": 15, "Show Creation": 16,
                            "Uncreate": 17, "Write Text": 18, "Fade In": 19, "Fade Out": 20, "Grow": 21, "Spark": 22,
                            "Highlight": 23, "Move": 24, "Move Along Path": 25, "Transform": 26}
            if prop_type == "obj":
                for i in ["nameEdit", "nameLabel", "showCheckBox", "colorLabel", "colorSelect", "currentColor"]:
                    exec("self.properties." + i + ".setEnabled(True)")
                try:
                    self.properties.showCheckBox.setChecked(self.objSave[self.objList.currentRow()][1]["show"])
                except:
                    pass
                try:
                    self.properties.currentColor.setStyleSheet(
                        "background-color: " + self.objSave[self.objList.currentRow()][1]["color"])
                except:
                    pass
                try:
                    self.properties.nameEdit.setText(self.objSave[self.objList.currentRow()][2])
                except:
                    self.properties.nameEdit.setText(self.objList.currentItem().text().split("(")[1][:-1])
                print(self.objSave)
                print(self.animSave)
                try:
                    self.properties.propertyStack.setCurrentIndex(
                        possibleProp[self.objList.currentItem().text().split('(')[0][:-1]])
                except:
                    self.propWindow.close()
            else:
                try:
                    self.properties.propertyStack.setCurrentIndex(possibleProp[self.animList.currentItem().text()])
                except:
                    self.propWindow.close()
            # Currently broken data validation
            # for i in self.properties.propertyStack.currentWidget().findChildren(QLineEdit):
            #     if i.placeholderText() in ["X Line Frequency","Y Line Frequency","X Coordinate","Y Coordinate","Start Angle","Angle","Radius","Stroke Width","Height","Width","Fill Opacity","Horizontal Movement","Vertical Movement"]:
            #         i.setValidator(QDoubleValidator())
            #     elif i.placeholderText()=="# of Sides":
            #         i.setValidator(QIntValidator())
            try:
                for i in self.properties.propertyStack.currentWidget().findChildren(QLineEdit):
                    eval(
                        "i.setText(" + prop_type + "Save[self." + prop_type + "List.currentRow()][1]['_'.join(i.objectName().split('_')[1:])])")
            except:
                pass

        def changeColor():
            self.properties.currentColor.setStyleSheet("background-color: " + QtWidgets.QColorDialog.getColor().name())

        self.propWindow = QtWidgets.QMainWindow()
        self.properties = Ui_Dialog()
        self.properties.setupUi(self.propWindow)
        self.propWindow.setWindowIcon(QIcon('logo.ico'))
        loadProperties(prop_type)
        self.properties.confirm.clicked.connect(submitProperties)
        self.properties.colorSelect.clicked.connect(changeColor)

        self.propWindow.show()

    def addItem(self):
        if self.treeWidget.currentItem().text(1) in ["Group","Scene"]:
            newItem = QTreeWidgetItem()
            newItem.setText(0,self.testDuplicateName("MyObject"))
            newItem.setText(1,"Object")
            self.treeWidget.currentItem().addChild(newItem)
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText('More information')
            msg.setWindowTitle("Error")
            msg.exec_()

    def delItem(self):
        indices = [self.objList.row(i) for i in self.objList.selectedItems()]
        for i in sorted(indices, reverse=True):
            self.objList.takeItem(i)
            self.objSave.pop(i)
        indices = [self.animList.row(i) for i in self.animList.selectedItems()]
        for i in sorted(indices, reverse=True):
            self.animList.takeItem(i)
            self.animSave.pop(i)

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

    # def render_full(self):
    #     if not self.save_mmtr():
    #         return None
    #     print(self.file_path)
    #     os.chdir("/".join(self.file_path.split("/")[:-1]))
    #     self.convert_to_manim("export")
    #     subprocess.run("manim manim_export.py MyScene")
    #     try:
    #         os.replace("./media/videos/manim_export/1080p60/MyScene.mp4", "./Export.mp4")
    #         shutil.rmtree('media')
    #         shutil.rmtree('__pycache__')
    #     except:
    #         pass

    # def render_preview(self):
    #     if not self.save_mmtr():
    #         return None
    #     os.chdir("/".join(self.file_path.split("/")[:-1]))
    #     self.convert_to_manim("preview")
    #     subprocess.run("manim manim_preview.py MyScene -ql")
    #     try:
    #         os.replace("./media/videos/manim_preview/480p15/MyScene.mp4", "./Preview.mp4")
    #         shutil.rmtree('media')
    #         shutil.rmtree('__pycache__')
    #     except:
    #         pass

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

    def move_up(self):
        obj_row = self.objList.currentRow()
        anim_row = self.animList.currentRow()
        if obj_row > 0:
            self.objList.insertItem(obj_row - 1, self.objList.takeItem(obj_row))
            tmp = self.objSave[obj_row - 1]
            self.objSave[obj_row - 1] = self.objSave[obj_row]
            self.objSave[obj_row] = tmp
            self.objList.setCurrentRow(obj_row - 1)
            self.objNames = [i[2] for i in self.objSave]
        if anim_row > 0:
            self.animList.insertItem(anim_row - 1, self.animList.takeItem(anim_row))
            tmp = self.animSave[anim_row - 1]
            self.animSave[anim_row - 1] = self.animSave[anim_row]
            self.animSave[anim_row] = tmp
            self.animList.setCurrentRow(anim_row - 1)

    def move_down(self):
        obj_row = self.objList.currentRow()
        anim_row = self.animList.currentRow()
        if -1 < obj_row < self.objList.count() - 1:
            self.objList.insertItem(obj_row + 1, self.objList.takeItem(obj_row))
            tmp = self.objSave[obj_row + 1]
            self.objSave[obj_row + 1] = self.objSave[obj_row]
            self.objSave[obj_row] = tmp
            self.objList.setCurrentRow(obj_row + 1)
            self.objNames = [i[2] for i in self.objSave]
        if -1 < anim_row < self.animList.count() - 1:
            self.animList.insertItem(anim_row + 1, self.animList.takeItem(anim_row))
            tmp = self.animSave[anim_row + 1]
            self.animSave[anim_row + 1] = self.animSave[anim_row]
            self.animSave[anim_row] = tmp
            self.animList.setCurrentRow(anim_row + 1)