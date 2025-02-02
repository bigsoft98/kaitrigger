import os
import getpass
# from langchain_anthropic import ChatAnthropic
# from langchain_community.llms import Ollama
# from langchain_community.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser




def get_contact_tran_file_content(contact_file_location):
    with open(contact_file_location, 'r') as file:
        file_content = file.read()
    return file_content

if "ANTHROPIC_API_KEY" not in os.environ:
    os.environ["ANTHROPIC_API_KEY"] = getpass.getpass("Enter your Anthropic API key: ")

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your Open API key: ")

contact_tran_file_location =input("Enter the contact transcript file location:")
contact_evaluate_question =input("Enter evaluation question:")
contact_evaluate_question_instruction = input("Enter evaluation question instruction:")


transcript = get_contact_tran_file_content(contact_tran_file_location)
# print(transcript)


# llm = ChatAnthropic(
#     model="claude-3-5-sonnet-20240620",
#     temperature=0,
#     max_tokens=1024,
#     timeout=None,
#     max_retries=1,
# )

# llm = Ollama(model="llama3.2:1b")
llm = ChatOpenAI(model_name="gpt-4", temperature=0.7)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system", "You are a customer contact quality assurer to evaluate contact to evaluate call transcript between <transcript></transcript> tags against categories shown between tags <question></question> by following instruction shown between tags <instruction></<instruction>> and provide evidence.",
        ),
        ("human", "<transcript>{transcript}</transcript>, <question>{question}</question>, <instruction>{instruction}</instruction>"),
    ]
)

chain = prompt | llm | StrOutputParser()
ai_message = chain.invoke(
    {
        "transcript": transcript,
        "question": contact_evaluate_question,
        "instruction": contact_evaluate_question_instruction,
    }
)


print(ai_message)
