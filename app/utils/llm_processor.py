import asyncio
import logging
from typing import List, Optional, Dict, Any
import json
import re
from app.models.schemas import FAQSchema
from app.core.config import settings
logger = logging.getLogger(__name__)
class LLMProcessor:
    def __init__(self):
        self.client = None
        self._initialize_client()
    def _initialize_client(self):
        if settings.OPENAI_API_KEY:
            try:
                import openai
                self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("OpenAI client initialized successfully")
            except ImportError:
                logger.warning("OpenAI package not available")
            except Exception as e:
                logger.error(f"Error initializing OpenAI client: {e}")
    def is_available(self) -> bool:
        return self.client is not None
    async def structure_faqs(self, raw_faqs: List[FAQSchema]) -> List[FAQSchema]:
        if not self.is_available() or not raw_faqs:
            return raw_faqs
        try:
            faq_text = "\n\n".join([f"Q: {faq.question}\nA: {faq.answer}" for faq in raw_faqs])
            prompt = f"""
            Please analyze and improve the following FAQ content. Your tasks:
            1. Clean up the questions and answers (fix grammar, make them clearer)
            2. Categorize each FAQ (e.g., "Shipping", "Returns", "Payment", "Product", "General")
            3. Remove any duplicate or very similar questions
            4. Ensure answers are complete and helpful
            Return the result as a JSON array with this structure:
            [
                {{
                    "question": "cleaned question",
                    "answer": "improved answer", 
                    "category": "category name"
                }}
            ]
            FAQ Content:
            {faq_text}
            """
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that structures and improves FAQ content for e-commerce websites."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            content = response.choices[0].message.content
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                structured_data = json.loads(json_match.group())
                structured_faqs = []
                for item in structured_data:
                    if isinstance(item, dict) and 'question' in item and 'answer' in item:
                        structured_faqs.append(FAQSchema(
                            question=item['question'],
                            answer=item['answer'],
                            category=item.get('category')
                        ))
                logger.info(f"LLM structured {len(structured_faqs)} FAQs")
                return structured_faqs
        except Exception as e:
            logger.error(f"Error structuring FAQs with LLM: {e}")
        return raw_faqs
    async def extract_brand_context(self, raw_text: str) -> Optional[str]:
        if not self.is_available() or not raw_text:
            return raw_text
        try:
            prompt = f"""
            Please extract and summarize the key brand information from the following text. 
            Focus on:
            1. What the brand does/sells
            2. Brand story and mission
            3. Key values or unique selling points
            4. Target audience
            Keep the summary concise (2-3 paragraphs max) and professional.
            Remove any navigation text, headers, or irrelevant content.
            Text content:
            {raw_text[:2000]}
            """
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that extracts and summarizes brand information from website content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            brand_context = response.choices[0].message.content.strip()
            if brand_context and len(brand_context) > 50:
                logger.info("LLM extracted brand context successfully")
                return brand_context
        except Exception as e:
            logger.error(f"Error extracting brand context with LLM: {e}")
        return raw_text[:1000] if raw_text else None
    async def analyze_competitors(self, main_brand_data: Dict[str, Any], competitor_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not self.is_available():
            return {"analysis_summary": "LLM analysis not available"}
        try:
            main_summary = f"Brand: {main_brand_data.get('brand_name', 'Unknown')}\n"
            main_summary += f"Products: {len(main_brand_data.get('product_catalog', []))}\n"
            main_summary += f"Context: {main_brand_data.get('brand_context', '')[:200]}"
            competitor_summaries = []
            for comp in competitor_data[:3]:
                comp_summary = f"Brand: {comp.get('brand_name', 'Unknown')}\n"
                comp_summary += f"Products: {len(comp.get('product_catalog', []))}\n"
                comp_summary += f"Context: {comp.get('brand_context', '')[:200]}"
                competitor_summaries.append(comp_summary)
            prompt = f"""
            Analyze the following brand and its competitors. Provide insights on:
            1. Competitive positioning
            2. Unique advantages of the main brand
            3. Areas for improvement
            4. Market opportunities
            Main Brand:
            {main_summary}
            Competitors:
            {chr(10).join(competitor_summaries)}
            Provide a concise analysis (2-3 paragraphs).
            """
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a business analyst providing competitive analysis for e-commerce brands."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.4
            )
            analysis = response.choices[0].message.content.strip()
            return {
                "analysis_summary": analysis,
                "competitive_advantages": self._extract_advantages(analysis)
            }
        except Exception as e:
            logger.error(f"Error analyzing competitors with LLM: {e}")
            return {"analysis_summary": "Error performing competitive analysis"}
    def _extract_advantages(self, analysis_text: str) -> List[str]:
        advantages = []
        lines = analysis_text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith(('-', '•', '*')) or re.match(r'^\d+\.', line):
                advantage = re.sub(r'^[-•*\d.]\s*', '', line).strip()
                if advantage:
                    advantages.append(advantage)
        return advantages if advantages else ["No specific advantages mentioned"]