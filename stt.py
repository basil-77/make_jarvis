import wave
from helpers import time_it


def get_wav_file(file_name):
    wav_file = wave.open(file_name, "w")
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(16000)
    return wav_file

# @time_it
# def wav_to_mp3(file_name, output_file_name):
#     command = f'ffmpeg -loglevel quiet -y -i {file_name} {output_file_name}'
#     os.system(command)

# def remove_wakeword(text, wake_word='Кристина'):
#     wake_word_lc = wake_word.lower()
#     text = text.replace(wake_word,'').replace(wake_word_lc, '').strip()
#     return text.strip(',')

@time_it
def transcribe_audio_file(model, input_audio_file):
    segments, _ = model.transcribe(input_audio_file, beam_size=5)
    text = []
    for segment in segments:
        text.append(segment.text)
    return ' '.join(text)

""" @time_it
def transcribe_audio_file_replicate(replicate_client, input_audio_file):
    model_version = 'openai/whisper:4d50797290df275329f202e48c76360b3f22b08d28c196cbc54600319435f8d2'
    uploaded_file = replicate.models.UploadedFile.upload(
    path=os.path.dirname(input_audio_file),
    name=os.path.basename(input_audio_file),
    )

    input_data = {
        "audio": uploaded_file.url,
        "model": "large-v3",
        "language": "ru",
        "translate": False,
        "temperature": 0,
        "transcription": "plain text",
        "suppress_tokens": "-1",
        "logprob_threshold": -1,
        "no_speech_threshold": 0.6,
        "condition_on_previous_text": True,
        "compression_ratio_threshold": 2.4,
        "temperature_increment_on_fallback": 0.2
        }
    output = replicate_client.run(model_version, input=input_data)

    return output """