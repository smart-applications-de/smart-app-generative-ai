import json
import os

import requests
from langchain.tools import tool
from crewai_tools import BaseTool
from pydantic import BaseModel
from dotenv import  load_dotenv

class SearchTools(BaseTool):
    name: str = "Search Internet Tool"
    description: str = (
                """Useful to search the internet
        about a a given topic and return relevant results"""
    )

    def _run(query:str) -> str:
        """Useful to search the internet
        about a a given topic and return relevant results"""
        load_dotenv()
        top_result_to_return = 4
        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": query})
        headers = {
            'X-API-KEY': os.environ['SERPER_API_KEY'],
            'content-type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        # check if there is an organic key
        if 'organic' not in response.json():
          return "Sorry, I couldn't find anything about that, there could be an error with you serper api key."
        else:
          results = response.json()['organic']
          string = []
          for result in results[:top_result_to_return]:
            try:
              string.append('\n'.join([
                  f"Title: {result['title']}", f"Link: {result['link']}",
                  f"Snippet: {result['snippet']}", "\n-----------------"
              ]))
            except KeyError:
              next

          return '\n'.join(string)
class CalculatorTool(BaseTool):
    name: str = "Calculator tool"
    description: str = (
        "Useful to perform any mathematical calculations, like sum, minus, multiplication, division, etc. The input to this tool should be a mathematical  expression, a couple examples are `200*7` or `5000/2*10."
    )

    def _run(self, operation: str) -> int:
        # Implementation goes here
        return eval(operation)