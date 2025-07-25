import ollama  # type: ignore
import logging
from typing import List, Dict, Any
from app.schemas.ai_chat import ChatMessage

logger = logging.getLogger(__name__)


class TunaAIService:
    def __init__(self, model_name: str = "llama3.2:3b"):
        self.model_name = model_name
        self.system_prompt = """You are Tuna, a friendly and knowledgeable AI assistant. 
You help users learn by answering questions, explaining concepts, and summarizing content.
You are particularly good at:
- Answering questions about lessons and educational content
- Summarizing long texts into key points
- Explaining complex concepts in simple terms
- Helping with study and learning strategies

Always be helpful, concise, and educational in your responses.
CRITICAL INSTRUCTION: Never use introductory phrases. Never start with phrases like "Here is", "This is", "Here's a summary", "In 2-3 sentences", or any similar prefixes. Always start your response directly with the main content. No preambles, no introductions, just the direct answer."""

    async def chat(self, message: str, conversation_history: List[ChatMessage] = None) -> str:
        """
        Send a chat message to Tuna and get a response
        """
        try:
            # Prepare conversation context
            messages = [{"role": "system", "content": self.system_prompt}]

            # Add conversation history
            if conversation_history:
                # Keep last 10 messages for context
                for msg in conversation_history[-10:]:
                    messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })

            # Add current user message
            messages.append({"role": "user", "content": message})

            # Get response from Ollama
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                options={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 3000  # Increased from 1000 to allow longer chat responses
                }
            )

            return response['message']['content']

        except Exception as e:
            logger.error(f"Error in Tuna chat: {str(e)}")
            return "I'm sorry, I'm having trouble processing your request right now. Please try again."

    async def summarize_text(self, text: str, summary_type: str = "general") -> Dict[str, Any]:
        """
        Summarize text content
        """
        try:
            # Different prompts for different summary types
            prompts = {
                "general": f"Summarize this text:\n\n{text}",
                "key_points": f"Key points from this text:\n\n{text}",
                "brief": f"Brief summary (2-3 sentences):\n\n{text}"
            }

            prompt = prompts.get(summary_type, prompts["general"])

            messages = [
                {"role": "system", "content": "You are Tuna, an AI assistant specialized in creating clear, educational summaries. NEVER use introductory phrases like 'Here is a summary', 'This is', 'In 2-3 sentences', etc. Start your response immediately with the actual summary content. No preambles."},
                {"role": "user", "content": prompt}
            ]

            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                options={
                    "temperature": 0.3,  # Lower temperature for more focused summaries
                    "max_tokens": 4000  # Increased from 800 to allow longer summaries
                }
            )

            summary = response['message']['content']

            return {
                "summary": summary,
                "original_length": len(text),
                "summary_length": len(summary)
            }

        except Exception as e:
            logger.error(f"Error in text summarization: {str(e)}")
            return {
                "summary": "I'm sorry, I couldn't generate a summary right now.",
                "original_length": len(text),
                "summary_length": 0
            }

    async def summarize_lesson(self, lesson_content: str, lesson_title: str) -> Dict[str, Any]:
        """
        Summarize lesson content with educational focus
        """
        try:
            prompt = f"""Lesson: "{lesson_title}"

{lesson_content}

Summary with key learning points and important concepts for student review:"""

            messages = [
                {"role": "system", "content": "You are Tuna, an educational AI assistant. Create summaries that help students learn and review effectively. NEVER use introductory phrases like 'Here is a summary', 'This is', 'The following is', etc. Start your response immediately with the actual summary content. No preambles."},
                {"role": "user", "content": prompt}
            ]

            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                options={
                    "temperature": 0.4,
                    "max_tokens": 5000  # Increased from 1200 to allow much longer lesson summaries
                }
            )

            summary_content = response['message']['content']

            # Try to extract key points (basic parsing)
            key_points = []
            lines = summary_content.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('- ') or line.startswith('• ') or line.startswith('* '):
                    key_points.append(line[2:])
                elif any(indicator in line.lower() for indicator in ['key point', 'important', 'remember']):
                    key_points.append(line)

            return {
                "summary": summary_content,
                "key_points": key_points[:10]  # Limit to 10 key points
            }

        except Exception as e:
            logger.error(f"Error in lesson summarization: {str(e)}")
            return {
                "summary": "I'm sorry, I couldn't generate a lesson summary right now.",
                "key_points": []
            }

    async def create_chapterized_summary(self, lesson_content: str, lesson_title: str) -> Dict[str, Any]:
        """
        Create a chapterized summary using LLM to break down content into logical chapters
        """
        try:
            prompt = f"""Analyze this lesson content and create a well-structured summary divided into logical chapters/sections.

Lesson Title: "{lesson_title}"

Content:
{lesson_content}

Please organize the summary into 3-6 logical chapters/sections. For each chapter:
1. Give it a clear, descriptive title
2. Provide 2-4 paragraphs of summary content
3. Use this exact format:

## Chapter 1: [Title]
[Content paragraphs]

## Chapter 2: [Title]  
[Content paragraphs]

Focus on educational value and make sure each chapter covers distinct topics or concepts."""

            messages = [
                {"role": "system", "content": "You are Tuna, an educational AI assistant. Create well-structured, chapterized summaries that help students learn systematically. NEVER use introductory phrases. Start directly with the first chapter. Use the exact format requested with ## headers."},
                {"role": "user", "content": prompt}
            ]

            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                options={
                    "temperature": 0.3,
                    "max_tokens": 6000
                }
            )

            full_response = response['message']['content']
            
            # Parse chapters from the response
            chapters = []
            current_chapter = ""
            
            lines = full_response.split('\n')
            for line in lines:
                if line.strip().startswith('## '):
                    # Save previous chapter if exists
                    if current_chapter.strip():
                        chapters.append(current_chapter.strip())
                    # Start new chapter
                    current_chapter = line.strip()[3:] + '\n'  # Remove ## prefix
                else:
                    current_chapter += line + '\n'
            
            # Add the last chapter
            if current_chapter.strip():
                chapters.append(current_chapter.strip())
            
            # If parsing failed, return the full response as a single chapter
            if not chapters:
                chapters = [full_response]

            return {
                "summary": full_response,
                "chapters": chapters,
                "chapter_count": len(chapters)
            }

        except Exception as e:
            logger.error(f"Error in chapterized summarization: {str(e)}")
            return {
                "summary": "I'm sorry, I couldn't generate a chapterized summary right now.",
                "chapters": [],
                "chapter_count": 0
            }

    def check_model_availability(self) -> bool:
        """
        Check if the specified model is available in Ollama
        """
        try:
            models = ollama.list()
            available_models = [model['name'] for model in models['models']]
            return self.model_name in available_models
        except Exception as e:
            logger.error(f"Error checking model availability: {str(e)}")
            return False

    async def pull_model(self) -> bool:
        """
        Pull the model if it's not available
        """
        try:
            logger.info(f"Pulling model {self.model_name}...")
            ollama.pull(self.model_name)
            logger.info(f"Model {self.model_name} pulled successfully")
            return True
        except Exception as e:
            logger.error(f"Error pulling model: {str(e)}")
            return False

    async def suggest_related_jobs(self, lesson_title: str, lesson_description: str, lesson_category: str) -> List[str]:
        """
        Suggest related job positions for a lesson based on its content
        Returns a list of job position strings that will be matched/created in the database
        """
        try:
            prompt = f"""Lesson Details:
Title: {lesson_title}
Category: {lesson_category}
Description: {lesson_description}

Based on this lesson content, suggest relevant job positions that someone who completes this lesson might pursue. Consider:
- Skills taught in the lesson
- Career paths this lesson supports
- Industry alignment
- Entry-level to advanced positions
- Different job titles in the field

Return 3-7 job position titles, one per line. Be specific and use common industry job titles.
Example format:
Software Developer
Data Analyst
Product Manager
UX Designer"""

            messages = [
                {"role": "system", "content": "You are Tuna, an AI career advisor that helps match educational content with relevant job positions. Analyze lesson content and suggest specific job titles that learners could pursue. Return ONLY the job position titles, one per line, no numbers or bullets."},
                {"role": "user", "content": prompt}
            ]

            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                options={
                    "temperature": 0.4,
                    "max_tokens": 200
                }
            )

            # Parse the response to extract job positions
            response_text = response['message']['content'].strip()
            job_positions = []

            # Split by lines and clean up
            lines = response_text.split('\n')
            for line in lines:
                line = line.strip()
                # Remove bullets, numbers, or other prefixes
                import re
                line = re.sub(r'^[\d\.\-\*\•\s]+', '', line).strip()

                if line and len(line) > 2:  # Valid job title
                    job_positions.append(line)

            return job_positions[:7]  # Limit to 7 suggestions

        except Exception as e:
            logger.error(f"Error in job suggestion: {str(e)}")
            return []

    async def suggest_category(self, lesson_title: str, lesson_description: str = "", lesson_content: str = "") -> str:
        """
        Suggest a category for a lesson based on its title, description, and content
        Returns a single category string
        """
        try:
            prompt = f"""Lesson Details:
Title: {lesson_title}
Description: {lesson_description}
Content Preview: {lesson_content[:500] if lesson_content else "Not available"}

Based on this lesson information, suggest the most appropriate category from common educational categories. Consider:
- Subject matter and topics covered
- Target audience and skill level
- Learning objectives
- Industry alignment

Popular categories include:
Programming, Web Development, Data Science, Mathematics, Science, Business, Marketing, Design, Language, Art, Music, History, Engineering, Health, Finance, Psychology, etc.

Return ONLY the category name, nothing else."""

            messages = [
                {"role": "system", "content": "You are Tuna, an educational AI that helps categorize learning content. Analyze lesson information and suggest the most appropriate single category. Return ONLY the category name."},
                {"role": "user", "content": prompt}
            ]

            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                options={
                    "temperature": 0.3,
                    "max_tokens": 50
                }
            )

            # Clean up the response
            category = response['message']['content'].strip()

            # Remove any extra text and get just the category
            import re
            category = re.sub(r'^[^\w]*', '', category).strip()
            category = category.split('\n')[0].strip()
            category = category.split('.')[0].strip()

            # Capitalize properly
            if category:
                category = category.title()

            return category or "General"

        except Exception as e:
            logger.error(f"Error in category suggestion: {str(e)}")
            return "General"


# Global instance
tuna_ai = TunaAIService()
