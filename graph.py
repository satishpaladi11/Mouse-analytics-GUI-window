import math
import collections
import time
from Xlib import display,X
import matplotlib
matplotlib.use('module://kivy.garden.matplotlib.backend_kivy')
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
import matplotlib.pyplot as plt
import struct

PIXEL_MILE_RATIO = 63360*100 # assuming 100 pixels/inch
pixels_to_miles = lambda p: p/PIXEL_MILE_RATIO
Sample = collections.namedtuple('Sample', 'x,y,z')

def calculate_speed(sample1, sample2):
    distance = math.sqrt((sample2.x - sample1.x)**2 + (sample2.y - sample1.y)**2)
    hours = (sample2.z - sample1.z) / 3600.
    return pixels_to_miles(distance)/hours if hours != 0 else 0

fig, ax = plt.subplots()
canvas = fig.canvas
class MyApp(App):

    def build(self):
        graphbox = BoxLayout(orientation = 'horizontal', size_hint=(1, 0.8))
        widgetsbox = BoxLayout(orientation = 'horizontal', size_hint=(1, 0.2))
        totalbox = BoxLayout(orientation = 'vertical')
        self.starttim=time.time()
        self.time=0
        self.data1 = display.Display().screen().root.query_pointer()._data
        self.sample1 = Sample(self.data1['root_x'], self.data1['root_y'],self.time)
        self.speed = calculate_speed(self.sample1,self.sample1)
        self.timearray = [self.time]
        self.speedarray = [self.speed]
        self.texture = Button(text="")
        self.poslabel = Label(text="({0},{1})".format(self.data1['root_x'], self.data1['root_y']))
        self.statlabel = Label(text="",font_size=30)
        graphbox.add_widget(canvas)
        widgetsbox.add_widget(self.poslabel)
        widgetsbox.add_widget(self.texture)
        widgetsbox.add_widget(self.statlabel)
        totalbox.add_widget(graphbox)
        totalbox.add_widget(widgetsbox)
        Clock.schedule_interval(self.update, 0)
        return totalbox

    def update(self, *args):
        if(len(self.speedarray)>=50):
            self.timearray.pop(0)
            self.speedarray.pop(0)
            plt.cla()

        plt.plot(self.timearray, self.speedarray,'-oy',linewidth=1)
        ax.set_title("Mouse speed w.r.to Time",size=16)
        ax.set_xlabel("Time in secs",size=16)
        ax.set_ylabel('Distance in 100pixels per inch',size=16)
        ax.get_yaxis().set_label_coords(0.06,0.3)
        ax.get_xaxis().set_label_coords(0.5,-0.07)
        endtim=time.time()
        self.time=endtim-self.starttim

        data2 = display.Display().screen().root.query_pointer()._data
        sample2 = Sample(data2['root_x'], data2['root_y'], self.time)
        self.speed = calculate_speed(self.sample1,sample2)
        self.sample1 = sample2

        raw = display.Display().screen().root.get_image(data2['root_x'], data2['root_y'], 1, 1, X.ZPixmap, 0xffffffff)
        hexcolor = raw.data
        getcolor = struct.unpack('<' + 'B' * len(hexcolor), hexcolor)

        self.speedarray.append(self.speed)
        self.timearray.append(self.time)

        self.poslabel.text="({0},{1})".format(data2['root_x'], data2['root_y'])

        if(self.speed!=0):
            self.statlabel.text="Active"
            self.statlabel.color = [0,1,0,1]
        else:
            self.statlabel.text="Inactive"
            self.statlabel.color = [1,0,0,1]

        self.texture.background_color = [round(getcolor[2]/90.0,1),round(getcolor[1]/90.0,1),round(getcolor[0]/90.0,1),1]

        canvas.draw()


MyApp().run()