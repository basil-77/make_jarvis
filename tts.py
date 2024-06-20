import os
import asyncio
import aioconsole

""" 
To make text-to-speach on windows platform the voice.exe tool is used
https://www.elifulkerson.com/projects/commandline-text-to-speech.php
 """

 
from helpers import time_it
#from say_thread import TextToSpeech

def say(text):
    command = f'voice.exe {text}'
    os.system(command)  
    
def interrupt_tts():
    pass

@time_it
def do_tts(text):
    #text = text.replace('\n', '')
    print (f'tts = {text}')
    say(text)


class TextToSpeech:
    def __init__(self):
        self.current_process = None

    async def speak(self, text, role):
        text = text.replace('\n', '')
        self.current_process = await asyncio.create_subprocess_shell(
        f'voice.exe {text}',
        stdout = asyncio.subprocess.PIPE,
        stderr = asyncio.subprocess.PIPE
        )
        try:
            stdout, stderr = await self.current_process.communicate()
            if stderr:
                print(f'Error: {stderr.decode().strip()}')
        except asyncio.CancelledError:
            if self.current_process:
                self.current_process.terminate()
                await self.current_process.wait()
            raise
        finally:
            self.current_process = None
    
    async def stop_speaking(self):
        if self.current_process:
            print('Stopping current speaking...')
            self.current_process.terminate()
            await self.current_process.wait()
            self.current_process = None
            print('Stopped.')


    async def listener(self, task_queue, stop_event):
        try:
            text, role = await asyncio.wait_for(task_queue.get(), timeout=1)
            print(f'Starting to speak {text}')
            await self.speak(text, role)
            print('Finished speaking')
            task_queue.task_done()
        except asyncio.TimeoutError:
            pass #continue

async def main():
    tts = TextToSpeech()
    task_queue = asyncio.Queue(maxsize=10)
    stop_event = asyncio.Event()

    listener_task = asyncio.create_task(tts.listener(task_queue, stop_event))

    try:
        while True:
            command = aioconsole.ainput('Enter command (speak/stop/exit): ')
            if command == 'speak':
                role = None
                text = await aioconsole.ainput('Enter text to speak: ')
                await task_queue.put((text, role))
            elif command == 'stop':
                await tts.stop_speaking()
            elif command == 'exit':
                stop_event.set()
                break
    except KeyboardInterrupt:
        stop_event.set()
    finally:
        await listener_task
        await asyncio.gather(listener_task)

# if __name__ == '__main__':
#     if os.__name__ == 'nt':
#         asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
#     asyncio.run(main())


""" @time_it
def do_tts_replicate(replicate_client, text):
    print (f'tts_replicate = {text}')

    model_version = 'lucataco/xtts-v2:684bc3855b37866c0c65add2ff39c78f3dea3f4ff103a436465326e0f438d55e'
    input_data = {
        "text": text,
        "language": "ru",
        "speaker": "https://replicate.delivery/pbxt/Jt79w0xsT64R1JsiJ0LQRL8UcWspg5J4RFrU6YwEKpOT1ukS/male.wav"
        }
    print ('--1')
    output = replicate_client.run(model_version, input=input_data)
    print ('--2')

    response = requests.get(output)
    print ('--3')
    filename = "data/generated_speech.wav"

    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
    else:
        print(f'Error downloading file: {response.status_code}')
    print ('--4')
    playsound(filename)
    print ('--5') """





