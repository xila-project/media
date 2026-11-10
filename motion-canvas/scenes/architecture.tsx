import {makeScene2D,Rect,Line} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {Logo,Text} from '../components/brand';
export default makeScene2D(function* (view) {
  view.fill('#000000');
  const logo = Logo({width:64}); logo.position([-800,-400]); view.add(logo);
  view.add(Text({text:'Built in Rust. Open to WebAssembly.',fontSize:48,y:-370}));
  const labels = ['Applications · WebAssembly','Xila · Rust core','Platform assembly'];
  for (let i=0;i<labels.length;i++) {
    const y = -160+i*190;
    if(i>0) view.add(new Line({points:[[0,y-135],[0,y-75]],stroke:'#ffffff',lineWidth:2}));
    const box = new Rect({width:1040,height:120,y,stroke:'#ffffff',lineWidth:2,opacity:0});
    box.add(Text({text:labels[i],fontSize:38})); view.add(box);
    yield* box.opacity(1,0.35);
  }
  view.add(Text({text:'Conceptual architecture • not a hardware support matrix',fontSize:20,fontWeight:400,y:450}));
  yield* waitFor(1.45);
  yield* view.opacity(0,0.5);
});
