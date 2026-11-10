import {makeScene2D} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {Logo, Text} from '../components/brand';
export default makeScene2D(function* (view) {
  view.fill('#000000');
  const logo = Logo({width: 260});
  logo.opacity(0);
  view.add(logo);
  const caption = Text({text: 'XILA',fontSize: 24,letterSpacing: 12,y: 260,opacity: 0});
  view.add(caption);
  yield* logo.opacity(1, 0.8);
  yield* caption.opacity(1, 0.4);
  yield* waitFor(1.3);
  yield* view.opacity(0, 0.5);
});
