import { chromium } from 'playwright';
import { mkdir, readFile } from 'node:fs/promises';
import assert from 'node:assert/strict';

const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || undefined,
  args: ['--enable-unsafe-swiftshader', '--use-angle=swiftshader'] });
const baseURL = process.env.PREVIEW_URL || 'http://localhost:5173';
const folder = new URL('../renders/web/', import.meta.url);
await mkdir(folder, { recursive: true });
try {
  for (const [name, width, height, touch] of [['desktop',1280,800,false],['tablet',820,1180,true]]) {
    const page = await browser.newPage({ viewport: { width,height }, hasTouch:touch, isMobile:touch });
    const errors=[];
    page.on('pageerror',err=>errors.push(String(err)));
    page.on('console',msg=>{ if (msg.type()==='error') errors.push(msg.text()); });
    await page.goto(baseURL);
    await page.waitForSelector('canvas[data-ready="true"]');
    const canvas=page.locator('canvas');
    const initial=await canvas.screenshot();
    await page.getByText('背面',{exact:true}).click();
    assert.ok(!initial.equals(await canvas.screenshot()),'Back view did not change');
    await page.getByRole('button',{name:'正面'}).click();
    const weapon=page.getByRole('button',{name:'武器'});
    await weapon.click();
    assert.equal(await weapon.getAttribute('aria-pressed'),'false');
    assert.ok(!initial.equals(await canvas.screenshot()),'Hidden weapon did not change output');
    await weapon.click();
    if (touch) {
      const cdp=await page.context().newCDPSession(page);
      async function gesture(steps) {
        const before=await canvas.screenshot();
        for (const [i,points] of steps.entries()) {
          await cdp.send('Input.dispatchTouchEvent',{type:i===0?'touchStart':'touchMove',touchPoints:points});
        }
        await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
        assert.ok(!before.equals(await canvas.screenshot()),'Touch gesture did not change view');
      }
      await gesture([[{x:360,y:550}],[{x:420,y:559}],[{x:520,y:565}]]);
      await gesture([[{x:300,y:550,id:0},{x:480,y:550,id:1}],
        [{x:285,y:550,id:0},{x:510,y:550,id:1}],[{x:260,y:550,id:0},{x:540,y:550,id:1}]]);
      await page.getByRole('button',{name:'正面'}).click();
    }
    await page.screenshot({path:new URL(name+'.png',folder).pathname});
    assert.deepEqual(errors,[]);
    console.log(name,width,height,'WebGL loaded; camera and weapon passed;',touch?'touch rotation and pinch passed':'desktop passed');
    await page.close();
  }
  const failurePage = await browser.newPage();
  await failurePage.route('**/*.glb*', route => route.abort());
  await failurePage.goto(baseURL);
  await failurePage.getByText('预览加载失败', { exact: false }).waitFor();
  console.log('Missing GLB produces a visible load error');
  const offline = await browser.newContext({offline:true});
  const singleFile = await offline.newPage();
  const requests = [];
  singleFile.on('request', request => {
    if (/^https?:/.test(request.url())) requests.push(request.url());
  });
  const html = await readFile(new URL('../preview/gordia.html', import.meta.url), 'utf8');
  await singleFile.setContent(html);
  await singleFile.waitForSelector('canvas[data-ready="true"]');
  await singleFile.getByRole('button', {name:'武器'}).click();
  assert.equal(await singleFile.locator('#weapon').getAttribute('aria-pressed'), 'false');
  assert.deepEqual(requests, []);
  console.log('Standalone HTML content rendered offline; zero HTTP requests and weapon toggle passed');
  await offline.close();
} finally {
  await browser.close();
}
