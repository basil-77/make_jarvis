import asyncio
import os
import aioconsole

from playsound import playsound

class TextToSpeech:
    def __init__(self):
        self.current_process = None

    async def speak(self, text, role):
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

if __name__ == '__main__':
    if os.__name__ == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())