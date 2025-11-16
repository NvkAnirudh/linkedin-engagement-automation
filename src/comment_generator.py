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
            style: Ignored - we match the post's tone instead
            author_name: Name of the post author

        Returns:
            Dictionary with 'comment', 'tone', and 'reasoning'
        """
        # Build the prompt (style parameter is now ignored in favor of tone matching)
        prompt = self._build_prompt(post_content, author_name)

        print(f"{Fore.CYAN}Generating tone-matched comment using {self.provider}...{Style.RESET_ALL}")

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

    def _build_prompt(self, post_content: str, author_name: str) -> str:
        """Build the AI prompt for comment generation.

        Args:
            post_content: Content of the post
            author_name: Name of the post author

        Returns:
            Formatted prompt string
        """
        emoji_instruction = "Include 1-2 relevant emojis if appropriate for the tone." if self.include_emojis else "Do not use emojis unless the post's tone calls for it."

        author_info = f" by {author_name}" if author_name else ""

        prompt = f"""You are a LinkedIn engagement expert. Generate an authentic, valuable comment for a LinkedIn post{author_info}.

POST CONTENT:
{post_content}

INSTRUCTIONS:
1. ANALYZE THE TONE: Carefully analyze the post's tone and style. Consider:
   - Is it humorous, serious, inspirational, technical, informative, celebratory, thoughtful?
   - What's the writing style? Casual, professional, technical, storytelling?
   - What emotions or energy does it convey?

2. MATCH THE TONE: Your comment should mirror the post's tone and style:
   - If the post is humorous and witty, be humorous and witty
   - If it's technical and informative, be technical and add insight
   - If it's inspirational, be supportive and motivational
   - If it's casual, be casual. If professional, be professional.

3. LENGTH & SUBSTANCE:
   - Don't force a one-liner if the context deserves more substance
   - Can be 1-3 sentences depending on what fits best
   - Add real value - insight, agreement, related perspective, or thoughtful question
   - Avoid generic comments like "Great post!" or "Thanks for sharing!"

4. AUTHENTICITY:
   - Show you actually read and understood the content
   - Reference specific points from the post when appropriate
   - Be genuine and conversational
   - {emoji_instruction}

OUTPUT FORMAT:
Tone: [detected tone and style - be specific, e.g. "humorous, technical, informative"]
Comment: [your tone-matched comment]
Reasoning: [brief explanation of how your comment matches the post's tone and adds value]

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
                    "content": "You are a LinkedIn engagement expert who writes authentic, tone-matched comments that adapt to each post's unique style and energy."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.8,  # Increased for more creative, tone-matched responses
            max_tokens=300    # Increased to allow 1-3 sentence comments
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
            max_tokens=300,    # Increased to allow 1-3 sentence comments
            temperature=0.8,   # Increased for more creative, tone-matched responses
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
