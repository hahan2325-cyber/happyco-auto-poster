import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv(r"C:\Users\CHAU\.gemini\antigravity\scratch\happyco-cloud-poster\.env")
email = os.getenv("CMS_EMAIL") or os.getenv("HAPPYCO_EMAIL")
password = os.getenv("CMS_PASSWORD") or os.getenv("HAPPYCO_PASSWORD")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://happyco.asia/admin/login")
    page.fill('input[name="email"]', email)
    page.fill('input[name="password"]', password)
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")
    
    # Check post row links in /admin/post
    page.goto("https://happyco.asia/admin/post")
    page.wait_for_load_state("networkidle")
    
    first_row = page.evaluate('''() => {
        let r = document.querySelector(".table tbody tr");
        if (!r) return null;
        let links = Array.from(r.querySelectorAll("a")).map(a => ({ text: a.innerText.trim(), href: a.href }));
        let tds = Array.from(r.querySelectorAll("td")).map(td => td.innerText.trim());
        return { links, tds };
    }''')
    print("First row data:", first_row)
    
    # Check blog list on frontend: https://happyco.asia/blog.html
    page.goto("https://happyco.asia/blog.html")
    page.wait_for_load_state("networkidle")
    blog_links = page.evaluate('''() => {
        return Array.from(document.querySelectorAll("a")).map(a => a.href).filter(h => h.includes('happyco.asia') && (h.includes('thiet-ke') || h.includes('blog/'))).slice(0, 10);
    }''')
    print("Frontend blog links:", blog_links)
    
    browser.close()
