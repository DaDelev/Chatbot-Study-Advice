import scrapy
from pathlib import Path

SCRAPED_DATA_PATH = "../data/scraped_data/"


class PdfSpider(scrapy.Spider):
    name = "pdf_spider"

    # Define a list of domains that are allowed in the scraping process
    allowed_domains = ["wim.uni-mannheim.de", "uni-mannheim.de"]

    # limit number of recursively followed links
    custom_settings = {
        "DEPTH_LIMIT": 2
    }

    def start_requests(self):
        # List of URLs that will be parsed by following links (study organization)
        study_org_urls = [
            "https://www.wim.uni-mannheim.de/studium/studienorganisation",
            "https://www.wim.uni-mannheim.de/en/academics/organizing-your-studies/",
            "https://www.uni-mannheim.de/studium/im-studium/studienorganisation/",
            "https://www.uni-mannheim.de/en/academics/during-your-studies/organizing-your-studies/"
        ]

        # List of URLs that will be parsed without following links (examination regulations)
        exam_regs_urls = [
             "https://www.uni-mannheim.de/studium/im-studium/pruefungen/pruefungsordnungen/bachelorpruefungsordnungen/",
             "https://www.uni-mannheim.de/studium/im-studium/pruefungen/pruefungsordnungen/masterpruefungsordnungen/",
             "https://www.uni-mannheim.de/en/academics/during-your-studies/examinations/examination-regulations/examination-regulations-for-masters-programs/"
        ]

        for url in study_org_urls:
            yield scrapy.Request(url=url, callback=self.parse_study_orgs)

        for url in exam_regs_urls:
            yield scrapy.Request(url=url, callback=self.parse_exam_regs)

    def parse_study_orgs(self, response):
        # Check if the content type is HTML
        content_type = response.headers.get('Content-Type', b'').decode('utf-8').lower()
        if 'text/html' in content_type:
            # Download HTML
            page = "_".join(response.url.rstrip("/").split("/")[2:])
            filename = f"{page}.html"
            Path(SCRAPED_DATA_PATH + filename).write_bytes(response.body)
            self.log(f"Saved file {page}")

            # Find links to all PDF files
            pdf_links = response.xpath("//a[contains(@href, '.pdf')]/@href").getall()
            for pdf_link in pdf_links:
                # Download each PDF file
                yield {
                    "file_urls": [response.urljoin(pdf_link)]
                }
            
            # Follow all links that
            # - are inside the list of allowed domains (implicitly with the condition defined above)
            # - are nested inside the div with id='page-content' (this excludes links inside navigation elements etc.)
            for next_page in response.xpath("//div[@id='page-content']/descendant::a/@href").getall():
                yield response.follow(next_page, self.parse_study_orgs)

    def parse_exam_regs(self, response):
        # Find links to all PDF files that are relevant to WIM faculty
        pdf_links_de = response.xpath("//*[contains(text(), 'Fakultät für Wirtschafts\xadinformatik')]/following::ul[1]/descendant::a[contains(@href, '.pdf')]/@href").getall()
        pdf_links_en = response.xpath("//a[(contains(text(), 'Data Science') or contains(text(), 'Business Informatics')) and contains(@href, '.pdf')]/@href").getall()
        for pdf_link in pdf_links_de + pdf_links_en:
            # Download each PDF file
            yield {
                "file_urls": [response.urljoin(pdf_link)]
            }