from micropython import const
from tempos import g, ac, prtc, buzzer, settings
from graphics import rgb, WHITE, BLACK, GREY, RED, GREEN
from fonts import roboto24, roboto36, bignumfont
from button import RoundButton, ButtonMan
from widgets import ValueDisplay
import math


X = const(120)
Y = const(120)


Hours = 0
Minutes = 0
AlarmState = 0  # 0 = Clear, 1 = Set, 2 = Alarmed
Buzzer_AlarmState = 0 # 0 = Clear, 1 = set the buzzer 
reset_steps_min = 0
reset_steps_hrs = 5
colors = [BLACK, GREEN, RED]


# Note : Alarms are saved as GMT timezone and displayed in local timezone



def to_local(hrs):
    hrs = hrs + settings.timezone
    return hrs + 24 if hrs < 0 else hrs - 24 if hrs >= 24 else hrs


def to_gmt(hrs):
    hrs = hrs - settings.timezone
    return hrs + 24 if hrs < 0 else hrs - 24 if hrs >= 24 else hrs


def drawValue():
    global Hours, Minutes, Buzzer_AlarmState
    color = colors[Buzzer_AlarmState]
    g.setfont(bignumfont)
    s = "{:02}:{:02}".format(Hours, Minutes)
    w, h = g.text_dim(s)
    g.fill_rect(X - w // 2 - 3, Y - h // 2 - 3, w + 6, h + 6, color)
    g.setfontalign(-1, -1)
    g.text(s, X - w // 2, Y - h // 2, WHITE if Buzzer_AlarmState == 0 else GREY)
    g.show()



def adjust_hours(iv):
    global Hours, Buzzer_AlarmState
    if Buzzer_AlarmState != 0:
        return
    Hours += iv
    Hours = 23 if Hours < 0 else 0 if Hours >= 24 else Hours
    drawValue()



def adjust_mins(iv):
    global Minutes, Buzzer_AlarmState
    if Buzzer_AlarmState != 0:
        return
    Minutes += iv
    Minutes = 59 if Minutes < 0 else 0 if Minutes >= 60 else Minutes
    drawValue()




def do_set():
    global Hours, Minutes, Buzzer_AlarmState
    Buzzer_AlarmState = 1
    prtc.set_alarm(Minutes, to_gmt(Hours))
    drawValue()





def do_clear():
    global AlarmState, Buzzer_AlarmState, reset_steps_hrs, reset_steps_min
    prtc.clear_alarm()     
    Buzzer_AlarmState = 0 # Clear the buzzer alarm state
    buzzer.stop()
    prtc.set_alarm(reset_steps_min, to_gmt(reset_steps_hrs)) # Reset the step reset alarm time
    drawValue()




minusH = RoundButton("-", 5, 140, 40, 40, theme=ValueDisplay.theme)
plusH = RoundButton("+", 5, 60, 40, 40, theme=ValueDisplay.theme)
minusM = RoundButton("-", 195, 140, 40, 40, theme=ValueDisplay.theme)
plusM = RoundButton("+", 195, 60, 40, 40, theme=ValueDisplay.theme)

setA = RoundButton("Set", 20, 200, 90, 40, theme=ValueDisplay.theme)
clearA = RoundButton("Clear", 130, 200, 90, 40, theme=ValueDisplay.theme)

buttons = ButtonMan()
buttons.add(plusH)
buttons.add(minusH)
buttons.add(plusM)
buttons.add(minusM)
buttons.add(setA)
buttons.add(clearA)
plusH.callback(adjust_hours, 1)
minusH.callback(adjust_hours, -1)
plusM.callback(adjust_mins, 1)
minusM.callback(adjust_mins, -1)
setA.callback(do_set)
clearA.callback(do_clear)


def app_init():
    global Buzzer_AlarmState, AlarmState, Minutes, Hours  #, reset_steps_hrs, reset_steps_min
    AlarmState, Minutes, Hours = prtc.read_alarm()
    Hours = to_local(Hours)    
    g.setfont(roboto36)
    g.setfontalign(0, -1)
    g.text("Alarm", 120, 10, WHITE)

    if AlarmState == 2:
        if Buzzer_AlarmState == 1:
            buzzer.start()
            
        elif Buzzer_AlarmState == 0:  # It must be the step reset time
            ac.stepInit()
            do_clear()
    
    else:
        drawValue()
        buttons.start()
     
    


def app_end():
    buttons.stop()
    buzzer.stop()
    g.fill(BLACK)
