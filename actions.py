from datetime import datetime
import threading

from helpers import time_it
from stt import transcribe_audio_file
from llms import get_answer_from_llm, get_random_ice_break
from tts import do_tts, interrupt_tts

@time_it
def answer_action(model_llm,
                   model_transcribe,
                   audio_file_name,
                   st_memory=None,
                   lt_memory=None,
                   current_transript=None):
    if not current_transript:
        print(f'Keyword detected {datetime.now()}')
        print('---1')
        transcription = transcribe_audio_file(model_transcribe, audio_file_name)
        print('---2')
    else:
        transcription = current_transript
    print('---3')        
    print (transcription)
    answer = get_answer_from_llm(model_llm, transcription, st_memory=st_memory, lt_memory=lt_memory)
    print('---4')

    if st_memory is not None:
        print('before', st_memory)
        st_memory.append(('user', transcription))
        st_memory.append(('assistant', answer))
        print('after', st_memory)

    print (answer)
    interrupt_tts()
    do_tts(answer)

@time_it
def proactive_action(model_llm,
                  st_memory=None,
                  lt_memory=None):
    answer = get_random_ice_break(model_llm, st_memory=st_memory, lt_memory=lt_memory)

    if st_memory is not None:
        st_memory.append(('assistant', answer))

    print(answer)
    do_tts(answer)

