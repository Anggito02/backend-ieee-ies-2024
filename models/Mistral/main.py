import ollama

class ModelRunner:
    def __init__(self) -> None:
        self.model = ""
        self.prompt_created_at = ""
        self.total_duration = 0
        self.prompt = ""
        self.result = ""

    async def run(self, prompts_in):
        client = ollama.AsyncClient()
        messages = []
        messages_in = []
        messages_out = []

        for prompt in prompts_in:
            if content_in := prompt:
                messages_in.append({"role": "user", "content": content_in})
                messages.append({"role": "user", "content": content_in})

                content_out = ""
                message_out = {"role": "assistant", "content": ""}

                async for response in await client.chat(model='mistral', messages=messages):
                    if response['done']:
                        messages.append(message_out)
                    
                    content = response['message']['content']
                    
                    content_out += content
                    if content in ['.', '!', '?', '\n']:
                        content_out += ''

                    message_out['content'] += content

                if content_out:
                    messages_out.append(message_out)

        return messages_out