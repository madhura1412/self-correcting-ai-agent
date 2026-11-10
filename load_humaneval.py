from datasets import load_dataset


def load_humaneval():
    dataset = load_dataset("openai/openai_humaneval")

    return dataset["test"]