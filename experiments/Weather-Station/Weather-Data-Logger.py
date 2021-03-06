'''
ExpEYES-Weather Station GUI

ExpEYES program developed as a part of GSoC-2015 project
Project Tilte: Sensor Plug-ins, Add-on devices and GUI Improvements for ExpEYES

Mentor Organization:FOSSASIA
Mentors: Hong Phuc, Mario Behling, Rebentisch
Author: Praveen Patil
License : GNU GPL version 3

This programme is for logging weather data like temperature,barometric pressure, Relative humidity and wind speed.
'''


import gettext
gettext.bindtextdomain("expeyes")
gettext.textdomain('expeyes')
_ = gettext.gettext


import time, math, sys
if sys.version_info.major==3:
        from tkinter import *
else:
        from Tkinter import *

sys.path=[".."] + sys.path

import expeyes.eyesj as eyes
import expeyes.eyeplot as eyeplot
import expeyes.eyemath as eyemath

WIDTH  = 800   # width of drawing canvas
HEIGHT = 600   # height    

# Connections  
# Humidity sensor HS1101 to IN1 and GND
# Temperature sensor LM-35 to IN2, OD1 and GND
# Barrometric Pressure Sensor  to A2
# Anemometer to A1
# Wind Direction Device  to SEN

class WS:
	tv = [ [], [], [], [], [], [] ]		# Six Lists for Readings time, v  , v1, v2, v3 and v4
	TIMER = 500			# Time interval between reads
	MINY = 0			# Voltage range
	MAXY = 100
	running = False
	MAXTIME = 10

	
	def v2t(self, v):			# Convert Voltage to Temperature for LM35
		
		t = v * 100
		return t

	def start(self):
		self.running = True
		self.index = 0
		p.set_state(10,1)
		self.tv = [ [], [], [], [], [], [] ]
		try:
			self.MAXTIME = int(DURATION.get())
			self.MINY = int(TMIN.get())
			self.MAXY = int(TMAX.get())
			
			g.setWorld(0, self.MINY, self.MAXTIME, self.MAXY,_('Time in second'),_('Data'))
			self.TIMER = int(TGAP.get())
			Total.config(state=DISABLED)
			Dur.config(state=DISABLED)
			self.msg(_('Starting the Measurements'))
			root.after(self.TIMER, self.update)
		except:
			self.msg(_('Failed to Start'))
			pass

	def stop(self):
		self.running = False
		Total.config(state=NORMAL)
		Dur.config(state=NORMAL)
		self.msg(_('User Stopped the measurements'))


	def update(self):
		if self.running == False:
			return
		t,v = p.get_voltage_time(4) # Read IN2 for temperature sensor
		if len(self.tv[0]) == 0:
			self.start_time = t
			elapsed = 0
		else:
			elapsed = t - self.start_time   # To be done : make changes to have system time
		self.tv[0].append(elapsed)
		
		temp = self.v2t(v)
		self.tv[1].append(temp)

		cap = p.measure_cap()		
		
		if cap< 180: 
         		RH= (cap -163)/0.3
		elif 180<cap<186: 
        		RH= (cap -160.25)/0.375
		elif 186<cap<195: 
        		RH= (cap -156.75)/0.425
		else:
			RH= (cap -136.5)/0.65

		self.tv[2].append(RH)


		v1 = p.get_voltage(1) 				# Read A1 for wind speed  

		v2 = p.get_voltage(2)				# Read A2 for Wind direction
		v3 = p.get_voltage(5)				# Read SEN for Barrometric Pressure

		# calculations of various parameters from v1 v2 and v3 to be done. 
		
		self.tv[3].append(v1)
		self.tv[4].append(v2)
		self.tv[5].append(v3)

		if len(self.tv[0]) >= 2:
			g.delete_lines()

			g.line(self.tv[0], self.tv[1],1)    # red line - temperature in celsius scale
			g.line(self.tv[0], self.tv[2],2)	# blue line - Relative Humidity in %
			g.line(self.tv[0], self.tv[3],0)	# black line - A1
			g.line(self.tv[0], self.tv[4],5)	# green line -A2
			g.line(self.tv[0], self.tv[5],6)	#yellow line - SEN
			
		if elapsed > self.MAXTIME:
			self.running = False
			Total.config(state=NORMAL)
			Dur.config(state=NORMAL)
			self.msg(_('Completed the Measurements'))
			return 
		root.after(self.TIMER, self.update)

	def save(self):
		try:
			fn = filename.get()
		except:
			fn = 'weather-station.dat'
		p.save([self.tv],fn)
		self.msg(_('Data saved to %s')%fn)

	def clear(self):
		if self.running == True:
			return
		self.tv = [ [], [], [], [], [], [] ]
		g.delete_lines()
		self.msg(_('Cleared Data and Trace'))

	def msg(self,s, col = 'blue'):
		msgwin.config(text=s, fg=col)

	def quit(self):
		#p.set_state(10,0)
		sys.exit()

p = eyes.open()
p.disable_actions()

root = Tk()
Canvas(root, width = WIDTH, height = 5).pack(side=TOP)  

g = eyeplot.graph(root, width=WIDTH, height=HEIGHT, bip=False)
pt = WS()

cf = Frame(root, width = WIDTH, height = 10)
cf.pack(side=TOP,  fill = BOTH, expand = 1)

b3 = Label(cf, text = _('Read Every'))
b3.pack(side = LEFT, anchor = SW)
TGAP = StringVar()
Dur =Entry(cf, width=5, bg = 'white', textvariable = TGAP)
TGAP.set('1000')
Dur.pack(side = LEFT, anchor = SW)
b3 = Label(cf, text = _('mS,'))
b3.pack(side = LEFT, anchor = SW)
b3 = Label(cf, text = _('for total'))
b3.pack(side = LEFT, anchor = SW)
DURATION = StringVar()
Total =Entry(cf, width=5, bg = 'white', textvariable = DURATION)
DURATION.set('100')
Total.pack(side = LEFT, anchor = SW)
b3 = Label(cf, text = _('Seconds.'))
b3.pack(side = LEFT, anchor = SW)

b3 = Label(cf, text = _('Range'))
b3.pack(side = LEFT, anchor = SW)
TMIN = StringVar()
TMIN.set('0')
Tmin =Entry(cf, width=5, bg = 'white', textvariable = TMIN)
Tmin.pack(side = LEFT, anchor = SW)
b3 = Label(cf, text = _('to,'))
b3.pack(side = LEFT, anchor = SW)
TMAX = StringVar()
TMAX.set('100')
Tmax =Entry(cf, width=5, bg = 'white', textvariable = TMAX)
Tmax.pack(side = LEFT, anchor = SW)
b3 = Label(cf, text = _('C. '))

b3 = Button(cf, text = _('SAVE to'), command = pt.save)
b3.pack(side = LEFT, anchor = SW)
b3.pack(side = LEFT, anchor = SW)
filename = StringVar()
e1 =Entry(cf, width=15, bg = 'white', textvariable = filename)
filename.set('temperature.dat')
e1.pack(side = LEFT, anchor = SW)

cf = Frame(root, width = WIDTH, height = 10)
cf.pack(side=TOP,  fill = BOTH, expand = 1)

cf = Frame(root, width = WIDTH, height = 10)
cf.pack(side=TOP,  fill = BOTH, expand = 1)
e1.pack(side = LEFT)

b3 = Label(cf, text = _(' RED Line - Temperature in Celsius'), fg = 'red')
b3.pack(side = LEFT, anchor = SW)
b3 = Label(cf, text = _('    BLUE Line - Relative Humidity in %'), fg = 'blue') # Add info for other data lines
b3.pack(side = LEFT, anchor = SW)

b5 = Button(cf, text = _('QUIT'), command = pt.quit)
b5.pack(side = RIGHT, anchor = N)
b4 = Button(cf, text = _('CLEAR'), command = pt.clear)
b4.pack(side = RIGHT, anchor = N)
b1 = Button(cf, text = _('STOP'), command = pt.stop)
b1.pack(side = RIGHT, anchor = N)
b1 = Button(cf, text = _('START'), command = pt.start)
b1.pack(side = RIGHT, anchor = N)

mf = Frame(root, width = WIDTH, height = 10)
mf.pack(side=TOP)
msgwin = Label(mf,text=_('Message'), fg = 'blue')
msgwin.pack(side=LEFT, anchor = S, fill=BOTH, expand=1)


eyeplot.pop_image('pics/image-name.png', _('---'))  # save the image in the same directory as of the program
root.title(_('ExpEYES- Weather Station Data Logger'))
root.mainloop()
