from openai import OpenAI


class ChatGPT:
    def __init__(self, api_key):
        self._client = OpenAI(api_key=api_key)

    def chitchat(self,
                 instructions: str,
                 prev_conversation: list = [],
                 new_question: str,
                 model: str = "gpt-3.5-turbo"):

        messages = [
            {"role": "system", "content": instructions},
        ]

        for question, answer in prev_conversation:
            messages.append({"role": "user", "content": question})
            messages.append({"role": "assistant", "content": answer})

        messages.append({"role": "user", "content": new_question})

        response = self._client.chat.completions.create(
            messages=messages,
            model=model
        )

        return response.choices[0].message.content.strip()

