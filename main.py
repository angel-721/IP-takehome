import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def main():
    productList = []  # Uncommented
    isHeadless = True
    link = "https://www.amazon.com/s?k=laptops"
    options = Options()

    if isHeadless:
        options.add_argument("--headless=new")

    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1024, 768)
    driver.get(link)

    productListelement = driver.find_element(
        By.CSS_SELECTOR,
        "[class='s-main-slot s-result-list s-search-results sg-row']",
    )

    productList = productListelement.find_elements(
        By.CSS_SELECTOR, "[class='a-declarative']"
    )

    products = []  # Create new list for product data

    for productElement in productList:
        try:
            productData = {}  # Uncommented - create new dict for each product

            titleH2 = productElement.find_element(By.TAG_NAME, "h2")
            linkA = productElement.find_element(By.TAG_NAME, "a")
            productData["title"] = titleH2.text  # Uncommented
            productData["link"] = linkA.get_attribute("href")  # Uncommented

            priceWholeH2 = productElement.find_element(By.CLASS_NAME, "a-price-whole")
            priceDecimalH2 = productElement.find_element(
                By.CLASS_NAME, "a-price-decimal"
            )
            priceString = f"{priceWholeH2.text}.{priceDecimalH2.text or '00'}"

            ratingA = productElement.find_element(By.CLASS_NAME, "a-icon-alt")
            productData["ratingString"] = ratingA.get_attribute("innerHTML").split(" ")[
                0
            ]
            productData["price"] = priceString

            products.append(productData)

        except:
            continue

    driver.quit()
    print(f"Total products: {len(products)}")
    print(json.dumps(products, indent=2))  # Print products list


if __name__ == "__main__":
    main()
