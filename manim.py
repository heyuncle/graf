import math
from manim import *
class MyScene(Scene):
    def construct(self):
        MyObject=Rectangle(height=1.0,width=1.0,grid_xstep=1.0,grid_ystep=1.0,color='#ffffff').shift(RIGHT*0.0+UP*0.0)
        self.add(MyObject,MyObject)
        self.wait()