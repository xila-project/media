import {createServer} from 'vite';
import {chromium} from 'playwright';
import {mkdir,writeFile,rm,readdir} from 'node:fs/promises';
import {resolve} from 'node:path';
import {parseArgs} from 'node:util';
import {spawnSync} from 'node:child_process';
const {values} = parseArgs({options:{production:{type:'string',default:'trailer'},resolution:{type:'string',default:'1920x1080'},fps:{type:'string',default:'30'},preset:{type:'string',default:'medium'}}});
const {production,preset}=values;
const [width,height]=values.resolution.split('x').map(Number);
const fps=Number(values.fps);
if(!['trailer','logo'].includes(production) || !['1920x1080','1280x720','960x540'].includes(values.resolution) || ![24,30,60].includes(fps) || !['fast','medium','slow'].includes(preset)) throw new Error('Invalid production, resolution, FPS or preset');
const duration=production==='logo'?3:15;
const run=(command,args)=>{const result=spawnSync(command,args,{stdio:'inherit'}); if(result.status!==0) throw new Error(`${command} failed`);};
run('python3',['scripts/brand.py']);
const directory=resolve('output',production);
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
  await page.evaluate(options=>window.runRender(options),{production,fps,width,height,duration});
  const count=(await readdir(frames)).length;
  if(count!==duration*fps) throw new Error(`Expected ${duration*fps} frames, got ${count}`);
  run('python3',['scripts/video.py','assemble',frames,resolve(directory,`${production}.mp4`),'--fps',String(fps),'--preset',preset]);
  run('python3',['scripts/video.py','validate',resolve(directory,`${production}.mp4`),'--width',String(width),'--height',String(height),'--fps',String(fps),'--duration',String(duration)]);
  await writeFile(resolve(directory,'render.json'),JSON.stringify({production,width,height,fps,duration,preset,frames:count},null,2)+'\n');
} finally {await browser?.close(); await server.close();}
