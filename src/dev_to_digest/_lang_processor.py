from typing import List
from pydantic import BaseModel, Field

from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser


class ProcResult(BaseModel):
    ja_title: str = Field(description="Japanese translation of the article title")
    ja_summary: str = Field(description="Japanese translation of the summary")


SUMMARIZE_PROMPT_TEMPLATE = """
## Instructions

Please summarize the following English text into a narrative of {summary_sentences} sentences in plain text format.

## Text

================================================================

{contents}

================================================================
""".strip()

JA_TRANSLATE_PROMPT_TEMPLATE = """
## Instructions
Please translate the following text into Japanese.

## Text
{text}
""".strip()

PARSE_PROMPT_TEMPLATE = """
## Instructions
Please return an object containing a Japanese title and a Japanese summary.

## Input
### Japanese Title
{ja_title}

### Japanese Summary
{ja_summary}

## Output Format
{formatted_instructions}
""".strip()


class LangProc:
    def __init__(
        self, title: str, contents: str, url: str, tag_list: List[str], model: str
    ):
        self.title = title
        self.contents = contents
        self.url = url
        self.tag_list = tag_list
        self.llm = Ollama(model=model)
        parser = PydanticOutputParser(pydantic_object=ProcResult)
        self.result_parser = OutputFixingParser.from_llm(
            parser=parser,
            llm=self.llm,
        )

    def summarize(self, summary_sentences: int):
        prompt = PromptTemplate(
            template=SUMMARIZE_PROMPT_TEMPLATE,
            input_variables=["summary_sentences", "contents"],
        )
        formatted_prompt = prompt.format(
            summary_sentences=summary_sentences, contents=self.contents
        )
        output = self.llm.invoke(formatted_prompt)
        return output

    def translate(self, text: str):
        prompt = PromptTemplate(
            template=JA_TRANSLATE_PROMPT_TEMPLATE,
            input_variables=["text"],
        )
        formatted_prompt = prompt.format(text=text)
        output = self.llm.invoke(formatted_prompt)
        return output

    def summarize_and_translate(self, summary_sentences: int):
        summary = self.summarize(summary_sentences)
        ja_summary = self.translate(summary)
        ja_title = self.translate(self.title)
        formatted_instructions = self.result_parser.get_format_instructions()
        prompt = PromptTemplate(
            template=PARSE_PROMPT_TEMPLATE,
            input_variables=["ja_title", "ja_summary"],
            partial_variables={"formatted_instructions": formatted_instructions},
        )
        formatted_prompts = prompt.format(ja_title=ja_title, ja_summary=ja_summary)
        output = self.llm.invoke(formatted_prompts)
        return self.result_parser.parse(output)

    def run(self, summary_sentences: int = 5) -> dict:
        result = self.summarize_and_translate(summary_sentences)
        print(result)
        exit()
        return {
            "en_title": self.title,
            "ja_title": result.ja_title.text,
            "url": self.url,
            "tags": ", ".join([f"#{t}" for t in self.tag_list]),
            "ja_summary": result.ja_summary.text,
        }
