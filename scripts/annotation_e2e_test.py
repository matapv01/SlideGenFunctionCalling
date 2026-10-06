"""Playwright end-to-end test for annotation_web against scripts/annotation_mock_server.py (port 8765)."""
import json, sys, urllib.request
from playwright.sync_api import sync_playwright
S=sys.argv[1]; URL='http://127.0.0.1:8765/'
def dump(): return json.load(urllib.request.urlopen(urllib.request.Request(URL+'api/_dump', data=b'{"code":"abc123"}', headers={'Content-Type':'application/json'})))
with sync_playwright() as p:
    b=p.chromium.launch(); page=b.new_page(viewport={'width':1400,'height':1000}); errors=[]
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.goto(URL)
    page.fill('#code-input','wrong'); page.click('#login-form button'); page.wait_for_selector('#login-error:not([hidden])')
    print('bad code ->', page.inner_text('#login-error'))
    page.fill('#code-input','abc123'); page.click('#login-form button'); page.wait_for_selector('#guide-view:not([hidden])')
    print('guide shown')
    page.click('#start-button'); page.wait_for_selector('#rate-view:not([hidden])')
    print('pair label:', page.inner_text('#pair-label'), '| progress:', page.inner_text('#progress-label'))
    for k in '12312': page.keyboard.press(k)          # only 5 of 6 criteria
    page.keyboard.press('Enter'); page.wait_for_timeout(300)
    print('incomplete submit ->', page.inner_text('#save-status'))
    page.keyboard.press('3'); page.check('#flags-A input[data-flag=broken]')
    page.keyboard.press('Enter'); page.wait_for_function("document.querySelector('#pair-label').textContent.startsWith('Cặp 2')")
    print('after submit:', page.inner_text('#pair-label'), '|', page.inner_text('#progress-label'))
    page.screenshot(path=S+'/rate_view.png', full_page=True)
    page.click('#prev-button'); page.wait_for_timeout(200)
    restored=page.evaluate("[...document.querySelectorAll('input[type=radio]:checked')].map(i=>i.name+'='+i.value)")
    print('prev restores answers:', restored, '| broken A checked:', page.is_checked('#flags-A input[data-flag=broken]'))
    page.click('#next-button'); page.wait_for_function("document.querySelector('#pair-label').textContent.startsWith('Cặp 2')")
    page.reload(); page.wait_for_selector('#rate-view:not([hidden])')
    print('after reload resumes at:', page.inner_text('#pair-label'))
    for _ in range(2):
        for k in '213213': page.keyboard.press(k)
        page.keyboard.press('Enter'); page.wait_for_timeout(400)
    page.wait_for_selector('#done-view:not([hidden])'); print('done view shown |', page.inner_text('#progress-label'))
    d=dump(); print('stored ratings:', len(d), '| p0 =', d.get('A1|p0'))
    print('JS errors:', errors or 'none'); b.close()
