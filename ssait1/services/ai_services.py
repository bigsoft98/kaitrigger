 
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
 
def talk_2_ai(transcript,contact_evaluate_question,contact_evaluate_question_instruction):
    # ai_message = "You are a customer contact quality assurer to evaluate contact to evaluate call transcript between <transcript>"+transcript+"</transcript> tags against categories shown between tags <question>"+contact_evaluate_question+"</question> by following instruction shown between tags <instruction>"+contact_evaluate_question_instruction+"</<instruction>> and provide evidence."
    
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
    
    # ai_message = "AI answer will be provided once the backend is linked to the selected FM"
    return ai_message