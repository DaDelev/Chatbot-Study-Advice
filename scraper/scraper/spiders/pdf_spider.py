import scrapy


class PdfSpider(scrapy.Spider):
    name = "pdf_spider"

    # Define a list of domains that are allowed in the scraping process
    allowed_domains = ['wim.uni-mannheim.de']
    # Define a list of URLs that will be used to make the start requests
    start_urls = [
        "https://www.wim.uni-mannheim.de/studium/studienorganisation"
    ]

    # limit number of recursively followed links
    custom_settings = {
        "DEPTH_LIMIT": 2
    }

    def parse(self, response):
            # Find links to all PDF files
            pdf_links = response.xpath("//a[contains(@href, '.pdf')]/@href").getall()
            for pdf_link in pdf_links:
                # Download each PDF file
                yield {
                    'file_urls': [response.urljoin(pdf_link)]
                }
            
            # Follow all links that
            # - are not part of a nav element
            # - are inside the list of allowed domains (implicitly with the condition defined above)
            for next_page in response.xpath("//a[not(ancestor::nav)]/@href").getall():
                yield response.follow(next_page, self.parse)