from firecrawl import Firecrawl
import json

# Usa tu API key
fc = Firecrawl(api_key="fc-c3a36c213c9f47e09ef0ecc7bd1ef181")

# URL de la página a scrapear
url = "https://books.toscrape.com/index.html"

# Configura el scrapeo para extraer los nombres y precios de los libros
formats = ["markdown", "html"]  # Puedes elegir los formatos que prefieras

# Scrapea la página
scrape_res = fc.scrape(url, formats=formats)

# Procesa el contenido para extraer libros y precios
# Firecrawl devolverá los datos en Markdown o HTML. Necesitamos extraer lo relevante.
html_content = scrape_res["data"]["html"]

# Puedes usar BeautifulSoup o regex para extraer nombres y precios, pero en Firecrawl también tenemos funciones útiles
import re
from bs4 import BeautifulSoup

# Parseamos el HTML de la página
soup = BeautifulSoup(html_content, "html.parser")

# Extraemos los nombres de los libros y sus precios
books = []
for book in soup.select("article.product_pod"):
    title = book.select_one("h3 a")["title"]
    price = book.select_one(".price_color").get_text()
    books.append({"title": title, "price": price})

# Mostrar los libros extraídos
print(json.dumps(books, indent=2))

