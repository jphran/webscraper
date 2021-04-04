from urllib.request import urlopen
from bs4 import BeautifulSoup as soup


class PageScraper:
    """
    Only accepts html pages
    """
    def __init__(self, page_url: str) -> None:
        self.url = page_url
        self.containers = None

        # load in url
        client = urlopen(self.url)
        self.page_html = client.read()
        client.close()

        self.page_soup = soup(self.page_html, 'html.parser')

    def get_all_containers(self, component_type: str, component: dict):
        """Grabs all containers of interest from webpage"""
        self.containers = self.page_soup.findAll(component_type, component)

    def search_containers_for(self, items: dict) -> str:
        """ Returns csv formatted string with desired container info"""
        result = ''
        for container in self.containers:
            for key, value in items.items():
                ioi = container.findAll(key, value)
                if ioi:
                    result += ioi[0].text.replace(',', '') + ','
            result += '\n'

        return result
