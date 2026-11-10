import assert from 'node:assert/strict';
import {test} from 'node:test';
import {renderOptions} from '../scripts/render-options.mjs';

test('defaults match the trailer specification',()=>{
  const options=renderOptions([]);
  assert.equal(options.width,1920);
  assert.equal(options.height,1080);
  assert.equal(options.fps,30);
  assert.equal(options.duration,15);
});
test('individual scenes have independent output and three-second ranges',()=>{
  const options=renderOptions(['--scene','architecture','--resolution','1280x720','--fps','24']);
  assert.equal(options.duration,3);
  assert.equal(options.outputName,'architecture');
  assert.equal(options.width,1280);
  assert.equal(options.scene,'architecture');
});
test('invalid options fail before a browser or output directory is created',()=>{
  for(const args of [['--fps','0'],['--resolution','1920x0'],['--production','../other'],['--preset','unknown'],['--scene','unknown'],['--production','logo','--scene','outro']]) {
    assert.throws(()=>renderOptions(args));
  }
});
