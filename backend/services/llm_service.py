from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma




def forRag(question: str,db):
    retriever = db.as_retriever(search_kwargs={"k": 5})
    # ✅ Initialize Groq LLM
    llm = ChatGroq(
        groq_api_key="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",
        model_name="llama3-8b-8192",  # try "llama3-70b-8192" if you want more power
        temperature=0
    )

    # ✅ Define Prompt
    prompt_template = ChatPromptTemplate.from_template("""
    You are the best teacher in the world, brilliant in Java.
    You got award for best tuitor in the world.
    Explain concepts clearly with simple real-world analogies.
    Use the following retrieved context to answer the question.
    I don’t know. The context does not provide this information.
    Say i dont know if asked anything other than java, Data Structures.

    Context: {context}

    Question: {question}

    Answer:
    """)

    # ✅ Build Retrieval QA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",  # simplest for testing
        chain_type_kwargs={"prompt": prompt_template}
    )

    # ✅ Run query
    response = qa_chain.run(question)
    return response

def ask_llm(c:str, userm:str):
    llm = ChatGroq(
        groq_api_key="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",
        model_name="llama3-8b-8192",  # try "llama3-70b-8192" if you want more power
        temperature=0
    )
    prompt=ChatPromptTemplate.from_template("""
    Role: You are an chatbot who explains the core topics in the data you get.
    Context: you will get the data , based on it find core topics in it and explain clearly with examples and not too long 8 lines enough. 
    Query:{userm}
    Answer:
    """)
    formated=prompt.format(c=c,userm=userm)
    response=llm.invoke(formated)
    return response.content