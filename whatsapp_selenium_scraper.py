# whatsapp_selenium_scraper.py
import time, random, re, json, requests, argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# CONFIG - change DJANGO_API_URL to your running django server
DJANGO_API_URL = "http://127.0.0.1:8000/api/save-members/"  # <- ensure runserver active
USER_DATA_DIR = "./selenium_profile"  # saves login session; change if needed
MAX_MEMBERS = 500  # safety cap
WAIT_TIMEOUT = 60

def hs(a=0.6, b=1.2):
    time.sleep(random.uniform(a,b))

def start_driver():
    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
    # options.add_argument("--disable-gpu")
    # don't run headless — visible browser looks more human
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def wait_for_login(driver, timeout=120):
    print("Open WhatsApp Web and scan QR if needed (or reuse saved session). Waiting...")
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true']"))
    )
    print("Logged in / ready.")

def open_chat_by_name(driver, group_name):
    # search box selector may vary; try to find the contenteditable search
    try:
        search_box = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div[contenteditable='true'][data-tab]"))
        )
        search_box.click(); hs(0.2,0.4)
        search_box.clear(); hs(0.1,0.2)
        search_box.send_keys(group_name); hs(0.8,1.2)
        search_box.send_keys(Keys.ENTER); hs(1.0,1.5)
        return True
    except Exception as e:
        print("Could not open by search:", e)
        return False

def open_group_info(driver):
    try:
        header = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "header"))
        )
        header.click(); hs(0.6,1.2)
        return True
    except Exception as e:
        print("Failed to open group header:", e)
        return False

def expand_members_panel(driver):
    # find a region that scrolls (info modal)
    try:
        region = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='region']"))
        )
    except Exception as e:
        print("Members region not found:", e)
        return None

    last = driver.execute_script("return arguments[0].scrollHeight", region)
    for _ in range(40):
        driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", region)
        hs(0.6, 1.0)
        new = driver.execute_script("return arguments[0].scrollHeight", region)
        if new == last:
            break
        last = new
    return region

def scrape_members(driver):
    members = []
    # Try common XPath/CSS patterns
    # 1) spans with title inside region (display names)
    elems = driver.find_elements(By.XPATH, "//div[@role='region']//span[@title]")
    if not elems:
        elems = driver.find_elements(By.XPATH, "//div[contains(@data-testid,'cell-frame-container')]")
    print("candidate elements:", len(elems))
    for el in elems:
        try:
            name = el.get_attribute("title") or el.text.splitlines()[0].strip()
            # parent text might contain phone; fallback often empty
            parent = el.find_element(By.XPATH, "./ancestor::div[1]")
            text = parent.text or ""
            phone_match = re.search(r'(\+?\d[\d\-\s\(\)]{6,}\d)', text)
            phone = phone_match.group(1).replace(" ", "").replace("-", "") if phone_match else ""
            members.append({"name": name.strip(), "phone": phone.strip()})
            if len(members) >= MAX_MEMBERS:
                break
        except Exception:
            continue

    # dedupe
    seen = set()
    cleaned = []
    for m in members:
        key = (m.get("phone") or m.get("name")).strip()
        if key and key not in seen:
            seen.add(key)
            cleaned.append(m)
    return cleaned

def post_to_django(group_name, link, members):
    if not DJANGO_API_URL:
        print("DJANGO_API_URL not set. Printing members instead.")
        print(json.dumps({"group_name":group_name, "link":link, "numbers":members}, indent=2))
        return
    try:
        r = requests.post(DJANGO_API_URL, json={"group_name":group_name, "link":link, "numbers":members}, timeout=30)
        print("POST status:", r.status_code, r.text)
    except Exception as e:
        print("Failed to POST to Django API:", e)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", help="Group name to search", default=None)
    parser.add_argument("--link", help="Group invite link (optional)", default=None)
    args = parser.parse_args()

    driver = start_driver()
    driver.get("https://web.whatsapp.com")
    wait_for_login(driver, timeout=120)

    if args.link:
        driver.get(args.link)
        hs(3,5)
    elif args.name:
        ok = open_chat_by_name(driver, args.name)
        if not ok:
            print("Open the group manually and press Enter to continue.")
            input()
    else:
        print("Open the group manually in the browser, then press Enter to continue.")
        input()

    if not open_group_info(driver):
        print("Please open group info manually, then press Enter.")
        input()

    expand_members_panel(driver)
    hs(0.6,1.0)
    members = scrape_members(driver)
    print("Scraped members count:", len(members))
    group_name = args.name or (args.link.split('/')[-1] if args.link else "unknown")
    post_to_django(group_name, args.link or "", members)

    print("Done. Keep browser open to inspect, then close manually.")
    # driver.quit()

if __name__ == "__main__":
    main()
