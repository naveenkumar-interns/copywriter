from dataclasses import dataclass
from typing import Dict, List, Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import Tool
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize LLM
llm = ChatGroq(
    model="mixtral-8x7b-32768",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=os.getenv("GROQ_API_KEY")
)

@dataclass
class CopyInput:
    product: str
    tone: str = ""
    length: str = ""
    industry: str = ""
    target_audience: str = ""
    brand_voice: str = ""
    unique_selling_points: List[str] = None

    def __post_init__(self):
        self.unique_selling_points = self.unique_selling_points or []

class ResearchAgent:
    def analyze_target_audience(self, copy_input: CopyInput) -> str:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert market researcher specializing in {industry}."),
            ("human", """
                Product: {product}
                Target Audience: {audience}
                Industry: {industry}
                
                Provide detailed insights about:
                1. Demographics and psychographics
                2. Pain points and challenges
                3. Motivations and goals
                4. Online behavior and preferences
                5. Purchase decision factors
            """)
        ])
        chain = prompt | llm
        result = chain.invoke({
            "industry": copy_input.industry,
            "product": copy_input.product,
            "audience": copy_input.target_audience
        })
        return result.content

class StrategyAgent:
    def create_content_strategy(self, research_data: str, copy_input: CopyInput) -> str:
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"You are a content strategist specializing in {copy_input.tone} copy."),
            ("human", """
                Research: {research}
                Product: {product}
                Tone: {tone}
                USPs: {usps}
                
                Create a content strategy with:
                1. Key messages and themes
                2. Tone guidelines
                3. Section priorities
                4. Conversion goals
            """)
        ])
        chain = prompt | llm
        result = chain.invoke({
            "research": research_data,
            "product": copy_input.product,
            "tone": copy_input.tone,
            "usps": ", ".join(copy_input.unique_selling_points)
        })
        return result.content

class CopywritingAgent:
    def write_website_copy(self, strategy: str, section: str, copy_input: CopyInput) -> str:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Expert copywriter creating {length} {tone} content."),
            ("human", """
                Strategy: {strategy}
                Section: {section}
                Product: {product}
                Brand Voice: {brand_voice}
                USPs: {usps}
                
                Write compelling copy focusing on:
                - Clear value proposition
                - Engaging headlines
                - {tone} body copy of {length} length
                - Strategic CTAs
            """)
        ])
        chain = prompt | llm
        result = chain.invoke({
            "length": copy_input.length,
            "tone": copy_input.tone,
            "strategy": strategy,
            "section": section,
            "product": copy_input.product,
            "brand_voice": copy_input.brand_voice,
            "usps": ", ".join(copy_input.unique_selling_points)
        })
        return result.content

class EditorAgent:
    def review_copy(self, copy: str) -> str:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert copy editor."),
            ("human", """
                Review this website copy:
                {copy}
                
                Improve:
                - Clarity and conciseness
                - Persuasiveness
                - Brand voice consistency
                - Grammar and style
            """)
        ])
        chain = prompt | llm
        result = chain.invoke({"copy": copy})
        return result.content

class WebsiteCopySystem:
    def __init__(self):
        self.agents = {
            "research": ResearchAgent(),
            "strategy": StrategyAgent(),
            "copywriting": CopywritingAgent(),
            "editor": EditorAgent()
        }

    def generate_website_copy(self, copy_input: CopyInput, sections: List[str]) -> Dict[str, str]:
        try:
            research = self.agents["research"].analyze_target_audience(copy_input)
            strategy = self.agents["strategy"].create_content_strategy(research, copy_input)
            
            section_copy = {}
            for section in sections:
                initial_copy = self.agents["copywriting"].write_website_copy(
                    strategy,
                    section,
                    copy_input
                )
                final_copy = self.agents["editor"].review_copy(initial_copy)
                section_copy[section] = final_copy
            return section_copy
            
        except Exception as e:
            raise Exception(f"Copy generation failed: {str(e)}")

if __name__ == "__main__":
    # Example usage
    input_data = CopyInput(
        product="food delivery website",
        tone="informative",
        length="short",
        industry="food delivery",
        target_audience="young urban professionals",
        brand_voice="friendly and reliable",
        unique_selling_points=["30-minute delivery", "local restaurants", "no minimum order"]
    )
    
    system = WebsiteCopySystem()
    sections = ["homepage", "about", "services", "contact"]
    
    try:
        results = system.generate_website_copy(input_data, sections)
        for section, copy in results.items():
            print(f"\n=== {section.upper()} ===")
            print(copy)
    except Exception as e:
        print(f"Error: {e}")