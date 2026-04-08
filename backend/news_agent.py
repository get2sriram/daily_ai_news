import os
from litellm import completion
from search_service import SearchService
import json

class NewsAgent:
    def __init__(self, model="gemini/gemini-3.1-flash-lite-preview"):
        self.model = model
        self.search_service = SearchService()
        # Using stable v1 API for the Gemini 3 series
        os.environ["GEMINI_API_VERSION"] = "v1"

    def get_reliable_sources(self):
        """
        Agentic step to determine top-tier, reliable AI news sources.
        """
        if not os.getenv("GEMINI_API_KEY"):
            # Mock high-volume distribution
            return ["openai.com", "anthropic.com", "deepmind.google", "techcrunch.com", "theverge.com", "wired.com", "technologyreview.com", "huggingface.co", "nvidia.com", "microsoft.com"]

        prompt = """
        Identify the 15 most reliable and authoritative websites for AI news.
        Include a mix of:
        1. Primary AI Labs (OpenAI, Anthropic, DeepMind, NVIDIA, Microsoft, Meta)
        2. Tech News Leaders (TechCrunch, The Verge, WIRED, MIT Technology Review)
        3. Community/Research Hubs (Hugging Face, ArXiv)
        
        Return ONLY a JSON list of domain names. 
        Rank them so the most frequent/authoritative ones are first.
        """
        try:
            response = completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                api_key=os.getenv("GEMINI_API_KEY"),
                api_version="v1"
            )
            content = response.choices[0].message.content
            return json.loads(content.replace("```json", "").replace("```", "").strip())
        except Exception as e:
            print(f"Error determining sources: {e}")
            return ["openai.com", "anthropic.com", "deepmind.google", "techcrunch.com", "theverge.com", "wired.com"]

    def get_summary(self, days: int = 1):
        """
        Determines reliable sources first, then gathers news with source-weighting.
        """
        reliable_domains = self.get_reliable_sources()
        
        # We take the top 8 domains as 'high frequency' sources and search them more deeply
        high_freq_domains = reliable_domains[:8]
        other_domains = reliable_domains[8:]

        categories = ["Major AI Announcements", "AI Models & Breakthroughs", "New AI Tools", "AI Research", "AI Industry News"]
        all_news = []

        # Gather more news from high-frequency domains to ensure weighted distribution
        for cat in categories:
            # High frequency search
            results_high = self.search_service.search_news(cat, days=days, max_results=12, include_domains=high_freq_domains)
            # Standard search for variety
            results_other = self.search_service.search_news(cat, days=days, max_results=5, include_domains=other_domains)
            
            for res in results_high + results_other:
                res["category"] = cat
            all_news.extend(results_high + results_other)

        if not os.getenv("GEMINI_API_KEY"):
            return self._mock_summarize(all_news, count=20)

        prompt = f"""
        Analyze the search results below.
        STRICT REQUIREMENT: Extract exactly 20 of the LATEST news UPDATES from the LAST {days} DAYS.
        - If 'days' is 1, ONLY include news from the last 24 hours.
        - ABSOLUTELY REJECT any news older than {days} days.
        - Ensure the 'publish_date' accurately reflects the timing.
        
        DISTRIBUTION RULE: Ensure a mix of sources, but prioritize selection from high-authority sources like {high_freq_domains}.
        - DO NOT include links to news sites or aggregate listicles.
        - ONLY include specific individual stories.
        
        For each news update, provide:
        1. A punchy title.
        2. A concise 2-sentence summary.
        3. The DIRECT URL to the specific article.
        4. The category.
        5. The publication date (YYYY-MM-DD).
        6. The SOURCE name (e.g. 'TechCrunch', 'OpenAI Blog', 'Wired').

        Format: Valid JSON list of 20 objects with keys: 'title', 'summary', 'url', 'category', 'publish_date', 'source'.

        Search Results:
        {json.dumps(all_news[:100], indent=2)}
        """

        try:
            response = completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"You are a professional AI news editor. You only output valid JSON. You ensure news is from the last {days} days."},
                    {"role": "user", "content": prompt}
                ],
                api_key=os.getenv("GEMINI_API_KEY"),
                api_version="v1"
            )
            content = response.choices[0].message.content
            # Handle potential markdown blocks
            content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except Exception as e:
            print(f"Error during LLM summarization: {e}")
            return self._mock_summarize(all_news, count=20)

    def _mock_summarize(self, all_news, count=20):
        """Returns realistic-looking mock updates with source and date."""
        today = datetime.now().strftime("%Y-%m-%d")
        summary = []
        for i in range(min(count, len(all_news))):
            item = all_news[i]
            summary.append({
                "title": item.get("title", f"AI News Update #{i+1}"),
                "summary": item.get("content", "No specific details found for this update.")[:180] + "...",
                "url": item.get("url", "#"),
                "category": item.get("category", "General AI"),
                "publish_date": today,
                "source": "Reliable AI Source"
            })
        return summary
