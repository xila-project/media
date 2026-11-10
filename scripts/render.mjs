import {createServer} from 'vite';
import {chromium} from 'playwright';
import {mkdir,writeFile,rm,readdir} from 'node:fs/promises';
import {resolve} from 'node:path';
import {renderOptions} from './render-options.mjs';
import {spawnSync} from 'node:child_process';
const options=renderOptions(process.argv.slice(2));
const {production,preset,width,height,fps,duration,outputName}=options;
const run=(command,args)=>{const result=spawnSync(command,args,{stdio:'inherit'}); if(result.status!==0) throw new Error(`${command} failed`);};
run('python3',['scripts/brand.py']);
const directory=resolve('output',production,...(options.scene?[options.scene]:[]));
const frames=resolve(directory,'frames');
await rm(frames,{recursive:true,force:true}); await mkdir(frames,{recursive:true});
const server=await createServer({server:{host:'127.0.0.1',port:0}});
let browser;
try {
  await server.listen();
  browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:{})});
  const page=await browser.newPage();
  page.on('pageerror',error=>console.error(error));
  await page.exposeFunction('saveFrame',async(frame,data)=>{
    if(!Number.isInteger(frame)||frame<0||frame>=duration*fps) throw new Error('Invalid frame');
    await writeFile(resolve(frames,`${String(frame).padStart(6,'0')}.png`),Buffer.from(data.split(',')[1],'base64'));
  });
  await page.goto(`${server.resolvedUrls.local[0]}render.html`,{waitUntil:'networkidle'});
  await server.waitForRequestsIdle();
  await page.waitForFunction(()=>typeof window.runRender==='function');
  await page.evaluate(options=>window.runRender(options),options);
  const count=(await readdir(frames)).length;
  if(count!==duration*fps) throw new Error(`Expected ${duration*fps} frames, got ${count}`);
  run('python3',['scripts/video.py','assemble',frames,resolve(directory,`${outputName}.mp4`),'--fps',String(fps),'--preset',preset]);
  run('python3',['scripts/video.py','validate',resolve(directory,`${outputName}.mp4`),'--width',String(width),'--height',String(height),'--fps',String(fps),'--duration',String(duration)]);
  await writeFile(resolve(directory,'render.json'),JSON.stringify({...options,frames:count},null,2)+'\n');
} finally {await browser?.close(); await server.close();}
