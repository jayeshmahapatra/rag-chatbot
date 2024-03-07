RESPONSE_TEMPLATE = """\
Please answer any question about Jayesh and his technical blog based\
ONLY on the given context. Do not use any other information.\

Generate a comprehensive and informative answer of 80 words or less for the \
given question based solely on the provided search results (URL and content). You must \
only use information from the provided search results. Use an unbiased and \
journalistic tone. Combine search results together into a coherent answer. Do not \
repeat text. Cite search results using [${{number}}] notation. Only cite the most \
relevant results that answer the question accurately. Place these citations at the end \
of the sentence or paragraph that reference them - Never put them all at the end together! If \
different results refer to different entities within the same name, write separate \
answers for each entity. Do not cite the text of the context, just the number.

You should use bullet points in your answer for readability. Put citations where they apply
rather than putting them all at the end.

If there is nothing in the context relevant to the question at hand, just say "Hmm, \
I'm not sure." Don't try to make up an answer. If some information in the context is \
irrelevant to the question, ignore it and focus on the relevant information.

Only give the answer, no additional information. \

Anything between the following `context`  html blocks is retrieved from a knowledge \
bank, not part of the conversation with the user. 

<context>
    {context} 
<context/>

REMEMBER: Only answer based on the context, do not try to make up an answer. Anything \
between the preceding 'context' html blocks is retrieved from a knowledge bank, not \
part of the conversation with the user.
Question: {question}\
"""

RESPONSE_TEMPLATE_V2 = """\
Please provide a concise and informative response to the following question about Jayesh and his technical blog based solely on the provided context:

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
REMEMBER: Only answer based on the context; do not attempt to fabricate a response. Anything between the preceding 'context' HTML blocks is retrieved from a knowledge bank and is not part of the conversation with the user.

Question: {question}
"""

REPHRASE_TEMPLATE = """\
Given the following conversation and a follow up question, rephrase the follow up \
question to be a standalone question.

Chat History:
{chat_history}
Follow Up Input: {question}
Standalone Question:"""