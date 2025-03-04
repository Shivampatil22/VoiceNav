import cv2 as cv
import mediapipe as mp
import pyautogui
import numpy as np
import speech_recognition as sp
import threading
import subprocess
import psutil
import os
import tkinter as tk
end_program=False
root = tk.Tk()
root.geometry("200x60+1400+100")  # Adjust size and position as needed
label_text = tk.StringVar()
label = tk.Label(root, textvariable=label_text, font=("Helvetica", 12))
label.pack()

class VoiceAssistant:
   
    def __init__(self):
     
        self.recognizer = sp.Recognizer()

    def listen(self):
        
        
        with sp.Microphone() as mic:
          
            print("Listening...")
            label_text.set("Listening...")
            self.recognizer.pause_threshold=1
            # Adjust for ambient noise
            self.recognizer.adjust_for_ambient_noise(mic, duration=0.1)
            
            try:
                # Listen for speech with a timeout of 2 seconds
                audio = self.recognizer.listen(mic)
                # Recognize the audio and return the result
                return self.recognizer.recognize_google(audio).lower()
            except sp.WaitTimeoutError:
                label_text.set("No speech detected after 2 seconds.")
                print("No speech detected after 2 seconds.")
                return ""  # Return an empty string if no speech is detected

    def terminate(self):
        global end_program
        end_program = True
       
  
    def tabs(self):
        pyautogui.keyDown("alt")
        pyautogui.press("tab")
    def change(self):
        pyautogui.press("tab") 
    def done (self):
        pyautogui.keyUp("alt")
    def last_tab(self):
        pyautogui.keyDown("alt")
        pyautogui.keyDown("tab")
        pyautogui.keyDown("tab")
        pyautogui.keyDown("tab")
        pyautogui.keyUp("alt")
        

       
    def execute_command(self, command):
        if command.startswith("open"):
            application_name = command[len("open "):]
            self.open_application(application_name)
        elif command.startswith("close"):
            application_name = command[len("close "):]
            self.close_application(application_name)
        elif command.startswith("type"):
            sentence_to_type = command[len("type "):]
            pyautogui.typewrite(sentence_to_type)
        elif command == "click":
            pyautogui.click()
        elif command == "erase":
            self.erase_last_word()
        elif command == "delete":
            self.erase_line()
        elif command == "select":
            self.select_line()
        elif command == "copy":
            self.copy_line()
        elif command == "paste":
            self.paste_line()
        elif command=="terminate":
            self.terminate()
        elif command=="last tab":
            self.last_tab()
    def open_application(self, application_name):
        username = os.getlogin()
        applications = {
            "google": r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            "file": r"C:\Windows\explorer.exe",
            "calculator": r"C:\Windows\System32\calc.exe",
            "notepad":  r"C:\Windows\System32\notepad.exe",  
            "code": r"C:\Users\{}\AppData\Local\Programs\Microsoft VS Code\Code.exe".format(username)
        }

        if application_name.lower() in applications:
            application_path = applications[application_name.lower()]
            subprocess.Popen([application_path], shell=True)
            print(f"{application_name} opened successfully.")
        else:
            print(f"Application '{application_name}' not recognized.")

    def close_application(self, application_name):
        for process in psutil.process_iter():
            try:
                if application_name.lower() in process.name().lower():
                    process.terminate()
                    print(f"{application_name} closed successfully.")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

    def erase_last_word(self):
        pyautogui.hotkey("ctrl", "backspace")
        print("Last word erased.")
    def select_line(self):
        pyautogui.click()
        pyautogui.keyDown('shift')
        pyautogui.press('home')

    def erase_line(self):
        pyautogui.click()
        pyautogui.press('backspace')
        pyautogui.keyUp('shift')

    def copy_line(self):
        pyautogui.click()
        pyautogui.hotkey("ctrl","c")
        pyautogui.keyUp('shift')
    def paste_line(self):
        pyautogui.click()
        pyautogui.hotkey("ctrl","v")
    def run(self):
       
        while not end_program:
            try:
                command = self.listen()
                label_text.set(command)
                print(command)
                self.execute_command(command)
            except sp.UnknownValueError:
                label_text.set("Sorry, I couldn't understand what you said. Please try again.")
                print("Sorry, I couldn't understand what you said. Please try again.")
            except sp.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))
            except KeyboardInterrupt:
                print("Voice assistant terminated by user.")
                break

class WebcamController:
    def __init__(self):
        
        self.smoothing = 7
        self.plocX, self.plocY = 0, 0
        self.mpDraw = mp.solutions.drawing_utils
        self.mpFaceMesh = mp.solutions.face_mesh
        self.faceMesh = self.mpFaceMesh.FaceMesh(static_image_mode=False, max_num_faces=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.cap = cv.VideoCapture(0)
        self.cap.set(3, 640)
        self.cap.set(4, 480)
        self.wScr, self.hScr = pyautogui.size()

    def run(self):
        global end_program
     
        while not end_program:
            success, img = self.cap.read()

            img = cv.flip(img, 1)
            imgRGB = cv.cvtColor(img, cv.COLOR_BGR2RGB)
            result = self.faceMesh.process(imgRGB)

            if result.multi_face_landmarks:
                for faceLms in result.multi_face_landmarks:
                    for id, lm in enumerate(faceLms.landmark):
                        h, w, c = img.shape
                        cx, cy = int(lm.x * w), int(lm.y * h)

                        if id == 4:
                            x1 = np.interp(cx, (185, w - 185), (0, self.wScr))
                            y1 = np.interp(cy, (185, h - 185), (0, self.hScr))
                            cLocX = self.plocX + (x1 - self.plocX) / self.smoothing
                            cLocY = self.plocY + (y1 - self.plocY) / self.smoothing

                            try:
                                if 0 <= cLocX <= self.wScr and 0 <= cLocY <= self.hScr:
                                    pyautogui.moveTo(cLocX, cLocY) 
                            except pyautogui.FailSafeException:
                                print("PyAutoGUI fail-safe triggered. Mouse moved to a corner of the screen.")

                            cv.circle(img, (cx, cy), 5, (0, 0, 255), cv.FILLED)
                            self.plocX = cLocX
                            self.plocY = cLocY
            
            cv.imshow("me", img)
          
            if end_program:
                self.cap.release()
                
                cv.destroyAllWindows()
                root.destroy()
                break

            if cv.waitKey(1) & 0xFF == ord('q'):
                break

def check_termination():
    global end_program
    while not end_program:
        if cv.waitKey(1) & 0xFF == ord('q'):

            end_program = True
          
            break


if __name__ == "__main__":
    voice_assistant = VoiceAssistant()
    webcam_controller = WebcamController()

    voice_thread = threading.Thread(target=voice_assistant.run)
    webcam_thread = threading.Thread(target=webcam_controller.run)
    

    voice_thread.start()
    webcam_thread.start()
    # # Then, use threading for this function
    # termination_thread = threading.Thread(target=check_termination)
    # termination_thread.start()
    root.mainloop()
    voice_thread.join()
    webcam_thread.join()

    cv.destroyAllWindows()
