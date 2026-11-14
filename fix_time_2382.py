import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv(r'C:\Users\CHAU\.gemini\antigravity\scratch\happyco-cloud-poster\.env')

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    pg = b.new_page(viewport={'width': 1440, 'height': 900})
    pg.goto('https://happyco.asia/admin/login')
    pg.fill('input[name="email"]', os.getenv('HAPPYCO_EMAIL'))
    pg.fill('input[name="password"]', os.getenv('HAPPYCO_PASSWORD'))
    pg.click('button[type="submit"]')
    pg.wait_for_load_state('networkidle')
    pg.goto('https://happyco.asia/admin/post/2382/edit')
    pg.wait_for_load_state('networkidle')
    pg.wait_for_timeout(1200)

    js_str = pg.evaluate("() => window.nav_submit_form ? window.nav_submit_form.toString() : 'none'")
    print("nav_submit_form:", js_str[:1200])

    # Update picker startDate + timePickerIncrement=1 + trigger apply.daterangepicker
    res = pg.evaluate("""() => {
        const el = document.querySelector('input[name="published_at"]');
        const jq = window.jQuery || window.$;
        const picker = jq && jq(el).data('daterangepicker');
        if (picker && window.moment) {
            picker.timePickerIncrement = 1;
            const m = window.moment('12-11-2026 11:20', 'DD-MM-YYYY HH:mm');
            picker.setStartDate(m);
            picker.setEndDate(m);
            el.value = '12-11-2026 11:20';
            jq(el).trigger('apply.daterangepicker', picker);
            return { pickerStart: picker.startDate.format('YYYY-MM-DD HH:mm'), elVal: el.value };
        }
        return 'no_picker';
    }""")
    print("Updated picker:", res)

    pg.evaluate("""() => {
        for (let k in window.CKEDITOR.instances) window.CKEDITOR.instances[k].updateElement();
        let btn = document.querySelector('button[onclick*="nav_submit_form"]') || document.querySelector('.btn-info.btn-ladda');
        if (btn) btn.click();
    }""")
    pg.wait_for_timeout(4000)

    pg.goto('https://happyco.asia/admin/post')
    pg.wait_for_load_state('networkidle')
    pg.wait_for_timeout(1000)
    row_time = pg.locator('table tbody tr').first.locator('td').nth(4).inner_text().strip()
    print("CMS Row Status/Time AFTER PICKER FIX:", row_time)
    pg.screenshot(path=r'C:\Users\CHAU\.gemini\antigravity\brain\3a554760-1f55-4a71-9c90-718eb795bd64\cms_b2c_11h20_exact_verified.png')
    b.close()
