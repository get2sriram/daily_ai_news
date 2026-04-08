from tavily import TavilyClient
import os
from datetime import datetime, timedelta

class SearchService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if self.api_key:
            self.client = TavilyClient(api_key=self.api_key)
        else:
            self.client = None

    def search_news(self, category: str = "AI news", days: int = 7, max_results: int = 10, include_domains: list = None):
        """
        Search for specific AI news using explicit time-range filtering.
        """
        if not self.client:
            print(f"No Tavily API key found. Returning mock news for: {category}")
            return self._get_mock_news(category, max_results)

        # Map days to Tavily's time_range parameter
        t_range = "d" if days <= 1 else ("w" if days <= 7 else "m")
        
        query = f"latest {category} article or product announcement"
        try:
            # Using topic="news" and time_range ensures we get absolute latest content
            response = self.client.search(
                query=query, 
                search_depth="advanced", 
                max_results=max_results,
                include_domains=include_domains,
                topic="news",
                time_range=t_range
            )
            return response.get("results", [])
        except Exception as e:
            print(f"Error during search: {e}")
            return self._get_mock_news(category, max_results)

    def _get_mock_news(self, category: str, count: int = 5):
        """Returns more realistic mock news items for UI demonstration."""
        today = datetime.now().strftime("%B %d, %Y")
        all_mocks = {
            "Major AI Announcements": [
                {"title": "OpenAI Unveils 'GPT-5' Preview to Select Partners", "url": "https://openai.com/blog/gpt-5-preview", "content": "OpenAI has started rolling out early access to its next-generation model, promising significantly reduced hallucinations."},
                {"title": "Anthropic Launches Claude 4 with 1M Token Context", "url": "https://anthropic.com/news/claude-4", "content": "The new Claude 4 model sets a new benchmark for long-form reasoning and massive document analysis."},
                {"title": "Google Integrates Real-time Web Search into Gemini 1.5 Pro", "url": "https://google.com/gemini", "content": "Gemini users can now access live internet data with citations for all generated answers."}
            ],
            "New AI Tools": [
                {"title": "Devin 2.0: The AI Software Engineer Gets a Speed Boost", "url": "https://cognition-labs.com/devin", "content": "The latest update to Devin includes a native code editor and support for complex multi-repo migrations."},
                {"title": "Sora API Now Available for Creative Professionals", "url": "https://openai.com/sora", "content": "OpenAI has opened up its text-to-video model for a broader set of testers via a new enterprise API."}
            ]
        }
        
        selected_mocks = all_mocks.get(category, [
            {"title": f"New Breakthrough in {category}", "url": "#", "content": f"Researchers have published a new method for optimizing {category} performance by 40%."}
        ])
        
        # Fill to match count
        while len(selected_mocks) < count:
            selected_mocks.append(selected_mocks[0])
            
        return selected_mocks[:count]
