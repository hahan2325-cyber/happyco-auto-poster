import os
import sys
from pathlib import Path
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
    
    # 1. Check the post we just created to see its content and images
    page.goto("https://happyco.asia/admin/post")
    page.wait_for_load_state("networkidle")
    
    edit_link = page.evaluate('''() => {
        let firstRow = document.querySelector(".table tbody tr");
        if (!firstRow) return null;
        let editBtn = firstRow.querySelector("a[href*='/edit'], .btn-primary, a");
        return editBtn ? editBtn.href : null;
    }''')
    print("Edit link:", edit_link)
    
    if edit_link:
        page.goto(edit_link)
        page.wait_for_load_state("networkidle")
        post_data = page.evaluate('''() => {
            let title = document.querySelector("input[name='title']") ? document.querySelector("input[name='title']").value : '';
            let slug = document.querySelector("input[name='slug']") ? document.querySelector("input[name='slug']").value : '';
            let content = '';
            if (window.CKEDITOR && window.CKEDITOR.instances) {
                for (let k in window.CKEDITOR.instances) {
                    if (document.getElementById(k) && document.getElementById(k).name === 'content') {
                        content = window.CKEDITOR.instances[k].getData();
                    }
                }
            }
            if (!content) {
                let txt = document.querySelector("textarea[name='content']");
                content = txt ? txt.value : '';
            }
            return { title, slug, content };
        }''')
        print("Post Title:", post_data.get("title"))
        print("Post Slug:", post_data.get("slug"))
        print("Content length:", len(post_data.get("content", "")))
        print("Content snippet (first 1000 chars):")
        print(post_data.get("content", "")[:1000])
        
        # Check img src tags inside content
        import re
        imgs = re.findall(r'<img[^>]+src=[\'"]([^\'"]+)[\'"]', post_data.get("content", ""))
        print("\nImages found in post content:")
        for im in imgs:
            print(" -", im)
            
    # 2. Check /admin/media
    page.goto("https://happyco.asia/admin/media")
    page.wait_for_load_state("networkidle")
    
    media_imgs = page.evaluate('''() => {
        return Array.from(document.querySelectorAll("table tr, .media-list-item, .thumbnail, img")).map(el => {
            let img = el.querySelector("img") || (el.tagName === "IMG" ? el : null);
            let link = el.querySelector("a") || (el.tagName === "A" ? el : null);
            return {
                src: img ? img.src : null,
                href: link ? link.href : null,
                text: el.innerText ? el.innerText.trim().substring(0, 50) : ''
            };
        }).filter(x => x.src || x.href).slice(0, 15);
    }''')
    print("\nRecent media in /admin/media:")
    for m in media_imgs:
        print(" -", m)
        
    browser.close()
