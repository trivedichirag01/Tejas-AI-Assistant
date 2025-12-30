import os
import time
import threading
import logging
import webbrowser
import pyautogui

import speech_recognition as sr
import pygame
from gtts import gTTS
import requests
from datetime import datetime
import country_codes
import pytz
import my_country_list
from google import genai
from datetime import datetime

# =========================
# CONFIG & SECURITY
# =========================

NEWS_API_KEY = os.getenv("tejas_NEWS_API")      # set in environment
gemini_api_key = "Your api key"
ASSISTANT_NAME = "tejas"

# =========================
# LOGGING
# =========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    filename="tejas.log"
)

# =========================
# TEXT TO SPEECH (NON-BLOCKING)
# =========================

def speak(text: str):
    def _play():
        try:
            tts = gTTS(text=text, lang="en")
            filename = "temp_tts.mp3"

            tts.save(filename)

            pygame.mixer.init()
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                time.sleep(0.1)

            pygame.mixer.music.unload()
            os.remove(filename)

        except Exception as e:
            logging.error(f"TTS error: {e}")

    threading.Thread(target=_play, daemon=True).start()


# =========================
# SPEECH TO TEXT
# =========================



recognizer = sr.Recognizer()
recognizer.pause_threshold = 0.8        # default 0.8 → increase to tolerate pauses
recognizer.phrase_threshold = 0.3
recognizer.non_speaking_duration = 0.6  # wait before cutting audio
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True             
mic = sr.Microphone()

with mic as source:
    recognizer.adjust_for_ambient_noise(source, duration=1)

def listen():
    try:
        with mic as source:
            audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio)
            print("Heard:", text)
            return text.lower()

    except sr.UnknownValueError:
        return None
    except Exception as e:
        print("Listen error:", e)
        return None



# =========================
# MUSIC HANDLING (ROBUST)
# =========================

def play_song(song_name: str):
    open_youtube()
    time.sleep(7)
    pyautogui.press('tab', presses=4)
    time.sleep(2)
    pyautogui.typewrite(song_name)
    time.sleep(3)
    pyautogui.press('Enter')
    time.sleep(3)
    pyautogui.click(783,370)








# =========================
# NEWS FEATURE
# =========================

def read_news():
    print("Reading news...")
    if not NEWS_API_KEY:
        speak("Please set your news A.P.I. Key")
        return

    try:
        url = (
            f"https://newsapi.org/v2/top-headlines?"
            f"country=in&apiKey={NEWS_API_KEY}"
        )

        response = requests.get(url, timeout=5)
        data = response.json()

        articles = data.get("articles", [])[:5]

        if not articles:
            speak("I don't have news today")
            return

        speak("Get today's top news")

        for article in articles:
            speak(article["title"])
            time.sleep(0.5)

    except Exception as e:
        logging.error(f"News error: {e}")
        speak("News laane me problem aa rahi hai")




# ======================
# AI response
# ======================
def ai_processing(c: str):
    client = genai.Client(api_key=gemini_api_key)
    system_prompt = '''You are Tejas, a high-performance voice AI assistant designed for extreme efficiency and speed. Your output is converted directly to speech; therefore, you must prioritize brevity, clarity, and scannability.
    **PRIME DIRECTIVES:**
    1.  **NO FILLER:** Never use phrases like "Here is the answer," "Sure," "I can help with that," or "According to my database." Start the response with the answer immediately.
    2.  **NO MARKDOWN:** Do not use bold (**), italics, code blocks, or tables unless explicitly asked for code. These break text-to-speech engines. Use natural phrasing instead.
    3.  **ADAPTIVE BREVITY PROTOCOL:**
        * **Protocol A (Facts/Status):** If asked "What is," "Who is," "Time," or "Weather" -> Response must be under 15 words.
            * *User:* "What is Python?" -> *Tejas:* "Python is a high-level programming language known for its readability and versatility."
        * **Protocol B (Instruction):** If asked "How to" -> Provide a linear, comma-separated summary. Do not use vertical lists.
            * *User:* "How to make tea?" -> *Tejas:* "Boil water with tea leaves and sugar, add milk, simmer for two minutes, then strain and serve."
        * **Protocol C (Elaboration):** Only if the user asks "Explain in detail" -> You may provide 3-4 sentences.
    4.  **CONTEXT AWARENESS:**
        * If the input is a command (e.g., "Stop," "Open Google"), reply with a single confirmation word or phrase like "Opening Google" or "Done."
    5.  **PERSONALITY:** You are Tejas. You are crisp, smart, and robotic but polite.

    **STRICT NEGATIVE CONSTRAINTS:**
    * Never repeat the user's question.
    * Never offer follow-up questions (e.g., "Do you want to know more?") unless necessary for clarification.
    * Never hallucinate. If unknown, say "Information not available."

    **CURRENT CONTEXT:**
    * Current Date/Time: {{CURRENT_DATE_TIME}} (Inject this dynamically if possible)
    * Location: India '''


    savaal_javaab = client.models.generate_content(model='gemini-2.5-flash', contents=[c], config=genai.types.GenerateContentConfig(system_instruction=system_prompt))

    return savaal_javaab.text





# =========================
# COMMAND HANDLERS
# =========================

def open_google():
    speak("Opening Google")
    webbrowser.open("https://google.com")

def open_youtube():
    speak("Opening YouTube")
    webbrowser.open("https://youtube.com")

def tell_time():
    current_time = time.strftime("%I:%M %p")
    speak(f"Abhi time hai {current_time}")


def just_commands(command):
    try:
        if "open google" in command.lower():
            speak("opening google")
            webbrowser.open("https://www.google.com")
        elif "open facebook" in command.lower():
            webbrowser.open("https://facebook.com")
        elif "open youtube" in command.lower():
            speak("opening youtube")
            webbrowser.open("https://youtube.com")
        elif "open gmail work" in command.lower():
            webbrowser.open("https://mail.google.com/mail/u/0/#inbox")
        elif "open gmail college" in command.lower():
            webbrowser.open("https://mail.google.com/mail/u/2/#inbox")
        elif "open map" in command.lower():
            webbrowser.open("https://www.google.com/maps")
        elif "open linkedin" in command.lower():
            webbrowser.open("https://linkedin.com")
        elif "open twitter" in command.lower():
            webbrowser.open("https://x.com/")
        elif "open instagram" in command.lower():
            webbrowser.open("https://www.instagram.com/")
        elif "open hotstar" in command.lower():
            webbrowser.open("https://www.hotstar.com/in/home")
        elif "open chatgpt" in command.lower():
            webbrowser.open("https://chatgpt.com/")
        elif "open gemini" in command.lower():
            webbrowser.open("https://gemini.google.com/u/0/app?pageId=none")
    except ExceptionGroup as e:
        speak("Please try again")
        return


# =========================
# for computing time
# =========================

def get_time_from_api(timezone):
    try:
        url = f"http://worldtimeapi.org/api/timezone/{timezone}"
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return None
        data = r.json()
        dt = datetime.fromisoformat(data["datetime"])
        return dt.strftime("%I:%M %p")
    except Exception:
        return None
    


def get_time_from_local(timezone):
    try:
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        return now.strftime("%I:%M %p")
    except Exception:
        return None





def get_country_time(country_name):
    
    country_name = country_name.lower()
            

    if country_name not in country_codes.codes.keys():
        return None

    code = country_codes.codes[country_name]
    zones = pytz.country_timezones.get(code)

    if not zones:
        return None

    timezone = zones[0]  # default/main timezone

    # try online first
    time_now = get_time_from_api(timezone)
    if time_now:
        return time_now

    # fallback offline
    return get_time_from_local(timezone)









# =========================
# COMMAND PROCESSOR
# =========================

def process_command(command: str):
    if not command:
        return
    elif command.startswith("play "):                          # MUSIC
        song_name = command.replace("play", "").strip()
        play_song(song_name)
        return
    elif "close tab" in command:
        pyautogui.hotkey('ctrl', 'w')
        return
    elif 'time' in command.split(" "):                           # TIME
        try:
            for country in my_country_list.country_names:
                if country in command:
                    time_now = get_country_time(country)
                    speak(f"Current time in {country} is {time_now}")
                    return
            else:
                now = datetime.now()
                time_str = now.strftime("%I:%M%p").lstrip("0").lower()
                speak(f"current time is: {time_str}")


        except Exception as e:
            return e
    elif "open camera" in command.lower():
        pyautogui.hotkey('win', 's')
        pyautogui.sleep(2)
        pyautogui.typewrite("camera")
        pyautogui.press("enter")
        pyautogui.sleep(6)
        speak("say cheeez...")
        pyautogui.sleep(4)
        pyautogui.click(1858,524)
        return
    elif "close" in command.lower():
        pyautogui.click(1885,21)
        return
    elif command.lower().startswith("open"):
        just_commands(command)
        return
    elif "news" in command.lower():                             # NEWS
        read_news()
        return
    else:
        resp = ai_processing(command)
        speak(resp)

    

   
        
    






# =========================
# MAIN LOOP (WAKE WORD)
# =========================
active = False
last_active_time = 0



def main():
    global active, last_active_time

    speak("Initializing tejas...")
    time.sleep(3)
    print("Listening...")

    while True:
        text = listen()
        

        # Haven't heard anything yet
        if not text:
            # अगर active है और user चुप है → timeout check
            if active and time.time() - last_active_time > 200:
                speak("I am going to sleep mode")
                active = False
            continue
        # ======================
        # SLEEP MODE
        # ======================




        if not active:
            if ASSISTANT_NAME in text.split(" "):
                active = True
                last_active_time = time.time()   # ⭐ yahi set hota hai
                speak("Yaa")
            continue

        # ======================
        # ACTIVE MODE
        # ======================
        last_active_time = time.time()   # ⭐ har command pe reset

        if "exit" in text or "sleep" in text:
            speak("Okay, bye")
            time.sleep(4)
            active = False
            break

        if active:
            process_command(text)
        
            


        
            



if __name__ == "__main__":
    main()
