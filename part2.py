import argparse
import json

from openai import OpenAI
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def parseArgs():
    parser = argparse.ArgumentParser(prog="InstaPermit Take Home", description="Hi :)")
    parser.add_argument("--query", "-q", default="laptops", type=str)
    parser.add_argument("--isHeadless", "-isH", default=True, type=bool)
    parser.add_argument("--Interest", "-i", default="I am a student", type=str)
    args = parser.parse_args()
    return args


def getProductsData(args):
    products = []
    options = Options()
    if args.isHeadless:
        options.add_argument("--headless=new")

    driver = webdriver.Chrome(options=options)

    # I'm doing this just in case the css changes so I avoid mobile/tablet classes
    driver.set_window_size(1024, 768)

    # query the page to get the results div
    try:
        driver.get(f"https://www.amazon.com/s?k={args.query}")
        productListelement = driver.find_element(
            By.CSS_SELECTOR,
            "[class='s-main-slot s-result-list s-search-results sg-row']",
        )
        productList = productListelement.find_elements(
            By.CSS_SELECTOR, "[class='a-declarative']"
        )
    except:
        print(
            f"https://www.amazon.com/s?k={args.query} is a invalid page that can't find the results row!"
        )
        return

    for productElement in productList:
        try:
            productData = {}
            titleH2 = productElement.find_element(By.TAG_NAME, "h2")
            linkA = productElement.find_element(By.TAG_NAME, "a")
            productData["title"] = titleH2.text
            productData["url"] = linkA.get_attribute("href")
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
        except Exception:
            # Assume if a results page(error handeled above) then any thing that doesn't fit this isn't a product listing
            pass

    driver.quit()
    return products


def main(args):
    client = OpenAI()
    products = getProductsData(args)

    if len(products) < 1:
        print(f"No Amazon listings found for query: {args.query}")
        return

    # I want to shorten the data such as not including the links
    cleanedProducts = []
    for product in products:
        cleanedProducts.append({k: v for k, v in product.items() if k != "url"})

    productJson = json.dumps(cleanedProducts)
    responseJSON = client.responses.create(
        model="gpt-5-mini",
        input=f"Here is {args.query} listings {productJson}, based off the price and title, append to each field a cateogry out of (budget, gaming, professional, casual). Give me a one sentence summary also with the key summary based on this info about me {args.Interest}. and append it to the record and give me back the updated data.",
    )
    enhancedProductsDict = responseJSON.output[1].content[0].text
    enhancedProducts = json.loads(enhancedProductsDict)

    # add data back
    for ep in enhancedProducts:
        matching_product = next(
            (p for p in products if p["title"] == ep["title"]), None
        )
        if matching_product:
            ep["url"] = matching_product["url"]

    print(json.dumps(enhancedProducts, indent=2))


if __name__ == "__main__":
    main(parseArgs())
