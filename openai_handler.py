from openai import OpenAI

class OpenaiHandler:
    def __init__(self, KEY):
        self.client = OpenAI(api_key=KEY)

    def summary(self, text):
        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Make a summary of the given text"
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            model="gpt-3.5-turbo-1106",
        )
        summary = chat_completion.choices[0].message.content
        return summary
