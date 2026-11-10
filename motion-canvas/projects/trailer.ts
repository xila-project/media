import '../global.css';
import {makeProject} from '@motion-canvas/core';
import intro from '../scenes/intro?scene';
import typography from '../scenes/typography?scene';
import footage from '../scenes/footage?scene';
import architecture from '../scenes/architecture?scene';
import outro from '../scenes/outro?scene';
export default makeProject({scenes:[intro,typography,footage,architecture,outro]});
