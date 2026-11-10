import {makeScene2D} from '@motion-canvas/2d';
import {all,waitFor} from '@motion-canvas/core';
import {Logo,Text} from '../components/brand';
export default makeScene2D(function* (view) {
  view.fill('#000000');
  const logo = Logo({width: 64}); logo.position([-800,-400]); view.add(logo);
  const title = Text({text: 'Small systems.\nOpen possibilities.',fontSize: 104,lineHeight: 132,y: 35,opacity: 0});
  const sub = Text({text: 'An open-source embedded operating system',fontSize: 26,fontWeight: 400,y: 300,opacity: 0});
  view.add([title,sub]);
  yield* all(title.opacity(1,0.6),title.y(0,0.6));
  yield* sub.opacity(1,0.4);
  yield* waitFor(1.5);
  yield* view.opacity(0,0.5);
});
