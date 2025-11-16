"""AI-powered comment generator for LinkedIn posts."""

from typing import Dict, Optional
from colorama import Fore, Style
import anthropic
import openai


class CommentGenerator:
    """Generate contextual comments using AI."""

    def __init__(
        self,
        provider: str = "openai",
        api_key: str = "",
        model: str = "gpt-4",
        default_style: str = "professional",
        length: str = "short",
        include_emojis: bool = False,
        analyze_tone: bool = True
    ):
        """Initialize comment generator.

        Args:
            provider: AI provider (openai or anthropic)
            api_key: API key for the provider
            model: Model to use
            default_style: Default comment style
            length: Comment length (short, medium, long)
            include_emojis: Include emojis in comments
            analyze_tone: Analyze post tone before generating
        """
        self.provider = provider.lower()
        self.api_key = api_key
        self.model = model
        self.default_style = default_style
        self.length = length
        self.include_emojis = include_emojis
        self.analyze_tone = analyze_tone

        # Initialize AI client
        if self.provider == "openai":
            self.client = openai.OpenAI(api_key=self.api_key)
        elif self.provider == "anthropic":
            self.client = anthropic.Anthropic(api_key=self.api_key)

    def generate_comment(
        self,
        post_content: str,
        style: Optional[str] = None,
        author_name: str = ""
    ) -> Dict[str, str]:
        """Generate a comment for a LinkedIn post.

        Args:
            post_content: Content of the LinkedIn post
            style: Comment style override
            author_name: Name of the post author

        Returns:
            Dictionary with 'comment', 'tone', and 'reasoning'
        """
        style = style or self.default_style

        # Build the prompt
        prompt = self._build_prompt(post_content, style, author_name)

        print(f"{Fore.CYAN}Generating comment using {self.provider}...{Style.RESET_ALL}")

        try:
            if self.provider == "openai":
                response = self._generate_openai(prompt)
            elif self.provider == "anthropic":
                response = self._generate_anthropic(prompt)
            else:
                raise ValueError(f"Unknown AI provider: {self.provider}")

            # Parse response
            result = self._parse_response(response)
            print(f"{Fore.GREEN}Comment generated successfully{Style.RESET_ALL}")

            return result

        except Exception as e:
            print(f"{Fore.RED}Error generating comment: {str(e)}{Style.RESET_ALL}")
            return {
                'comment': "Great insights! Thanks for sharing.",
                'tone': "unknown",
                'reasoning': f"Error: {str(e)}"
            }

    def _build_prompt(self, post_content: str, style: str, author_name: str) -> str:
        """Build the AI prompt for comment generation.

        Args:
            post_content: Content of the post
            style: Desired comment style
            author_name: Name of the post author

        Returns:
            Formatted prompt string
        """
        length_guide = {
            'short': '5-10 words',
            'medium': '10-20 words',
            'long': '20-30 words'
        }

        emoji_instruction = "Include 1-2 relevant emojis." if self.include_emojis else "Do not use emojis."

        tone_instruction = ""
        if self.analyze_tone:
            tone_instruction = """
First, analyze the tone of the post (e.g., inspirational, informative, celebratory, thoughtful, questioning, controversial, personal story, professional achievement).
"""

        author_info = f" by {author_name}" if author_name else ""

        prompt = f"""You are a LinkedIn engagement expert. Generate a thoughtful, authentic one-liner comment for a LinkedIn post{author_info}.

POST CONTENT:
{post_content}

REQUIREMENTS:
{tone_instruction}
- Style: {style} (professional=business-appropriate, casual=friendly and relaxed, enthusiastic=energetic and excited, thoughtful=deep and reflective, supportive=encouraging and positive)
- Length: {length_guide.get(self.length, '5-10 words')}
- {emoji_instruction}
- Be authentic and add value - avoid generic comments like "Great post!"
- Match the tone of the original post
- Show you actually read and understood the content
- Be concise and impactful

OUTPUT FORMAT:
Tone: [detected tone]
Comment: [your one-liner comment]
Reasoning: [brief explanation of why this comment fits]

Generate the comment now:"""

        return prompt

    def _generate_openai(self, prompt: str) -> str:
        """Generate comment using OpenAI.

        Args:
            prompt: The prompt to send

        Returns:
            AI response text
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a LinkedIn engagement expert who writes authentic, valuable comments."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=200
        )

        return response.choices[0].message.content

    def _generate_anthropic(self, prompt: str) -> str:
        """Generate comment using Anthropic Claude.

        Args:
            prompt: The prompt to send

        Returns:
            AI response text
        """
        message = self.client.messages.create(
            model=self.model,
            max_tokens=200,
            temperature=0.7,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return message.content[0].text

    def _parse_response(self, response: str) -> Dict[str, str]:
        """Parse AI response into structured format.

        Args:
            response: Raw AI response

        Returns:
            Dictionary with tone, comment, and reasoning
        """
        result = {
            'tone': 'unknown',
            'comment': '',
            'reasoning': ''
        }

        lines = response.strip().split('\n')

        for line in lines:
            line = line.strip()

            if line.lower().startswith('tone:'):
                result['tone'] = line.split(':', 1)[1].strip()

            elif line.lower().startswith('comment:'):
                result['comment'] = line.split(':', 1)[1].strip()

            elif line.lower().startswith('reasoning:'):
                result['reasoning'] = line.split(':', 1)[1].strip()

        # If comment wasn't found in structured format, use the whole response
        if not result['comment']:
            # Try to extract just the comment part
            for line in lines:
                if line and not line.lower().startswith(('tone:', 'reasoning:', 'output')):
                    result['comment'] = line.strip()
                    break

        # Fallback if still no comment
        if not result['comment']:
            result['comment'] = response.strip()

        return result


# Example usage and testing
if __name__ == "__main__":
    # Example post
    example_post = """
    Excited to share that our team just launched a new AI-powered feature that's
    going to revolutionize how businesses handle customer support. After 6 months
    of development, we're finally seeing it in action. The early feedback has been
    incredible! 🚀

    Special thanks to the amazing engineering team who made this possible.
    """

    # This is just for testing - in production, use proper env vars
    print("Example usage of CommentGenerator")
    print("-" * 50)
    print(f"Post: {example_post[:100]}...")
    print("\nTo test, set up your API keys in .env file and run the main application.")
