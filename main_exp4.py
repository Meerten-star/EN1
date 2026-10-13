import math
import statistics

from matplotlib import pyplot as plt
from matplotlib.widgets import SpanSelector, RangeSlider


class DataLists:
    def __init__(self, filename):
        self.filename = filename

        self.time = []
        self.R_YBCO = []
        self.R_PT100 = []
        self.temperature = []

        self.readData()
        # create temperature list
        for r in self.R_PT100:
            t = self.rToTemp(r)
            self.temperature.append(t)

    def readData(self):
        file = open(self.filename, "r")
        file.readline() # first two lines are useless
        file.readline()
        line = file.readline()
        removeDotsMap = {ord('.'): None}
        while line:
            data_points = line.strip().split(",")
            t = int(data_points[0].translate(removeDotsMap)) * 10**(-15)
            r = float(data_points[1])
            y = int(data_points[2].translate(removeDotsMap)) * 10**(-15)
            self.time.append(t)
            self.R_YBCO.append(y)
            self.R_PT100.append(r)

            line = file.readline()
        file.close()

    def getYBCOList(self):
        return self.R_YBCO

    def getPT100List(self):
        return self.R_PT100

    def getTemperatureList(self):
        return self.temperature


    def __str__(self):
        return (f"file: {self.filename}\n"
                f"time: {self.time}\n"
                f"ybco: {self.R_YBCO}\n"
                f"pt100: {self.R_PT100}\n"
                f"temp: {self.temperature}")

    @staticmethod
    def getTemperature(avg, dev):
        return DataLists.rToTemp(avg), DataLists.rDevToTempDev(avg, dev)

    @staticmethod
    def rToTemp(r):
        return 30.84 + 2.232*r + 2.43 * 10**(-3) * r**2 - 5.33 * 10**(-6) * r**3

    @staticmethod
    def rDevToTempDev(avg, dev):
        return (2.232 + 4.86 * 10**(-3) * avg - 15.99 * 10**(-6) * avg**2) * dev

    @staticmethod
    def addDev(dev1, dev2):
        return math.sqrt(dev1**2 + dev2**2)



class Selection:
    def __init__(self, data_list):
        self.data = data_list

        self.domain = (0, 0) # selection in kelvin
        self.ybco10 = (0, 0) # avg, dev in ohm
        self.ybco90 = (0, 0) # avg, dev in ohm
        self.temp10 = (0, 0) # avg, dev in kelvin; 10% of resistance
        self.temp90 = (0, 0) # avg, dev in kelvin; 90% of resistance
        self.transitiebreedte = (0, 0) # avg, dev in kelvin

        self.displayAndSelect()
        self.calcTransitiebreedte()


    def displayAndSelect(self):
        def select(xMin, xMax):
            self.domain = (xMin, xMax)
            print(self.domain)

            if self.domain[0] != 0:
                self.calcTransitiebreedte()
                print("\n" + self.__str__())
                fig_txt.set_text(self.__str__())

            fig.canvas.draw_idle()

        # Create function to be called when slider value is changed
        def updateX(val):
            ax.set_xlim(left=val[0], right=val[1])
            fig.canvas.draw_idle()

        def updateY(val):
            ax.set_ylim(bottom=val[0], top=val[1])
            fig.canvas.draw_idle()

        def keyPress(event):
            if event.key == 'escape':
                plt.close()

        ## Measured data
        fig, ax = plt.subplots()
        plt.subplots_adjust(bottom=0.25, right=0.6)

        # DMM data
        x_temp = self.data.getTemperatureList() # temperature
        y_ybco = self.data.getYBCOList()  # ybco resistance

        # make scatter plot
        ax.scatter(x_temp, y_ybco, label="R_YBCO", s=0.5)
        # layout
        ax.set_title("Weerstand van de supergeleider als functie van de temperatuur")
        ax.set_xlabel("Temperatuur (K)")
        ax.set_ylabel("Weerstand supergeleider (Ohm)")
        ax.set_xlim(left=77)

        ## SpanSelection
        # Define selector
        span = SpanSelector(ax, onselect=select, direction="horizontal", useblit=True,
                            props=dict(alpha=0.3, facecolor="tab:blue"),
                            interactive=True, drag_from_anywhere=True, grab_range=1,
                            ignore_event_outside=False,
                            snap_values=x_temp)

        ## Plot sliders
        # Define sliders
        sliders = []
        sliderLabels = ("x", "y")
        sliders.append(
            RangeSlider(plt.axes((0.1, 0.06 + 0.06, 0.7, 0.03)), sliderLabels[0], 75, 90,
                    valstep=x_temp, handle_style=dict(size=12)))
        sliders.append(
            RangeSlider(plt.axes((0.1, 0.06, 0.7, 0.03)), sliderLabels[1], -10, 90,
                    valstep=y_ybco, handle_style=dict(size=12)))

        # Call update function when slider value is changed
        sliders[0].on_changed(updateX)
        sliders[1].on_changed(updateY)

        # Show calculated transition width
        txt = self.__str__()
        fig_txt = plt.figtext(0.65, 0.5, txt, wrap=True, horizontalalignment='left', fontsize=12)

        # fullscreen
        figManager = plt.get_current_fig_manager()
        figManager.full_screen_toggle()

        # escape key press to close window
        fig.canvas.mpl_connect('key_press_event', keyPress)

        # shows the plot, user can now make selection, continues after closing screen.
        plt.show()


    # calculate average and standard deviation of local area around point
    def localDeviation(self, index):
        # local: 10 before, 10 after?
        local = 10
        sliced_ybco = self.data.getYBCOList()[index - local:index + local]
        avg = sum(sliced_ybco) / len(sliced_ybco)
        dev = statistics.stdev(sliced_ybco)
        return avg, dev


    def deviationDMM(self, avg, dev): # add deviation of measurement tools; dmm, pt100 accuracy
        dev_dmm = 0.035 / 100 * avg # 0.035% afwijking
        dev_pt100 = 0.56 # Ohm afwijking
        extra_dev = DataLists.addDev(dev_dmm, dev_pt100)
        return DataLists.addDev(dev, extra_dev)

    def ybcoToTemp(self, avg_ybco, dev_ybco):
        avg_pt100, dev_pt100 = self.ybcoToPt100(avg_ybco, dev_ybco)
        dev_pt100 = self.deviationDMM(avg_pt100, dev_pt100)
        avg_temp = DataLists.rToTemp(avg_pt100)
        dev_temp = DataLists.rDevToTempDev(avg_pt100, dev_pt100)
        return avg_temp, dev_temp

    # LET OP: Geen fit, dus werkt alleen goed voor stijgende data
    def ybcoToPt100(self, avg_ybco, dev_ybco):
        for decimals in range(9, 0 ,-1):
            avg = round(avg_ybco, decimals)
            for index, data_point in enumerate(self.data.getYBCOList()):
                if avg == round(data_point, decimals):
                    dev = DataLists.rDevToTempDev(dev_ybco, data_point - avg_ybco)
                    avg_pt100 = self.data.getPT100List()[index]
                    dev_pt100 = dev * avg_pt100 / avg_ybco
                    return avg_pt100, dev_pt100
        return None, None

    def calcTransitiebreedte(self):
        startDomainIndex = self.data.getTemperatureList().index(self.domain[0])
        endDomainIndex = self.data.getTemperatureList().index(self.domain[1])
        avg1, dev1 = self.localDeviation(startDomainIndex)
        avg2, dev2 = self.localDeviation(endDomainIndex)
        # 10% and 90% transition
        avg10 = 0.90 * avg1 + 0.10 * avg2
        dev10 = DataLists.addDev(0.90 * dev1, 0.10 * dev2)
        avg90 = 0.10 * avg1 + 0.90 * avg2
        dev90 = DataLists.addDev(0.10 * dev1, 0.90 * dev2)
        # dev10 and dev90 ??
        self.ybco10 = (avg10, dev10)
        self.ybco90 = (avg90, dev90)
        # get temp of these resistances
        self.temp10 = self.ybcoToTemp(avg10, dev10)
        self.temp90 = self.ybcoToTemp(avg90, dev90)
        deltaTemp = self.temp90[0] - self.temp10[0]
        deltaDevTemp = DataLists.addDev(self.temp10[1], self.temp90[1])
        self.transitiebreedte = (deltaTemp, deltaDevTemp)


    def __str__(self):
        d = 6 # number of decimals
        return (f"Punt 10% transitie:\n"
                f"{round(self.temp10[0],d)} +- {round(self.temp10[1],d)} K;\n"
                f"{round(self.ybco10[0],d)} +- {round(self.ybco10[1],d)} Ohm\n\n"
                f"Punt 90% transitie:\n"
                f"{round(self.temp90[0],d)} +- {round(self.temp90[1],d)} K;\n"
                f"{round(self.ybco90[0],d)} +- {round(self.ybco90[1],d)} Ohm.\n\n"
                f"Transitiebreedte:\n"
                f"{round(self.transitiebreedte[0],d)} +- {round(self.transitiebreedte[1],d)} K; ")

path = "measured_data_exp4/test_data.csv"
path = "measured_data_exp4/afkoel2.csv"
#path = "measured_data_exp4/opwarmenX3.csv"
data = DataLists(path)
print(data)
selection = Selection(data)


