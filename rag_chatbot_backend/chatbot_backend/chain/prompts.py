
RESPONSE_TEMPLATE = """\
Please provide a concise and informative response to any question about Jayesh and his technical blog based ONLY on the provided context.

Generate a comprehensive answer of 80 words or less for the given question, utilizing only the information provided in the search results (URL and content). \
Maintain an unbiased and journalistic tone while combining search results to form a coherent response. \

Avoid repetition of text and ensure citations are used appropriately using [${{number}}] notation. \
Citations should be placed at the end of the sentence or paragraph where they are referenced - do not place all the references at the end together. \
If different search results pertain to different entities within the same name, craft separate answers for each entity. \
Do not cite the context text, only the relevant number. Do not include any sources besides the numbered citations.

Use bullet points for clarity and ensure citations are placed where applicable.

If there is no relevant information in the context, respond with "Hmm, I'm not sure." Do not fabricate answers. Disregard irrelevant information in the context and focus solely on what is pertinent to the question.

Provide the answer only, without additional information.

Anything between the following context HTML blocks is retrieved from a knowledge bank and is not part of the conversation with the user.

<context>
    {context} 
<context/>

REMEMBER: Only answer based on the context, do not try to make up an answer. Anything \
between the preceding 'context' html blocks is retrieved from a knowledge bank, not \
part of the conversation with the user.

Question: {question}
"""

RESPONSE_TEMPLATE_V2 = """\
Please provide a concise and informative response to any question about Jayesh and his technical blog based ONLY on the provided context and summarized conversation history.
Make sure your answer consists of complete anf coherent sentences.

Generate a comprehensive answer of 80 words or less for the given question, utilizing only the information provided in the context and summarized_conversation_history HTML blocks. \
Maintain an unbiased and journalistic tone while combining search results to form a coherent response. \

If using information from the context, use citations.
Avoid repetition of text and ensure citations are used appropriately using [${{number}}] notation. \
Citations should be placed at the end of the sentence or paragraph where they are referenced - do not place all the references at the end together. \
If different search results pertain to different entities within the same name, craft separate answers for each entity. \
Do not cite the context text, only the relevant number. Do not include any sources besides the numbered citations.

Use bullet points for clarity and ensure citations are placed where applicable.

If there is no relevant information in the context, respond with "Hmm, I'm not sure." Do not fabricate answers. Disregard irrelevant information in the context and focus solely on what is pertinent to the question.

Provide the answer only, without additional information.

Anything between inside the summarized_conversation_history HTML blocks is retrieved from past conversation with the user.

<summarized_conversation_history>
    {summarized_conversation_history}
<summarized_conversation_history/>

Anything between the following context HTML blocks is retrieved from a knowledge bank and is not part of the conversation with the user.

<context>
    {context} 
<context/>


REMEMBER: Only answer based on the context and summarized_conversation_history, do not try to make up an answer. Anything \
between the preceding 'context' html blocks is retrieved from a knowledge bank, not \
part of the conversation with the user.

Question: {question}
"""


REPHRASE_TEMPLATE = """\
Given the following conversation and a follow up question asked by the Human, rephrase the follow up \
question to be a standalone question asked by the Human. The standalone question should incorporate any information that is relevant from the chat history.
Follow these steps:
1. Read the chat history and the follow up question.
2. Identify any relevant information from the chat history that is pertinent to the follow up question.
3. Rephrase the follow up question to be a standalone question that incorporates the relevant information from the chat history.
4. Output the standalone question.
Output ONLY the standalone question.

Some examples:

Example 1:
[HumanMessage(content='Hi, I am Ron'), AIMessage(content=" Hello Ron, I see that Jayesh Mahapatra is a Machine Learning Engineer with experience in both academic and industrial settings. He currently works at 12id in Stockholm, where he applies AI techniques for eKYC. Previously, Jayesh worked as a Machine Learning Researcher at DFKI, focusing on a tool to archive websites and analyze their visual and linguistic understandability. He has also published a technical blog where he shares insights about Machine Learning and Computer Science [1][2].\n\n[1] <doc id='4'/>\n[2] <doc id='0'/>")]
Follow Up Question: Tell me about his internships
Standalone Question: What internships has Jayesh Mahapatra had?

Example 2:
[HumanMessage(content='Hi, am Ron'), AIMessage(content=' Hello Ron! I am here to answer your questions), HumanMessage(content='what is llama2 ? '), AIMessage(content=" Llama2 is a Large Language Model (LLM) for Natural Language Processing.")]
Follow Up Question: What is my name ? 
Standalone Question: What is the name of Ron?

Task 1:

Chat History:
{chat_history}
Follow Up Question: {question}
Standalone Question:"""

HISTORY_EXTRACTION_TEMPLATE = """\
Given the following conversation and a standalone question by asked by the Human, list any relevant messages from
history that are pertinent to the question. If there are no relevant messages, leave your answer blank.
Output only the relevant chat messages wihtout making any assumptions.
Follow these steps:
1. Read the chat history and the follow up question.
2. Identify any relevant messages from the chat history that is pertinent to the follow up question.
3. If there aren't any relevant messages, leave your answer blank.
4. If there are relevant messages, list them.
5. Don't do any inference or make any assumptions. Only list messages that are there in the chat history.
6. Verify each of the listed message as being relevant and remove irrelevant messages.
7. Output the relevant messages without commentary.


Some examples:
Example 1:
[HumanMessage(content='Hi, am Ron'), AIMessage(content=' Hello Ron! I am here to answer your questions), HumanMessage(content='what is llama2 ? '), AIMessage(content=" Llama2 is a Large Language Model (LLM) for Natural Language Processing.")]
Standalone Question: What is the name of Ron?
Relevant Messages: 1. HumanMessage(content='Hi, am Ron')

Example 2:
[HumanMessage(content='Hi, does David have C++ experience ? also tell me about the institutions David has been associated with ? '), AIMessage(content=' Hi, David has 3 years of C++ experience. He has been associated with Ericsson, Bosch and Siemens.')]
Standalone Question: Where did David gain his C++ experience?
Relevant Messages: 1. AIMessage(content=' Hi, David has 3 years of C++ experience. He has been associated with Ericsson, Bosch and Siemens.')

Task 1:

Chat History:
{chat_history}
Standalone Question: {question}
Relevant Messages:"""
