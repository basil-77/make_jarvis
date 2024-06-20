import threading
import time
import random

from actions import answer_action, proactive_action


class Agent:

    def __init__(self, model_llm, model_audio_transcribe, settings):
        '''
        
        '''

        self.threads = []
        self.stop_event = threading.Event()

        self.model_llm = model_llm
        self.moel_audio_transcribe = model_audio_transcribe
        self.wav_file = settings['wav_file']
        self.current_audio_file_name = settings['current_audio_file_name']
        self.proactive_frequency_sec = settings['proactive_frequency_sec']
        self.min_freq = settings.get('proactive_frequency_sec', 30)
        self.max_freq = self.min_freq * 2
        self.dialog_lock = threading.Lock()
        self.dialog_history = []

        self.proactive_thread = threading.Thread(target=self.proactive_actions_thread)
        self.proactive_thread.daemon = True
        self.threads.append(self.proactive_thread)

        #self.passive_thread = threading.Thread(target=self.passive_agent_thread)
        #self.passive_thread.daemon = True
        #self.threads.append(self.passive_thread)
        
        #self.debug_thread = threading.Thread(target=self.memory_debug_thread)
        #self.debug_thread.daemon = True
        #self.threads.append(self.debug_thread)
        

    def start(self):
        for thread in self.threads:
            thread.start()
        print('Listening ... (press Ctrl+C to exit)')

    def stop(self):
        self.stop_event.set()
        try:
            for thread in self.threads:
                thread.join()
        except KeyboardInterrupt:
            print ('Keyboard interrupted')

    def memory_debug_thread(self):
        while not self.stop_event.is_set():
            time.sleep(30)
            for i, (role, message) in enumerate(self.dialog_history):
                print(f'{i} {role}: {message}')        

    def proactive_actions_thread(self):
        while not self.stop_event.is_set():
            time.sleep(random.randint(self.min_freq, self.max_freq))
            with self.dialog_lock:
                proactive_action(self.model_llm, st_memory=self.dialog_history)

    def event(self, event):
        if event['type'] == 'wakeword':
            with self.dialog_lock:
                answer_action(self.model_llm, self.moel_audio_transcribe, self.current_audio_file_name, st_memory=self.dialog_history)
        elif event['type'] == 'stopword':
            self.stop()
            self.stop_event.set()
        else:
            unk_event_type = event['type']
            print(f'Unknown event type: {unk_event_type}')

    def is_alive(self):
        return not self.stop_event.is_set()


"""     def passive_agent_thread(self):
        try:
            while True:
                pcm = self.recorder.read()
                result = self.porcupine.process(pcm)

                if self.wav_file is not None:
                    self.wav_file.writeframes(struct.pack("h" * len(pcm), *pcm))

                if result >= 0:
                    with self.dialog_lock:
                        passive_action(self.model_llm, self.model_audio_transcribe, self.current_audio_file, st_memory=self.dialog_history)
                        if self.wav_file is not None:
                            self.wav_file.close()
                        os.unlink(self.current_audio_file_name)
                        self.wav_file = get_wav_file(self.current_audio_file_name)

        
        except KeyboardInterrupt:
            print('Stopping ...')
        
        finally:
            self.recorder.delete()
            self.porcupine.delete()
            if self.wav_file is not None:
                self.wav_file.close()



         """