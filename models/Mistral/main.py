import ollama
import time

class ModelRunner:
    def __init__(self) -> None:
        self.model = ""
        self.prompt_created_at = ""
        self.total_duration = 0
        self.prompt = ""
        self.result = ""

    def run(self, prompts_in):
        messages = []
        messages_in = []
        messages_out = []

        i = 0
        for prompt in prompts_in:
            print("===== Mistral =====")
            print(f"Prompt {i}")
            time_per_prompt_start = time.time()
            if content_in := prompt:
                messages_in.append({"role": "user", "content": content_in})
                messages.append({"role": "user", "content": content_in})

                content_out = ""
                message_out = {"role": "assistant", "content": ""}

                for response in ollama.chat(model='mistral', messages=messages, stream=True):
                    if response['done']:
                        messages.append(message_out)
                    
                    content = response['message']['content']
                    print(content, end='', flush=True)
                    
                    content_out += content
                    if content in ['.', '!', '?', '\n']:
                        content_out += ''

                    message_out['content'] += content

                if content_out:
                    messages_out.append(message_out)
            
            print(f"Time spent for prompt {i}: {time.time() - time_per_prompt_start}")
            i += 1

        return messages_out, messages