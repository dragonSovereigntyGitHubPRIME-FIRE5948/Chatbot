import os
import openai
import config

# validate OpenAI API key
def validate_openai_key():
    if config.marcus_openai_key is not None:
        openai.api_key = config.marcus_openai_key
    else:
        raise ValueError(
            "OPENAI_API_KEY cannot be None. Set the key using in config.py"
    )

# checks if user input is acceptable in terms of OpenAI's usage policies
def check_moderation(input):
    # async check
    response = openai.Moderation.acreate(
        input=input
    )
    # returning results so that can output message in chatbot
    return response['results'][0]["flagged"]

    # raise exception block
    # if it is flagged, raise
    # if response['results'][0]["flagged"] == True:
    #     raise Exception(
    #         "This text did not pass the OpenAI's usage policies. Please retry"
    # )