import struct
import math
import pyaudio
import wave

def rms(data):
    count = len(data) // 2
    format_str = "<" + "h" * count
    shorts = struct.unpack_from(format_str, data)

    sum_squares = 0.0
    for sample in shorts:
        sum_squares += sample * sample

    if count == 0:
        return 0

    return math.sqrt(sum_squares / count)


class VoiceRecorder:
    CHUNK = 1024
    RATE = 16000
    FORMAT = pyaudio.paInt16
    CHANNELS = 1

    def __init__(self, silence_limit: float, threshold: int, output_name: str):
        self.silence_limit =  silence_limit
        self.threshold = threshold
        self.output_name = output_name

    def record(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=VoiceRecorder.FORMAT,
                        channels=VoiceRecorder.CHANNELS,
                        rate=VoiceRecorder.RATE,
                        input=True,
                        frames_per_buffer=VoiceRecorder.CHUNK)

        frames = []

        print("Start recording, please speak...")

        silence_counter = 0
        loud_counter = 0
        while True:
            data = stream.read(VoiceRecorder.CHUNK)
            frames.append(data)
            current_rms = rms(data)
            if current_rms < self.threshold:
                silence_counter += 1
            else:
                silence_counter = 0
                loud_counter = loud_counter + 1

            if silence_counter * (VoiceRecorder.CHUNK / VoiceRecorder.RATE) > self.silence_limit:
                break
        stream.stop_stream()
        stream.close()
        p.terminate()

        print("Recording is over.")

        wf = wave.open(self.output_name, 'wb')
        wf.setnchannels(VoiceRecorder.CHANNELS)
        wf.setsampwidth(p.get_sample_size(VoiceRecorder.FORMAT))
        wf.setframerate(VoiceRecorder.RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        return loud_counter > 0
        
