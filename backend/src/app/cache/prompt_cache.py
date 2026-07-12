class PromptCache:

    def __init__(self):
        self.cache = {}

    def get(self, prompt: str):
        return self.cache.get(prompt)

    def set(self, prompt: str, response: str):
        self.cache[prompt] = response


_prompt_cache = PromptCache()


def get_prompt_cache():
    return _prompt_cache