/** Port of Core's timeline at dab153676f7d2c02cbee57fa49211ed5db7660cf.
 * Keep fixed-point truncation and child order TL, BL, BR, TR for parity.
 * Source: libraries/bootsplash/src/lib.rs (Apache-2.0).
 */
export const INTRO = 900;
export const PERIOD = 1600;
const ONE = 1024;
export const CLOCKWISE_RANK = [0, 3, 2, 1];
export const DIRECTION = [
  [-1, -1],
  [-1, 1],
  [1, 1],
  [1, -1],
] as const;
const div = (a: number, b: number) => Math.trunc(a / b);
const progress = (time: number, start: number, duration: number) =>
  Math.max(0, Math.min(ONE, div((time - start) * ONE, duration)));
export function squareOpacity(time: number) {
  return div(progress(time, 0, 240) * 255, ONE);
}
export function introArm(index: number, time: number, size: number) {
  const remaining =
    ONE - progress(time, 150 + CLOCKWISE_RANK[index] * 100, 450);
  const eased = ONE - div(div(remaining * remaining, ONE) * remaining, ONE);
  return {
    offset: div((ONE - eased) * div(size, 5), ONE),
    opacity: div(eased * 255, ONE),
  };
}
export function loopArm(
  index: number,
  time: number,
  size: number,
  firstCycle: boolean,
) {
  const start = (CLOCKWISE_RANK[index] * PERIOD) / 4;
  if (firstCycle && time < start) return { offset: 0, opacity: 255 };
  const phase = (((time - start) % PERIOD) + PERIOD) % PERIOD;
  if (phase >= PERIOD / 2) return { offset: 0, opacity: 255 };
  const p = div(phase * ONE, PERIOD / 2);
  const parabola = div(4 * p * (ONE - p), ONE);
  const amount = div(parabola * parabola, ONE);
  return {
    offset: div(amount * Math.max(div(size, 20), 1), ONE),
    opacity: 255 - div(amount * 75, ONE),
  };
}
