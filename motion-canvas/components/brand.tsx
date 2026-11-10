import {Img, Txt, type TxtProps} from '@motion-canvas/2d';
import symbolWhite from '../../assets/brand/upstream/assets/symbol/xila-symbol-white.svg';
import symbolBlack from '../../assets/brand/upstream/assets/symbol/xila-symbol-black.svg';
import lockupWhite from '../../assets/brand/upstream/assets/lockup/xila-horizontal-white.svg';
import lockupBlack from '../../assets/brand/upstream/assets/lockup/xila-horizontal-black.svg';

// Images preserve upstream paths and transforms. Reserve 25% clear space around them.
export function Logo({light = false, lockup = false, width = 240}) {
  return new Img({src: lockup ? (light ? lockupBlack : lockupWhite) : (light ? symbolBlack : symbolWhite), width});
}
export function Text(props: TxtProps) {
  return new Txt({fontFamily: 'Montserrat',fontWeight: 600,fill: '#ffffff',fontSize: 64,...props});
}
