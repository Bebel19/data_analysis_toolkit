import csv
from datetime import datetime, timedelta
from gnews import GNews
from scripts import ScriptInterface
from utils.logger import logger


class NewsScraper(ScriptInterface):
    def run(self, input_file=None, output_file=None, **kwargs):
        if not output_file:
            raise ValueError("Aucun fichier de sortie spécifié.")

        try:
            start_date = datetime.strptime(kwargs.get("start_date"), '%Y-%m-%d')
            end_date = datetime.strptime(kwargs.get("end_date"), '%Y-%m-%d')
            keyword = kwargs.get("keyword", "")

            fieldnames = ['title', 'url', 'published date', 'description', 'publisher']
            all_articles = []

            for start, end in self.generate_date_ranges(start_date, end_date):
                logger.info(f"Scraping du {start.date()} au {end.date()}")
                gnews = GNews(language='ar', country='MA', max_results=50)
                gnews.start_date = start
                gnews.end_date = end
                articles = gnews.get_news(keyword)
                all_articles.extend(articles)

            with open(output_file, mode='w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for article in all_articles:
                    writer.writerow({
                        'title': article.get('title', 'N/A'),
                        'url': article.get('url', 'N/A'),
                        'published date': article.get('published date', 'N/A'),
                        'description': article.get('description', 'N/A'),
                        'publisher': article['publisher']['title']
                            if 'publisher' in article and 'title' in article['publisher'] else 'N/A'
                    })

            logger.info(f"Scraping terminé. Résultats dans : {output_file}")
        except Exception as e:
            logger.error(f"Erreur dans NewsScraper : {e}")
            raise

    def generate_date_ranges(self, start_date, end_date):
        current = start_date
        while current < end_date:
            next_date = min(current + timedelta(days=7), end_date)
            yield current, next_date
            current = next_date

    def get_metadata(self):
        return {
            "name": "Scraper d'actualités GNews",
            "input_required": False,
            "parameters": {
                "start_date": {
                    "type": "string",
                    "default": "2024-01-01",
                    "help": "Date de début (format AAAA-MM-JJ)"
                },
                "end_date": {
                    "type": "string",
                    "default": "2024-01-08",
                    "help": "Date de fin (format AAAA-MM-JJ)"
                },
                "keyword": {
                    "type": "string",
                    "default": "Maroc",
                    "help": "Mot-clé à rechercher"
                }
            }
        }
