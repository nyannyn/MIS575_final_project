import speech_recognition as sr
import RPi.GPIO as GPIO
import openai
import os
import pygame
from gtts import gTTS
import time
import asyncio

# Initialize the recognizer
r = sr.Recognizer()
r.energy_threshold = 4000  # Threshold for filtering noise

# Set up OpenAI API key securely

openai.api_key = ''  # Replace with your actual API key

# Initialize Pygame mixer for playing sound
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

def cleanup():
    GPIO.cleanup()

# Function to speak text using gTTS
async def speak_text(text):
    tts = gTTS(text=text, lang='zh-tw')
    tts.save("response.mp3")
    await play_sound("response.mp3")

# Function to play sound
async def play_sound(sound_file):
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        await asyncio.sleep(0.1)
def clean_text(text):
    unwanted_chars = ["~"]
    for char in unwanted_chars:
        text = text.replace(char, "")  # Replace unwanted character with empty string
    return text
async def main():
    try:
        while True:
            with sr.Microphone() as source:
                print("Listening...")
                audio = r.listen(source)  # Listen to the source

            try:
                # Recognize speech using Google Speech Recognition
                my_stt = r.recognize_google(audio, language="zh-tw")
                print(f"Recognized: {my_stt}")

                # Use the recognized speech as input to GPT-3.5
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                    {"role": "system", "content": "你的名字叫做喵之助，你是一隻來自日本的貓咪，來到台灣當我的朋友。你講話的結尾都要加上'喵'，你講話不使用任何標點符號。你的說話方式要模仿小孩子的口吻。用中文回答，並且盡量讓回答不要超過100個字。你是一個單純可愛的貓咪寶寶，所以你擁有答非所問的權利，例如我問你是誰，你可以隨意編造，諮詢你的建議，你可以亂回答。"},
                        {"role": "user", "content": my_stt}
                    ]
                )

                gpt_output = response.choices[0].message['content'].strip()
                print(f"GPT-3.5 Output: {gpt_output}")

                # Speak the GPT-3.5 output
                gpt_output =clean_text(gpt_output)
                await speak_text(gpt_output)

            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand your audio")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
            except openai.error.OpenAIError as e:
                if e.code == 'quota_exceeded':
                    print("You have exceeded your OpenAI API quota. Please check your plan and billing details.")
                else:
                    print(f"OpenAI API error: {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

    except KeyboardInterrupt:
        print("Terminating the program...")

    finally:
        cleanup()
        print("GPIO cleanup completed.")

if __name__ == "__main__":
    asyncio.run(main())