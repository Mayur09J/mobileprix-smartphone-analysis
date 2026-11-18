from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = webdriver.Chrome()
driver.get('https://www.smartprix.com/mobiles')
time.sleep(3)

# 1. Handle Filter Checkboxes safely via JavaScript
chkbox1 = driver.find_element(by=By.XPATH, value='/html/body/div/main/aside/div/div[5]/div[2]/label[1]/input')
driver.execute_script("arguments[0].click();", chkbox1)
time.sleep(2)

chkbox2 = driver.find_element(by=By.XPATH, value='/html/body/div/main/aside/div/div[5]/div[2]/label[2]/input')
driver.execute_script("arguments[0].click();", chkbox2)
time.sleep(3)

print("Filters selected. Creating local HTML source backup script...")

# 2. Open a blank HTML file in write mode to initialize the layout
with open('mobile_prix_complete.html', 'w', encoding='utf-8') as f:
    f.write("<html><head><title>Smartprix All Mobiles Source</title></head><body>\n")

old_height = driver.execute_script('return document.body.scrollHeight')
processed_ids = set()  # To keep track of unique phones and avoid duplicating HTML elements

while True:
    try:
        # 3. Capture the inner HTML wrapper source of the visible product elements
        visible_phones = driver.find_elements(By.XPATH, "//div[contains(@class, 'sm-product')]")

        # Open the file in APPEND mode ('a') to keep adding HTML rows dynamically
        with open('mobile_prix_complete.html', 'a', encoding='utf-8') as f:
            for phone in visible_phones:
                try:
                    # Fetch the unique ID attribute assigned to the product card by the website
                    phone_id = phone.get_attribute('id') or phone.text[:30]

                    # If we haven't written this phone's HTML structure yet, append it now
                    if phone_id not in processed_ids:
                        phone_html = phone.get_attribute('outerHTML')  # Extracts raw HTML element source
                        f.write(phone_html + "\n\n")
                        processed_ids.add(phone_id)
                except Exception:
                    continue

        print(f"Captured HTML chunks for {len(processed_ids)} total phones in the file source.")

        # 4. Handle pagination using explicit expectations
        load_more_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'sm-load-more')]"))
        )

        driver.execute_script("arguments[0].click();", load_more_btn)
        time.sleep(3)  # Increase buffer wait time for heavy DOM modifications

        new_height = driver.execute_script('return document.body.scrollHeight')
        print(f"Old Height: {old_height} | New Height: {new_height}")

        if old_height == new_height:
            print("Reached the absolute page boundaries.")
            break

        old_height = new_height

    except Exception as e:
        print("Load More interface target unrendered or dropped. Saving final block data...")
        break

# 5. Capture any remaining elements left in the viewport before closing
with open('mobile_prix_complete.html', 'a', encoding='utf-8') as f:
    final_phones = driver.find_elements(By.XPATH, "//div[contains(@class, 'sm-product')]")
    for phone in final_phones:
        try:
            phone_id = phone.get_attribute('id') or phone.text[:30]
            if phone_id not in processed_ids:
                f.write(phone.get_attribute('outerHTML') + "\n\n")
                processed_ids.add(phone_id)
        except:
            pass
    # Close off the HTML structural container cleanly
    f.write("\n</body></html>")

print(
    f"\n🎉 Successfully compiled full raw HTML dump! Open 'mobile_prix_complete.html' to review all {len(processed_ids)} entries.")
driver.quit()
