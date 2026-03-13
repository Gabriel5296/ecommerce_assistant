import csv
import time
import re
import os
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

class FlipkartScraper:
    def __init__(self, output_dir="data"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def get_top_reviews(self,product_url,count=2):
        """Get the top reviews for a product.
        """
        options = uc.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-blink-features=AutomationControlled")
        driver = uc.Chrome(options=options, use_subprocess=True, version_main=144)

        if not product_url.startswith("http"):
            driver.quit()
            return "No reviews found"

        try:
            driver.get(product_url)
            time.sleep(4)
            try:
                driver.find_element(By.XPATH, "//button[contains(text(), '✕')]").click()
                time.sleep(1)
            except Exception as e:
                print(f"Error occurred while closing popup: {e}")

            for _ in range(4):
                ActionChains(driver).send_keys(Keys.END).perform()
                time.sleep(1.5)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            review_cards = soup.select("div.vQDoqR:has(div._7dzyg26)")
            print(f"[DEBUG] Found {len(review_cards)} review cards on product page")

            if not review_cards:
                # Save page HTML for inspection
                debug_path = os.path.join(self.output_dir, "debug_reviews.html")
                with open(debug_path, "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                print(f"[DEBUG] Review page HTML saved to {debug_path}")

            seen = set()
            reviews = []

            for card in review_cards:
                title_el = card.select_one("div.v1zwn24")
                body_el = card.select_one("a._1psv1zeh6")
                title = title_el.get_text(strip=True) if title_el else ""
                body = body_el.get_text(separator=" ", strip=True) if body_el else ""
                text = f"{title}: {body}" if title and body else (body or title)
                if text and text not in seen:
                    reviews.append(text)
                    seen.add(text)
                if len(reviews) >= count:
                    break
        except Exception as e:
            print(f"[DEBUG] Exception in get_top_reviews: {e}")
            reviews = []

        driver.quit()
        return " || ".join(reviews) if reviews else "No reviews found"
    
    def scrape_flipkart_products(self, query, max_products=1, review_count=2):
        """Scrape Flipkart products based on a search query.
        """
        options = uc.ChromeOptions()
        driver = uc.Chrome(options=options, use_subprocess=True, version_main=144)
        search_url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
        driver.get(search_url)
        time.sleep(4)

        try:
            driver.find_element(By.XPATH, "//button[contains(text(), '✕')]").click()
        except Exception as e:
            print(f"Error occurred while closing popup: {e}")

        time.sleep(2)
        products = []

        items = driver.find_elements(By.CSS_SELECTOR, "div[data-id]")[:max_products]
        print(f"[DEBUG] Found {len(items)} product cards with 'div[data-id]'")

        if not items:
            # Dump page title and a snippet to help diagnose
            print(f"[DEBUG] Page title: {driver.title}")
            print(f"[DEBUG] Page URL: {driver.current_url}")
            print(f"[DEBUG] Page source (first 2000 chars):\n{driver.page_source[:2000]}")

        for item in items:
            try:
                title = item.find_element(By.CSS_SELECTOR, "div.RG5Slk").text.strip()
                price = item.find_element(By.CSS_SELECTOR, "div.hZ3P6w").text.strip()
                rating = item.find_element(By.CSS_SELECTOR, "div.MKiFS6").text.strip()
                reviews_text = item.find_element(By.CSS_SELECTOR, "span.PvbNMB").text.strip()
                match = re.search(r"\d+(,\d+)?(?=\s+Reviews)", reviews_text)
                total_reviews = match.group(0) if match else "N/A"

                link_el = item.find_element(By.CSS_SELECTOR, "a[href*='/p/']")
                href = link_el.get_attribute("href")
                product_link = href if href.startswith("http") else "https://www.flipkart.com" + href
                match = re.findall(r"/p/(itm[0-9A-Za-z]+)", href)
                product_id = match[0] if match else "N/A"
            except Exception as e:
                print(f"[DEBUG] Error processing item: {e}")
                # Save full card HTML to file for inspection
                card_html = item.get_attribute('outerHTML')
                debug_path = os.path.join(self.output_dir, "debug_card.html")
                with open(debug_path, "w", encoding="utf-8") as f:
                    f.write(card_html)
                print(f"[DEBUG] Full card HTML saved to {debug_path}")
                continue

            top_reviews = self.get_top_reviews(product_link, count=review_count) if "flipkart.com" in product_link else "Invalid product URL"
            products.append([product_id, title, rating, total_reviews, price, top_reviews])

        driver.quit()
        return products
    
    def save_to_csv(self, data, filename="product_reviews.csv"):
        """Save the scraped product reviews to a CSV file."""
        if os.path.isabs(filename):
            path = filename
        elif os.path.dirname(filename):  # filename includes subfolder like 'data/product_reviews.csv'
            path = filename
            os.makedirs(os.path.dirname(path), exist_ok=True)
        else:
            # plain filename like 'output.csv'
            path = os.path.join(self.output_dir, filename)

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["product_id", "product_title", "rating", "total_reviews", "price", "top_reviews"])
            writer.writerows(data)
        