from serpapi import GoogleSearch

class WebSearchClient:
    """
    Клиент SerpAPI для поиска Google (free limited/paid).
    """

    def __init__(self, api_key: str):
        self.api_key = api_key

    def search(self, query: str, num_results: int = 3):
        """
        Выполняет поиск по запросу и возвращает краткие результаты.
        :param query: поисковый запрос
        :param num_results: макс. число результатов
        :return: список dict [{'title': ..., 'link': ..., 'snippet': ...}]
        """
        params = {
            "q": query,
            "num": num_results,
            "hl": "ru",
            "api_key": self.api_key
        }
        try:
            # ВАЖНО: создаем новый объект GoogleSearch с параметрами
            search = GoogleSearch(params)
            res = search.get_dict()

            results = []
            for item in res.get("organic_results", [])[:num_results]:
                results.append({
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "snippet": item.get("snippet"),
                })
            return {"success": True, "results": results}
        except Exception as e:
            return {"success": False, "error": str(e)}
