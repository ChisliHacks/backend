import ollama
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

Always be helpful, concise, and educational in your responses."""

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
                    "max_tokens": 1000
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
                "general": f"Please provide a clear and concise summary of the following text:\n\n{text}",
                "key_points": f"Extract the key points from the following text and list them:\n\n{text}",
                "brief": f"Provide a very brief summary (2-3 sentences) of the following text:\n\n{text}"
            }

            prompt = prompts.get(summary_type, prompts["general"])

            messages = [
                {"role": "system", "content": "You are Tuna, an AI assistant specialized in creating clear, educational summaries."},
                {"role": "user", "content": prompt}
            ]

            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                options={
                    "temperature": 0.3,  # Lower temperature for more focused summaries
                    "max_tokens": 800
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
            prompt = f"""Please analyze and summarize this lesson titled "{lesson_title}":

{lesson_content}

Provide:
1. A comprehensive summary
2. Key learning points
3. Important concepts to remember

Format your response to be helpful for students reviewing the material."""

            messages = [
                {"role": "system", "content": "You are Tuna, an educational AI assistant. Create summaries that help students learn and review effectively."},
                {"role": "user", "content": prompt}
            ]

            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                options={
                    "temperature": 0.4,
                    "max_tokens": 1200
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


# Global instance
tuna_ai = TunaAIService()
