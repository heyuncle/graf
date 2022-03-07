import math
from manim import *
class Logo(Scene):
    def construct(self):
        text=Text(text=r'¨',font_size=170,fill_opacity=1.0,slant=r'NORMAL',weight=r'NORMAL',stroke_width=0.0,color='#ffffff').shift(RIGHT*0.54+UP*0.86)
        latex=MathTex(r'gra',r'f',font_size=240,color='#ffffff').shift(RIGHT*0.0+UP*0.0)
        group=VGroup(text,latex[1])
        text1=Text(text=r'¨',font_size=280,fill_opacity=1.0,slant=r'NORMAL',weight=r'NORMAL',stroke_width=0.0,color='#ffffff').shift(RIGHT*0.58+UP*2.16)
        latex1=MathTex(r'f',font_size=400,color='#ffffff').shift(RIGHT*0.0+DOWN*0.1)
        group1=VGroup(text1,latex1)
        self.add(group1)
        self.wait(0.4)
        self.play(ReplacementTransform(group1,group), Write(latex[0]),run_time=1.5)
        self.wait(0.4)