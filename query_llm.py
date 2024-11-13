from openai import OpenAI
from typing import Union, Optional


class QueryOpenAI():

    def __init__(self, temperature: float = 0.7, top_p: float = 0.8):
        self.client = OpenAI()
        self.temperature = temperature
        self.top_p = top_p

    def send_query_to_chatgpt(self, query) -> Optional[str]:
        response = self.client.chat.completions.create(
            model='gpt-3.5-turbo' if self.open_ai_model_input == 2 else 'gpt-4o',
            frequency_penalty=0.5,
            temperature=self.temperature,
            top_p=self.top_p,
            messages=[
                {"role": "system", "content": "You are writing advertising copy for a home decor e-commerce store. Make the copy very engaging, persuasive, concise, and direct."},
                {"role": "user", "content": f"{query}"},
            ]
        )

        ai_response = response.choices[0].message.content
        return ai_response

    def run_query(self, accept_user_input: bool = False, open_ai_model_input: int = 2, prompt_type_input: Union[int, None] = None, user_input: Union[str, None] = None) -> Optional[str]:
        if accept_user_input:
            self.open_ai_model_input = int(input('\nEnter index for type of OpenAI model:\n1: 4o\n2: 3.5-turbo\n\n'))
            self.prompt_type_input = int(input('\nEnter index for type of prompt:\n1: Title\n2: Body\n3: Bullet\n\n'))
            self.user_input = input('\nInput text:\n\n')
        else:
            self.open_ai_model_input = open_ai_model_input
            self.prompt_type_input = prompt_type_input
            self.user_input = user_input

        prompt = None

        if self.prompt_type_input == 1:
            prompt = f'The product is {self.user_input}. Generate a name for this product. Make it concise and short suitable for a Shopify product name.'
        elif self.prompt_type_input == 2:
            prompt = f'Write a 2 sentence copy advertisement description that best describes the product based on this product information: {self.user_input}'
        else:
            prompt = f'Create 4 short bullet points of the most important product features without explanations based on this product information: {self.user_input}.'

        ai_response = self.send_query_to_chatgpt(prompt)
        print(f'\n{ai_response}\n')

        return ai_response
