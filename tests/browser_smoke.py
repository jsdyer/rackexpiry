from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import tempfile,shutil,threading,json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
with tempfile.TemporaryDirectory() as d:
 shutil.copytree(ROOT/'dist',Path(d)/'rackexpiry')
 server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=d));threading.Thread(target=server.serve_forever,daemon=True).start()
 try:
  with sync_playwright() as p:
   browser=p.chromium.launch();page=browser.new_page(viewport={'width':1440,'height':1000});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto(f'http://127.0.0.1:{server.server_port}/rackexpiry/');page.wait_for_function("document.querySelector('#product').options.length > 10")
   page.locator('#example').click();assert page.locator('#total').inner_text()=='5'
   page.locator('#asset').fill('<img src=x onerror=alert(1)>');page.locator('#product').select_option('php');page.locator('#version').fill('8.5');page.locator('#add button').click();assert page.locator('.item').count()==6;assert page.locator('img').count()==0
   page.locator('#asset').fill('@rack, \"one\"');page.locator('#add button').click();assert page.locator('#total').inner_text()=='7'
   page.locator('#save').click();page.reload();page.wait_for_function("document.querySelector('#total').textContent === '7'")
   with page.expect_download() as download:page.locator('#export').click()
   assert download.value.suggested_filename.endswith('.csv')
   with page.expect_download() as backup:page.locator('#export-json').click()
   assert backup.value.suggested_filename.endswith('.json');payload=Path(backup.value.path()).read_text();assert any(r['asset']=='@rack, \"one\"' for r in json.loads(payload))
   page.locator('#clear').click();page.locator('summary').click();page.locator('#bulk').fill(payload);page.locator('#import').click();assert page.locator('#total').inner_text()=='7'
   page.locator('#asof').fill('2040-01-01');page.locator('#asset').fill('Date-free branch');page.locator('#product').select_option('proxmox-ve');page.locator('#version').fill('9');page.locator('#add button').click();assert 'Support status unknown at assessment date' in page.locator('#inventory').inner_text()
   (ROOT/'browser-checks').mkdir(exist_ok=True);page.screenshot(path=str(ROOT/'browser-checks/desktop.png'),full_page=True)
   page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth <= innerWidth');page.screenshot(path=str(ROOT/'browser-checks/mobile.png'),full_page=True)
   page.locator('#clear').click();assert page.locator('#total').inner_text()=='0';page.locator('#forget').click();assert not errors,errors;browser.close()
 finally:server.shutdown()
