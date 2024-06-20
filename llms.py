from llama_cpp import Llama

from helpers import time_it

model_id = "./models/Meta-Llama-3-8B-Instruct.Q5_K_M.gguf"

def get_model():
    llm = Llama(
        model_path=model_id,
        n_gpu_layers=-1, # Uncomment to use GPU acceleration
        # seed=1337, # Uncomment to set a specific seed
        n_ctx=1024, # Uncomment to increase the context window
)
    return llm

@time_it
def get_answer_from_llm(model, text, st_memory=None, lt_memory=None):
    messages = [
        {'role': 'system', 'content': 'Твое имя София, ты - ассистент с  юмором'},
        {'role': 'user', 'content': text}
    ]

    if lt_memory:

        for m in lt_memory:
            messages.append(
                {'role': 'system', 'content': 'Факты о предыдущем разговоре: ' + m['content']}
            )
    if st_memory:
        for role, message in st_memory:
            messages.append(
                {'role': role, 'content': message}
            )

    messages.append(
        {'role': 'user', 'content': text}
    )
    response = model.create_chat_completion(messages)
    return response["choices"][0]['message']['content'].replace('\n', '')


@time_it
def get_random_ice_break(model, st_memory=None, lt_memory=None):

    messages = [
        {'role': 'system', 'content': 'Твое имя София, ты - ассистент с юмором'},
    ]

    if lt_memory:
        for m in lt_memory:
            messages.append(
                {'role': 'system', 'content': 'Факты о предыдущем разговоре: ' + m['content']}
            )
    if st_memory:
        for role, message in st_memory:
            messages.append(
                {'role': role, 'content': message}
            )

    messages.append(
        {'role': 'user', 'content': 'Скажи что-нибудь чтобы прервать затянувшееся молчание'}
    )    
      
    
    message = [
        {'role': 'system', 'content': 'Твое имя София, ты - ассистент с юмором'},
        {'role': 'user', 'content': 'Пауза несколько затянулась, порадуй нас чем-нибудь'}
    ]
    response = model.create_chat_completion(message, temperature=0.1)
    return response["choices"][0]['message']['content'].replace('\n', '')

