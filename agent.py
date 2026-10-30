from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json

class SmalltalkAgent:
    """Agent to handle general queries and smalltalk."""
    def __init__(self, llm):
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_template(
            "You are a friendly IT support assistant. Respond to: {query}\n"
            "IMPORTANT: Use plain text only. Do not use markdown (no bold, no italics, no bullet points, no *, /, -, |, : etc)."
        )
        self.chain = self.prompt | self.llm | StrOutputParser()

    def respond(self, query):
        return self.chain.invoke({"query": query})

class RetrieverAgent:
    """Agent that retrieves technical docs and answers the query."""
    def __init__(self, retriever, llm):
        self.retriever = retriever
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_template(
            "Use this context to answer the IT query.\nContext: {context}\nQuery: {query}\n"
            "IMPORTANT: Respond in plain text only. Do not use any markdown symbols such as **bold**, # headers, or special list symbols(#, *, /, -, |, _, : etc). Use plain paragraphs or simple numbered lists (1, 2, 3) if needed."
        )
        self.chain = self.prompt | self.llm | StrOutputParser()

    def respond(self, query):
        docs = self.retriever.get_relevant_documents(query)
        context = "\n".join([d.page_content for d in docs])
        return self.chain.invoke({"query": query, "context": context})

class ValidatoryAgent:
    """The master agent that selects which specialized agent to call."""
    def __init__(self, llm):
        self.llm = llm
        self.selector_prompt = ChatPromptTemplate.from_template(
            "Route the query to 'Smalltalk' or 'Technical'.\nQuery: {query}\nResponse (JSON):"
        )
        self.selector_chain = self.selector_prompt | self.llm | StrOutputParser()

    def orchestrate(self, query, smalltalk_agent, retriever_agent):
        print(f"[Validatory] Selecting agent for: {query}")
        response = self.selector_chain.invoke({"query": query})
        
        # Simple extraction for JSON-like string
        choice = "Technical" if "Technical" in response else "Smalltalk"
        print(f"[Validatory] Selected: {choice}")
        
        if choice == "Technical":
            return retriever_agent.respond(query)
        else:
            return smalltalk_agent.respond(query)
