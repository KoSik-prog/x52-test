import ctypes
import ctypes.wintypes
import os
import time
import sys
from colorama import init, Fore, Back, Style
import threading

#LEDs
LED_FIRE_A_RED = 1
LED_FIRE_A_GREEN = 2
LED_FIRE_B_RED = 3
LED_FIRE_B_GREEN = 4
LED_FIRE_D_RED = 5
LED_FIRE_D_GREEN = 6
LED_FIRE_E_RED = 7
LED_FIRE_E_GREEN = 8
LED_TOGGLE_1_2_RED = 9
LED_TOGGLE_1_2_GREEN = 10
LED_TOGGLE_3_4_RED = 11
LED_TOGGLE_3_4_GREEN = 12
LED_TOGGLE_5_6_RED = 13
LED_TOGGLE_5_6_GREEN = 14
LED_POV_2_RED = 15
LED_POV_2_GREEN = 16
LED_CLUTCH_RED = 17
LED_CLUTCH_GREEN = 18


#BUTTONS
LED_FIRE_A = 1
LED_FIRE_B = 3
LED_FIRE_D = 5
LED_FIRE_E = 7
LED_TOGGLE_1_2 = 9
LED_TOGGLE_3_4 = 11
LED_TOGGLE_5_6 = 13
LED_POV_2 = 15
LED_CLUTCH = 17
LED_FIRE = 0
LED_THROTTLE = 19

BUTTONS_LIST = [1, 3, 5, 7, 9, 11, 13, 15, 17, 0, 19]

#MFD LINES
MFD_LINE_1 = 0
MFD_LINE_2 = 2
MFD_LINE_3 = 3

LED_ON = 1
LED_OFF = 0

LED_COLOR_OFF = 4
LED_COLOR_RED = 0
LED_COLOR_GREEN = 1
LED_COLOR_ORANGE = 2

PAGE_0 = 0
PAGE_1 = 1
FLAG_SET_AS_INACTIVE = 0x0
FLAG_SET_AS_ACTIVE = 0x1


class DirectOutput(object):
    devices = []
    defaultDevice = None
    deviceFoundFlag = False

    def __init__(self, application_name):
        init(autoreset=True)
        print(f"\n{Fore.YELLOW}..:: SAITEK X52 PRO Test Script ::..   {Fore.WHITE}{Style.DIM}created by KoSik\n{Style.RESET_ALL}")
        dll_path = os.getcwd() + '\\DirectOutput.dll'
        self.DirectOutputDLL = ctypes.WinDLL(dll_path)
        self.deviceHandle = ctypes.c_void_p()
        self.device_callback_closure = None
        self.dll_path = dll_path
        self.application_name = application_name

        result = self.initialize(application_name)
        if result != 0:
            print(f"Failed to initialize device -> {result}")
        else:
            result = self.registerDeviceCallback(self.device_callback)
            if result != 0:
                print(f"Failed to register device callback -> {result}")

            result = self.enumerate(self.enumerate_callback)
            if result != 0:
                print(f"Failed to enumerate devices -> {result}")
            else:
                startTime = time.time()
                print(f"{Style.DIM}{Fore.GREEN}Wait for device.", end='')
                while self.deviceFoundFlag == False:
                    print(f"{Style.DIM}{Fore.GREEN}.", end='')
                    if time.time() - startTime > 10:
                        print(f"\r{Style.RESET_ALL}Device not found\033[K", end='')
                        sys.exit()
                    time.sleep(0.2)

                if len(self.devices) > 0:
                    print("\rDevice found\033[K")
                    self.set_defaultDevice(self.devices, 0)
                    page_debug_name = "X52_page"
                    result = self.addPage(PAGE_0, page_debug_name, FLAG_SET_AS_ACTIVE)
                    if result != 0:
                        print(f"Failed to add page. HRESULT: {result}")

                    self.setString(PAGE_0, MFD_LINE_1, "..:: SAITEK X52 PRO Test Script ::..")

    def set_defaultDevice(self, devicesList, devNr):
        self.defaultDevice = devicesList[devNr]

    def initialize(self, application_name):
        return self.DirectOutputDLL.DirectOutput_Initialize(
            ctypes.wintypes.LPWSTR(application_name)
        )

    def registerDeviceCallback(self, callback):
        CALLBACK_TYPE = ctypes.WINFUNCTYPE(None, ctypes.c_void_p, ctypes.c_bool, ctypes.c_void_p)
        return self.DirectOutputDLL.DirectOutput_RegisterDeviceCallback(
            CALLBACK_TYPE(callback),
            None
        )

    def enumerate(self, callback):
        CALLBACK_TYPE = ctypes.WINFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p)
        return self.DirectOutputDLL.DirectOutput_Enumerate(
            CALLBACK_TYPE(callback),
            None
        )

    def addPage(self, page_id, page_name, flags):
        return self.DirectOutputDLL.DirectOutput_AddPage(
            ctypes.c_void_p(self.defaultDevice), page_id, ctypes.wintypes.LPWSTR(page_name), flags
        )

    def setString(self, page, index, data):
        size = len(data)
        data_ptr = ctypes.c_wchar_p(data)
        return self.DirectOutputDLL.DirectOutput_SetString(
            ctypes.c_void_p(self.defaultDevice), page, index, size, data_ptr
        )

    def setLed(self, page, index, state):
        return self.DirectOutputDLL.DirectOutput_SetLed(
            ctypes.c_void_p(self.defaultDevice), page, index, state
        )
    
    def setColor(self, page, buttonNr, colorState):
        if buttonNr == LED_FIRE or buttonNr == LED_THROTTLE:
            if colorState == 1 or colorState == 2:
                self.setLed(page, buttonNr, 1)
            else:
                self.setLed(page, buttonNr, 0)
        else:
            if colorState == 0:
                self.setLed(page, buttonNr, 1)
                self.setLed(page, buttonNr+1, 0)
            elif colorState == 1:
                self.setLed(page, buttonNr, 0)
                self.setLed(page, buttonNr+1, 1)
            elif colorState == 2:
                self.setLed(page, buttonNr, 1)
                self.setLed(page, buttonNr+1, 1)
            else:
                self.setLed(page, buttonNr, 0)
                self.setLed(page, buttonNr+1, 0)

    def device_callback(self, hDevice, bAdded, pvContext):
        if bAdded:
            self.devices.append(hDevice)
            print(f"Device added: {hDevice}")
        else:
            print(f"Device removed: {hDevice}")

    def enumerate_callback(self, hDevice, pvContext):
        self.devices.append(hDevice)
        self.deviceFoundFlag = True
        print(f"Device enumerated: {hDevice}")

    def _terminate_program(self):
        print("Initialization timed out. Terminating program...")
        os._exit(1)


x52 = DirectOutput('X52PRO')

print("Test 1 start")
for state in range(4):
    for button in BUTTONS_LIST:
        result = x52.setColor(PAGE_0, button, state)
    time.sleep(2)
    
print("Test 2 start")
for state in range(4):
    for button in BUTTONS_LIST:
        result = x52.setColor(PAGE_0, button, state)
        time.sleep(.3)
print("End")
