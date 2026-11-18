import { Img, Line, makeScene2D, Node, Path, Rect } from "@motion-canvas/2d";
import { createSignal, easeOutCubic, tween } from "@motion-canvas/core";
import { Logo } from "../../components/brand";
import benchImage from "../../../assets/images/makerspace-bench/bench.jpg";
import gadgetImage from "../../../assets/images/makerspace-bench/gadgets.jpg";
import browserImage from "../../../assets/images/makerspace-bench/browser-login.png";
import nativeImage from "../../../assets/images/screens/screen-ad6d93688499941ed49ecc6f361033b648f413dd47ce8e5c9269f48d87a89613.png";
import production from "../../../productions/makerspace-bench/production.json";
import transcript from "../../../productions/not-your-regular/takes/001/transcript-words.json";
import {
  board,
  chip,
  cobalt,
  coral,
  ink,
  paper,
  plate,
  scope,
  tape,
  traces,
  word,
} from "./props";

const { start, end } = production.audio;
const beat = 60 / production.audio.bpm;
const clamp = (x: number) => Math.max(0, Math.min(1, x));

// Word starts from the take-001 transcript. Long syllables are subdivided by ear
// for the mascot's preview blink, pending alignment to the v2 recording.
const voiceRanges = [
  [24.34, 24.73],
  [26.98, 27.65],
  [29.32, 29.99],
  [32.36, 49.2],
];
const extraSyllables = [
  24.52, 27.45, 29.78, 33.03, 33.22, 33.79, 38.67, 38.89, 40.32, 42.63, 42.83,
  43.42, 43.66, 46.15, 46.41, 48.04,
];
const syllables = [
  ...transcript.words
    .filter(({ start: at }) =>
      voiceRanges.some(([from, to]) => at >= from && at < to),
    )
    .map(({ start: at }) => at),
  ...extraSyllables,
];

export default makeScene2D(function* (view) {
  const clock = createSignal(start);
  const pulse = () =>
    Math.max(
      ...syllables.map((at) => {
        const dt = clock() - at;
        return dt >= 0 ? Math.exp(-dt * 23) : 0;
      }),
    );
  const kick = () => Math.exp(-((clock() - start) % beat) * 12);
  view.fill(ink);

  function shot(from: number, to: number, ...layers: Node[]) {
    const stage = new Node({
      opacity: () => Number(clock() >= from && clock() < to),
      children: layers,
    });
    view.add(stage);
    return stage;
  }

  const bench = (scale = 1.02, y = 0, x = 0) => plate(benchImage, scale, y, x);
  function mascot(x: number, y: number, scale: number, rotation = -8) {
    const prop = board(pulse);
    prop.position([x, y]);
    prop.scale(scale);
    prop.rotation(rotation);
    return prop;
  }

  const opener = shot(
    start,
    24.34,
    bench(),
    mascot(352, 240, 1.12, -9),
    tape(
      () => (clock() < 23.48 ? "CAN IT" : "CAN IT RUN APPS?"),
      685,
      { x: -269, y: 93, rotation: -7 },
      65,
    ),
    tape("while (true)", 296, { x: -647, y: 366, rotation: 8 }, 34, paper),
  );
  opener.scale(() => 1 + 0.06 * clamp((clock() - start) / 1.14));

  const closeChip = mascot(0, 95, 2.8, 0);
  closeChip.scale(() => 2.8 + 7 * clamp((clock() - 24.35) / 0.17) ** 3);
  closeChip.position(() => [
    -80 * clamp((clock() - 24.35) / 0.17),
    95 - 240 * clamp((clock() - 24.35) / 0.17),
  ]);
  shot(
    24.34,
    24.53,
    traces(),
    closeChip,
    tape("PLURAL!", 510, { x: -475, y: -251, rotation: -6 }, 92),
    tape(
      "Microcontroller Wasm · roadmap",
      640,
      { x: -420, y: -132, rotation: -6 },
      33,
      cobalt,
    ),
  );
  const gadgets = shot(
    24.53,
    25.1,
    plate(gadgetImage, 1.06),
    tape("PLURAL!", 530, { x: 58, y: -349, rotation: -4 }, 100),
    tape(
      "Fern Pings · imagined app",
      470,
      { x: -365, y: 189, rotation: -8 },
      29,
      paper,
    ),
    tape(
      "Toast Forecast · imagined app",
      540,
      { x: 460, y: 296, rotation: 5 },
      29,
      paper,
    ),
    tape(
      "Microcontroller Wasm · roadmap",
      640,
      { x: 116, y: -216, rotation: 3 },
      33,
      cobalt,
    ),
  );
  gadgets.scale(() => 1 + 0.08 * clamp((clock() - 24.53) / 0.57));

  // Overhead crash into the datasheet. File tabs rise from its binding.
  const book = new Node({ rotation: -10, position: [-112, 105] });
  for (let i = 8; i >= 0; i--) {
    book.add(
      new Rect({
        y: i * 3,
        x: i * 3,
        size: [1340, 730],
        fill: i ? "#d6c8b7" : paper,
        lineWidth: 2,
        stroke: "#c1aa9c",
        radius: 12,
        shadowColor: "#15172c55",
        shadowOffset: [3, 6],
        shadowBlur: 8,
      }),
    );
  }
  book.add(new Rect({ width: 5, height: 727, fill: "#c8ac9e" }));
  book.add(word("NANO 33 BLE", 38, cobalt).position([-354, -274]));
  book.add(word("DATASHEET", 78, ink).position([-351, -181]));
  book.add(word("WITH FILES?", 79, ink).position([-348, -63]));
  for (let i = 0; i < 8; i++) {
    book.add(
      new Rect({
        x: -327,
        y: 35 + i * 31,
        width: 460 - (i % 3) * 75,
        height: 5,
        fill: "#958aa2",
      }),
    );
  }
  book.add(
    tape(
      () => (clock() >= 26.98 ? "AND USERS!" : "LittleFS"),
      510,
      {
        x: 350,
        y: -156,
        rotation: 5,
        scale: () => 1 + 0.18 * Math.exp(-Math.abs(clock() - 26.98) * 15),
      },
      64,
      cobalt,
    ),
  );
  book.add(word("/devices/gpio/d13", 35, ink).position([311, -9]));
  book.add(
    new Line({
      points: [
        [125, 21],
        [499, 21],
      ],
      stroke: "#958aa2",
      lineWidth: 3,
    }),
  );
  // Slide the paper under the board, then swing it past the lens on the last beat.
  book.x(() => -112 - 1080 * clamp((clock() - 27.69) / 0.19) ** 3);
  book.rotation(() => -10 + 22 * clamp((clock() - 27.69) / 0.19) ** 3);
  const filesBoard = mascot(440, 218, 1.14, 12);
  shot(25.1, 27.88, bench(1.22, -120), book, filesBoard).scale(
    () => 1.03 + 0.04 * clamp((clock() - 25.1) / 2.78),
  );

  // ALIX is a gloved silhouette. The board is still a separate photographic prop.
  const hand = new Path({
    data: "M 345 680 L 118 335 C 61 248 -18 134 -72 81 C -121 39 -95 -25 -43 -16 L 37 24 L -10 -79 C -28 -129 14 -161 58 -123 L 145 -33 C 111 -123 151 -164 198 -121 L 271 -24 C 248 -98 298 -114 335 -57 L 413 102 C 478 208 475 264 473 318 L 635 680 Z",
    fill: "#292d56",
    stroke: "#536fbb",
    lineWidth: 4,
    shadowColor: "#050819bb",
    shadowOffset: [15, 18],
    shadowBlur: 30,
  });
  const held = mascot(166, -2, 1.28, -7);
  const gesture = new Node({ children: [hand, held], x: 375, y: 162 });
  gesture.y(() => 162 - 100 * easeOutCubic(clamp((clock() - 29.32) / 0.39)));
  shot(
    27.88,
    30.32,
    bench(1.08, -28),
    gesture,
    tape(
      () => (clock() < 29.32 ? "SO WHERE’S THE" : "YOU’RE"),
      632,
      { x: -420, y: 18, rotation: -4 },
      66,
      paper,
    ),
    tape(
      () => (clock() < 29.32 ? "REAL COMPUTER?" : "HOLDING IT."),
      761,
      { x: -356, y: 147, rotation: 3 },
      73,
    ),
  );

  const invoice = new Rect({
    size: [963, 700],
    y: 28,
    x: -114,
    rotation: -12,
    fill: paper,
    shadowBlur: 26,
    shadowColor: "#080b26c9",
    shadowOffset: [12, 16],
    children: [
      word("COMPUTER ORDER", 45, cobalt).position([0, -248]),
      new Line({
        points: [
          [-380, -175],
          [380, -175],
        ],
        stroke: "#657296",
        lineWidth: 3,
        lineDash: [14, 11],
      }),
      word("I ORDERED A", 79, ink).position([0, -54]),
      word("REAL COMPUTER.", 86, ink).position([0, 72]),
      word("QTY  01     •     SIZE: POCKET", 32, ink).position([0, 245]),
    ],
  });
  invoice.rotation(() => -12 + 14 * clamp((clock() - 32.13) / 0.23));
  invoice.x(() => -114 + 1210 * clamp((clock() - 32.14) / 0.22) ** 3);
  shot(30.32, 32.36, bench(1.19, -66), invoice, mascot(663, 276, 0.59, 17));

  function hook(from: number, osAt: number, to: number, close: boolean) {
    const { housing, glass } = scope();
    const traceZoom = () =>
      close ? 0 : 0.92 * clamp((clock() - to + 0.14) / 0.14) ** 3;
    housing.rotation(close ? 6 : -5);
    housing.x(() => 145 * traceZoom());
    housing.y(() => -240 * traceZoom());
    housing.scale(
      () =>
        1.02 +
        0.09 * clamp((clock() - osAt) / 0.24) +
        kick() * 0.012 +
        traceZoom(),
    );
    const waveform = new Line({
      points: () =>
        Array.from({ length: 106 }, (_, i) => {
          const x = (i - 52) * 11;
          const amplitude =
            7 + (51 + 52 * pulse()) * Math.exp(-((x / 245) ** 2));
          return [x, 233 + Math.sin(i * 0.42 - clock() * 28) * amplitude];
        }),
      stroke: coral,
      lineWidth: 5,
      shadowColor: coral,
      shadowBlur: 19,
    });
    glass.add(waveform);
    const headline = word(
      () =>
        clock() >= osAt
          ? "O–S!"
          : clock() >= from + 0.48
            ? "REGULAR!"
            : "NOT YOUR",
      164,
      "#ff685e33",
    );
    headline.position([0, -38]);
    headline.stroke("#ffc2ac");
    headline.lineWidth(3.5);
    headline.shadowColor(coral);
    headline.shadowBlur(16);
    glass.add(headline);
    glass.add(word("CH 1     |     128 BPM", 28, coral).position([-330, -278]));
    shot(from, to, bench(close ? 1.36 : 1.15), housing);
  }
  hook(32.36, 33.58, 34.04, false);

  const silicon = chip();
  silicon.rotation(-7);
  silicon.add(word("A REAL OS", 126).position([0, -119]));
  silicon.add(word("ON A CHIP,", 116, "#d0d9fc").position([0, 20]));
  silicon.add(word("NO LESS.", 89, coral).position([0, 155]));
  silicon.scale(
    () => 1.02 + 0.22 * easeOutCubic(clamp((clock() - 34.04) / 0.33)),
  );
  const macro = mascot(658, 363, 0.74, 9);
  shot(34.04, 35.42, traces(), silicon, macro);

  // Match the desktop image's staircase to a cut-paper placeholder in the tab.
  const monitor = new Rect({
    size: [1030, 694],
    x: 294,
    y: -42,
    radius: 30,
    fill: "#282b46",
    stroke: "#6b87dd",
    lineWidth: 5,
    shadowColor: "#090c2a",
    shadowOffset: [17, 28],
    shadowBlur: 36,
    children: [new Img({ src: nativeImage, width: 968, height: 605, y: -18 })],
  });
  const stand = new Rect({
    x: 294,
    y: 324,
    width: 178,
    height: 295,
    radius: 17,
    fill: "#1c2554",
  });
  const desktopPlate = bench(1.16, 48);
  shot(
    35.42,
    36.14,
    desktopPlate,
    stand,
    monitor,
    tape("SAME APP", 510, { x: -526, y: -145, rotation: -6 }, 72),
    tape("ON A DESK,", 515, { x: -507, y: -18, rotation: 4 }, 69, cobalt),
    tape(
      "Pixel Painter · native",
      370,
      { x: 548, y: 300, rotation: 2 },
      29,
      paper,
    ),
  );
  const deskWhip = () => -115 * clamp((clock() - 36.01) / 0.13) ** 3;
  monitor.x(() => 294 + deskWhip());
  stand.x(() => 294 + deskWhip());

  const tabs = new Rect({
    x: 108,
    y: 5,
    size: [1400, 821],
    radius: 29,
    fill: cobalt,
    stroke: "#99adff",
    lineWidth: 4,
    shadowColor: "#090c2abb",
    shadowOffset: [21, 28],
    shadowBlur: 35,
    children: [
      new Rect({
        x: -441,
        y: -401,
        size: [508, 132],
        radius: 27,
        fill: cobalt,
        stroke: "#99adff",
        lineWidth: 4,
      }),
      tape("IN A TAB,", 710, { x: -241, y: -291, rotation: -2 }, 105),
      new Line({
        points: [
          [-528, 111],
          [-356, 111],
          [-356, -2],
          [-183, -2],
          [-183, -126],
          [43, -126],
        ],
        stroke: "#0c1c74",
        lineWidth: 70,
        lineJoin: "miter",
        shadowColor: "#080e40",
        shadowBlur: 12,
        shadowOffset: [6, 9],
      }),
      new Line({
        points: [
          [-528, 111],
          [-356, 111],
          [-356, -2],
          [-183, -2],
          [-183, -126],
          [43, -126],
        ],
        stroke: "#8cafff",
        lineWidth: 49,
        lineJoin: "miter",
      }),
      tape(
        "Pixel Painter · browser placeholder",
        735,
        { x: -164, y: 251, rotation: -3 },
        34,
        paper,
      ),
    ],
  });
  const confirmations = [36.62, 37.08].map((at, index) =>
    tape(
      "YES!",
      310,
      {
        x: 423 + 170 * index,
        y: -128 + index * 192,
        rotation: index ? 14 : -12,
        opacity: () => Number(clock() >= at),
        scale: () => 1 + 0.31 * Math.exp(-Math.max(0, clock() - at) * 19),
      },
      85,
    ),
  );
  tabs.x(() => 108 + 154 * (1 - easeOutCubic(clamp((clock() - 36.14) / 0.22))));
  shot(36.14, 37.98, bench(1.22, -5), tabs, ...confirmations);
  hook(37.98, 39.92, 41.28, true);

  const parcel = new Rect({
    size: [1340, 695],
    x: 34,
    y: 99,
    radius: 36,
    fill: "#bd534d",
    stroke: "#f78f78",
    lineWidth: 7,
    shadowColor: "#090c2aee",
    shadowBlur: 35,
    shadowOffset: [24, 32],
    children: [
      new Rect({ width: 137, height: 695, x: -452, fill: "#8b393d" }),
      tape(
        "ONE SIGNED PACKAGE,",
        1035,
        { y: -196, x: 55, rotation: -3 },
        81,
        paper,
      ),
      word("THREE ADDRESSES", 78).position([24, 2]),
    ],
  });
  parcel.rotation(() => -10 + 2 * kick());
  ["DESKTOP", "BROWSER", "CONTAINER"].forEach((host, i) => {
    const at = [42.18, 42.42, 42.67][i];
    parcel.add(
      tape(
        host,
        310,
        {
          x: -329 + 333 * i,
          y: 169,
          rotation: -7 + i * 6,
          opacity: () => Number(clock() >= at),
          scale: () => 1 + 0.21 * Math.exp(-Math.max(0, clock() - at) * 16),
        },
        36,
        cobalt,
      ),
    );
  });
  shot(41.28, 43.14, bench(1.18, -47), parcel);

  const suit = mascot(275, 48, 2.48, -9);
  const tie = new Path({
    data: "M -47 -7 L -200 -100 L -185 100 L -47 19 L 47 19 L 185 100 L 200 -100 L 47 -7 Z",
    fill: ink,
    stroke: "#5167be",
    lineWidth: 5,
    shadowColor: "#101632",
    shadowBlur: 8,
    shadowOffset: [6, 9],
    x: 385,
    y: 65,
    rotation: -11,
  });
  tie.scale(
    () =>
      0.88 +
      0.12 * easeOutCubic(clamp((clock() - 44.06) / 0.2)) +
      0.036 * kick(),
  );
  tie.opacity(() => Number(clock() >= 44.06));
  shot(
    43.14,
    45.48,
    bench(1.12, -33),
    new Rect({
      x: 452,
      y: 414,
      size: [1040, 557],
      radius: 37,
      rotation: -8,
      fill: "#293ba7",
      stroke: "#798eef",
      lineWidth: 5,
      lineDash: [9, 9],
      shadowBlur: 28,
      shadowColor: "#070b2c95",
      shadowOffset: [5, 15],
    }),
    suit,
    tie,
    tape("POCKET-SIZED", 663, { x: -481, y: -29, rotation: -8 }, 69),
    tape(
      "AND FULLY DRESSED!",
      1110,
      { x: -223, y: 294, rotation: 3, opacity: () => Number(clock() >= 44.06) },
      71,
      paper,
    ),
  );

  // The tape stays stuck to the mat as the camera swings up into the browser.
  const finaleHook = shot(
    45.48,
    46.84,
    bench(1.04),
    tape(
      () => (clock() < 45.96 ? "NOT YOUR" : "NOT YOUR REGULAR!"),
      1400,
      { x: -74, y: 40, rotation: -6 },
      108,
    ),
    tape("O–S!", 325, { x: 539, y: 286, rotation: 7 }, 82, cobalt),
    mascot(-462, 332, 0.65, -9),
  );
  finaleHook.scale(() => 1 + 0.42 * clamp((clock() - 46.64) / 0.2) ** 3);

  const finalTab = new Rect({
    x: 306,
    y: 11,
    size: [1111, 855],
    radius: 30,
    fill: "#e2dcf0",
    stroke: "#afc2ff",
    lineWidth: 6,
    shadowColor: "#090c2a",
    shadowOffset: [16, 26],
    shadowBlur: 40,
    children: [
      new Rect({ y: -360, size: [983, 62], radius: 31, fill: paper }),
      word("platforms.xila.dev", 33, ink).position([0, -359]),
      new Img({ src: browserImage, width: 1024, height: 640, y: 45 }),
    ],
  });
  const mark = Logo({ width: 82 });
  const sticker = new Rect({
    x: -671,
    y: -295,
    radius: 8,
    size: [160, 145],
    fill: ink,
    children: [mark],
  });
  shot(
    46.84,
    end,
    bench(1.18, 8),
    finalTab,
    sticker,
    tape("TRY ME IN YOUR", 653, { x: -602, y: -105, rotation: -5 }, 58),
    tape("BROWSER TAB!", 635, { x: -580, y: 27, rotation: 3 }, 64, cobalt),
    tape(
      "YES!",
      310,
      { x: 760, y: 328, rotation: -12, opacity: () => Number(clock() >= 48.8) },
      83,
    ),
  );

  yield* tween(production.duration, (_, elapsed) => clock(start + elapsed));
});
