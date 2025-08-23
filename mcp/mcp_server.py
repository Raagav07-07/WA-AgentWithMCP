from json import tool
from fastmcp import FastMCP
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel,Field
from langchain.agents import create_tool_calling_agent,AgentExecutor
from langchain_community.tools import TavilySearchResults
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
llm=ChatGoogleGenerativeAI(model="gemini-pro",google_api_key=GEMINI_API_KEY,temperature=0,max_output_tokens=1024
                           )
mcp=FastMCP("WA-AgentWithMCP")
tavily_search=TavilySearchResults(max_results=3)
class SearchWeb(BaseModel):
    Response:str=Field(description="Response from the llm")
    Source:str=Field(description="Source of the information")
output_parser=PydanticOutputParser(pydantic_object=SearchWeb)
format_instructions=output_parser.get_format_instructions()
prompt=ChatPromptTemplate.from_messages(
    [("system",
      '''You are a tech industry analyst and trendspotter with deep expertise in emerging technologies and market dynamics. Your role is to provide accurate, up-to-date, and actionable insights.
Search the web for the latest and most trending technology news, breakthroughs, and updates from credible sources such as TechCrunch, Wired, The Verge, and official company blogs. Focus on:
Emerging technologies (AI, Web3, Quantum Computing, AR/VR).
Major product launches or updates from big tech companies (Google, Apple, Microsoft, OpenAI, Meta).
Significant industry trends (cloud, cybersecurity, semiconductors, generative AI, robotics).
Follow the below format for your response:{format_instructions}'''),
('system', '{agent_scratchpad}')],
).partial(format_instructions=format_instructions)
search_agent_tool=create_tool_calling_agent(
    llm=llm,prompt=prompt,tools=[tavily_search])
@mcp.tool
def search_web():
    '''Search the web for the latest technology news and trends'
    Returns: SearchWeb'''
    agent_executor=AgentExecutor(agent=search_agent_tool,tools=[tavily_search])
    agent_response=agent_executor.invoke()
    return agent_response
@mcp.tool
def summarise(text:str)->str:
    '''Summarise the given response.
    Args:
        text: The text to be summarised.
    Returns:
        A concise summary of the text.'''
    response=llm.invoke("Summarise the following text in a concise manner without spilling any details and include the sources:\n"+text)
    return response
if __name__ == "__main__":
    mcp.run()

    


