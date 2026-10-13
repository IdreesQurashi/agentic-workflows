import json
from duckduckgo_search import DDGS
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("LiveSearch")

@mcp.tool()
def search_live_web(query: str, max_results: int = 5) -> str:
    """Perform a live web search for real time information, news, websites, prices, or local data."""
    try:
        results = list(DDGS().text(query, max_results=max_results))
        if not results:
            return f"No search results found for query: {query}"
        formatted = []
        for idx, r in enumerate(results, start=1):
            formatted.append(f"{idx}. {r.get('title', 'No Title')}\nURL: {r.get('href', '')}\nSnippet: {r.get('body', '')}\n")
        return "\n".join(formatted)
    except Exception as e:
        return f"Web search error: {e}"

@mcp.tool()
def search_news(query: str, max_results: int = 5) -> str:
    """Search live breaking news headlines and articles across the world."""
    try:
        results = list(DDGS().news(query, max_results=max_results))
        if not results:
            return f"No news results found for: {query}"
        formatted = []
        for idx, r in enumerate(results, start=1):
            formatted.append(f"{idx}. {r.get('title', '')} (Source: {r.get('source', '')})\nDate: {r.get('date', '')}\nURL: {r.get('url', '')}\nSnippet: {r.get('body', '')}\n")
        return "\n".join(formatted)
    except Exception as e:
        return f"News search error: {e}"

if __name__ == "__main__":
    mcp.run()
