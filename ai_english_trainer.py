import asyncio
from transcriber import Transcriber
from text_to_speech import TextToSpeech
from voice_recorder import VoiceRecorder
from playsound import playsound
import websockets

async def start():
    silence_limit = 3.0
    threshold = 200
    recorded_filename = "input.mp3"
    tts_output_filename = "tts_out.mp3"
    voice_recorder = VoiceRecorder(silence_limit, threshold, recorded_filename)
    transcriber = Transcriber(recorded_filename)
    text_to_speech = TextToSpeech(tts_output_filename)    
    deep_seek_service_uri = "ws://localhost:8080/"  # deepseek electron app

    # Read a start prompt from the file
    file = open("starter-prompt.txt", "r")
    start_prompt = file.read()
    
    async with websockets.connect(deep_seek_service_uri) as deep_seek_service:
        await deep_seek_service.send(start_prompt)
        response = await deep_seek_service.recv()

        text_to_speech.save(response)
        playsound(tts_output_filename)

        while True:
            if not voice_recorder.record():
                print("No speech detected in audio stream, please try again.")
                continue

            user_text = transcriber.transcribe()
            if not user_text.strip():
                print("No speech detected, please try again.")
                continue

            print(f"Speech detected: {user_text}")
            await deep_seek_service.send(user_text)

            deepseek_response = await deep_seek_service.recv()
            print(f"Deepseek response: {response}")

            text_to_speech.save(deepseek_response)
            playsound(tts_output_filename)

asyncio.get_event_loop().run_until_complete(start())