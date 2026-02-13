import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

products = []
isHeadless = True
options = Options()

if isHeadless:
    options.add_argument("--headless=new")

driver = webdriver.Chrome(options=options)
driver.set_window_size(1024, 768)
driver.get("https://www.amazon.com/s?k=laptops")

productListelement = driver.find_element(
    By.CSS_SELECTOR,
    "[class='s-main-slot s-result-list s-search-results sg-row']",
)

productList = productListelement.find_elements(
    By.CSS_SELECTOR, "[class='a-declarative']"
)

for productElement in productList:
    try:
        productData = {}
        titleH2 = productElement.find_element(By.TAG_NAME, "h2")
        linkA = productElement.find_element(By.TAG_NAME, "a")
        productData["title"] = titleH2.text
        productData["url"] = linkA.get_attribute("href")
        priceWholeH2 = productElement.find_element(By.CLASS_NAME, "a-price-whole")
        priceDecimalH2 = productElement.find_element(By.CLASS_NAME, "a-price-decimal")
        priceString = f"{priceWholeH2.text}.{priceDecimalH2.text or '00'}"

        ratingA = productElement.find_element(By.CLASS_NAME, "a-icon-alt")
        productData["ratingString"] = ratingA.get_attribute("innerHTML").split(" ")[0]
        productData["price"] = priceString
        products.append(productData)
    except Exception:
        # Ideally I would better split up the code to get the product div then have error handling for the product div
        # instead I'm just assuming anything that doesn't perfectly fit this isn't a product div and not reading it
        pass

driver.quit()
print(json.dumps(products, indent=2))
