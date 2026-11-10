import {makeScene2D} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {Logo,Text} from '../components/brand';
export default makeScene2D(function* (view) {
  view.fill('#ffffff');
  const logo = Logo({light:true,lockup:true,width:640}); logo.y(-70); logo.opacity(0); view.add(logo);
  view.add(Text({text:'www.xila.dev',fill:'#000000',fontSize:36,fontWeight:400,y:230}));
  yield* logo.opacity(1,0.6);
  yield* waitFor(2.4);
});
