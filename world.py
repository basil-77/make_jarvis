import torch

import pvporcupine
from pvrecorder import PvRecorder
import argparse
import os
from dotenv import load_dotenv
from faster_whisper import WhisperModel
import threading
import sys
import struct
from llms import get_model
from stt import get_wav_file
from agent import Agent



if __name__=='__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--audio_device_index', help='Index of input audio device.', type=int, default=0)
    parser.add_argument('--audio_buffer_file', help='Absolute path to recorded audio for debugging.', default='data/temp.wav')
    
    args = parser.parse_args()
    
    audio_buffer_file_name = args.audio_buffer_file
    audio_device_index = args.audio_device_index


    device = "cuda" if torch.cuda.is_available() else "cpu"

    load_dotenv()
    api_key = os.getenv('API_KEY')
    REPLICATE_API_KEY = os.getenv('REPLICATE_API_KEY')

    wake_keyword_path = 'wakeup/София_ru_windows_v3_0_0.ppn'
    stop_keyword_path = 'wakeup/Достаточно_ru_windows_v3_0_0.ppn'
    model_path = 'wakeup/porcupine_params_ru.pv'
    porcupine_sensivities = 0.9
    proactive_frequency_sec = 180
    keyword2command = {
        0: 'wakeword',
        1: 'stopword'
    }
   
    porcupine = pvporcupine.create(
        access_key=api_key,
        keyword_paths=[wake_keyword_path], #, stop_keyword_path],
        model_path=model_path,
        sensitivities=[porcupine_sensivities] #, porcupine_sensivities]
    )

    model_audio_transcribe = WhisperModel(model_size_or_path="large-v2", device="cuda", compute_type="float16")
    model_llm = get_model()
  
    # wake_keyword_paths = './wakeup/Kristina_en_windows_v3_0_0.ppn'
    # stop_keyword = 'Stop'
    # porcupine_sensivities = 0.9
   
    # porcupine = pvporcupine.create(
    #     access_key=api_key,
    #     keyword_paths=[wake_keyword_path],
    #     keywords=[stop_keyword,],
    #     sensitivities=[porcupine_sensivities]
    # ) 


    # keywords = list()
    # for x in wake_keyword_path:
    #     keyword_phrase_part = os.path.basename(x).replace('.ppn', '').split('_')
    #     if len(keyword_phrase_part) > 6:
    #         keywords.append(' '.join(keyword_phrase_part[0:-6]))
    #     else:
    #         keywords.append(keyword_phrase_part[0])
    # #keywords.append(stop_keyword)

    recorder = PvRecorder(
        frame_length=porcupine.frame_length,
        device_index=args.audio_device_index)
    recorder.start()

    current_audio_file_name = os.path.abspath(audio_buffer_file_name)
    wav_file = get_wav_file(current_audio_file_name)

    settings = {
        'proactive_frequency_sec': proactive_frequency_sec,
        'wav_file': wav_file,
        'current_audio_file_name': current_audio_file_name,
    }

    agent = Agent(model_llm, model_audio_transcribe, settings)
    agent.start()

    try:
        while agent.is_alive():
            pcm = recorder.read()
            result = porcupine.process(pcm)
            wav_file.writeframes(struct.pack("h" * len(pcm), *pcm))

            if result >= 0:
                agent.event({'type': keyword2command[result], 'result': result})
                wav_file.close()
                os.unlink(current_audio_file_name)
                wav_file = get_wav_file(current_audio_file_name)

    except KeyboardInterrupt:
         print ('Stopping...')
         agent.stop()
    finally:
         recorder.delete()
         porcupine.delete()




