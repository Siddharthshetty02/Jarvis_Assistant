import asyncio
import edge_tts
import pygame
import os
import uuid
import io

# Init audio modules
pygame.init()
pygame.mixer.init()

# Global stop flag
voice_stop_flag = {"stop": False}

# Core async speaker
# Core async speaker (in-memory, no file saved)
async def speak_async(text, voice="en-US-GuyNeural"):
    try:
        communicate = edge_tts.Communicate(text, voice)
        mp3_data = io.BytesIO()

        async for msg in communicate.stream():
            if voice_stop_flag["stop"]:
                return
            if msg["type"] == "audio":
                mp3_data.write(msg["data"])

        if voice_stop_flag["stop"]:
            return

        # Reset buffer position to start
        mp3_data.seek(0)

        # Play the MP3 from memory
        pygame.mixer.music.load(mp3_data)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            if voice_stop_flag["stop"]:
                pygame.mixer.music.stop()
                break
            await asyncio.sleep(0.1)

    except Exception as e:
        print(f"[ERROR in speak_async]: {e}")

# Simulated streaming voice: split into sentences
async def speak_streamed_text(text):
    voice_stop_flag["stop"] = False
    sentences = text.split(". ")
    for sentence in sentences:
        if voice_stop_flag["stop"]:
            break
        await speak_async(sentence + ".")

# Wrapper for Streamlit-safe calling
def safe_speak(text):
    try:
        asyncio.run(speak_streamed_text(text))
    except RuntimeError:
        loop = asyncio.get_event_loop()
        loop.create_task(speak_streamed_text(text))

# Stop everything now
def stop_audio():
    voice_stop_flag["stop"] = True
    try:
        pygame.mixer.music.stop()
    except:
        pass
