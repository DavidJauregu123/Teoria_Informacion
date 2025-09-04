from firecrawl import Firecrawl
import json
import re

# Usa tu API key
fc = Firecrawl(api_key="fc-c3a36c213c9f47e09ef0ecc7bd1ef181")

# URL de la página base de Amazon (puedes elegir una categoría específica)
base_url = "https://www.amazon.com/s?field-keywords=laptops"

# Configura el crawl (por ejemplo, 5 páginas)
limit = 5  # número de páginas a crawlear

# Inicia el crawl
crawl_res = fc.crawl(url=base_url, limit=limit)

# Procesa los resultados
products = []
for page in crawl_res["data"]:
    html_content = page["html"]
    
    # Usamos expresiones regulares o BeautifulSoup para extraer los productos
    product_links = re.findall(r'href="(/dp/[^"]+)"', html_content)
    for link in product_links:
        product_url = f"https://www.amazon.com{link}"
        title_match = re.search(r'aria-label="([^"]+)"', html_content)
        price_match = re.search(r'priceblock_ourprice.*?(\$[\d,\.]+)', html_content)

        title = title_match.group(1) if title_match else "Unknown Title"
        price = price_match.group(1) if price_match else "Price not found"

        products.append({
            "product_url": product_url,
            "title": title,
            "price": price
        })

# Muestra los resultados en formato JSON
print(json.dumps(products, indent=2))
