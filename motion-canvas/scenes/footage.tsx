import {makeScene2D,Rect,Video} from '@motion-canvas/2d';
import {waitFor} from '@motion-canvas/core';
import {Logo,Text} from '../components/brand';
import production from '../../productions/trailer/production.json';
export default makeScene2D(function* (view) {
  view.fill('#000000');
  const logo = Logo({width: 64}); logo.position([-800,-400]); view.add(logo);
  view.add(Text({text:'Xila in motion',fontSize: 44,y:-400}));
  if (production.footage) {
    const video = new Video({src: production.footage,width: 1280,height: 720,y: 30});
    view.add(video); video.play();
  } else {
    view.add(new Rect({width:1280,height:620,stroke:'#555555',lineWidth:2,y:30}));
    view.add(Text({text:'FOOTAGE PLACEHOLDER',fontSize:40,y:0}));
    view.add(Text({text:'Replace with a verified Xila screen recording',fontSize:24,fontWeight:400,y:75}));
  }
  view.add(Text({text: production.footage ? 'Recorded Xila session' : 'Production test • no interface simulation',fontSize:22,fontWeight:400,y:450}));
  yield* waitFor(2.5);
  yield* view.opacity(0,0.5);
});
