import {
  Circle,
  Gradient,
  Line,
  Node,
  Rect,
  makeScene2D,
} from "@motion-canvas/2d";
import { waitFor, type PossibleColor } from "@motion-canvas/core";
import { Logo, Text } from "../../components/brand";

type Point = [number, number];

const ink = "#100A22";
const violet = "#211641";
const cobalt = "#2626C8";
const cyan = "#60F1F5";
const amber = "#FFB849";
const butter = "#FFF1BF";
const pink = "#FF5D94";
const red = "#FA4B58";
const orange = "#FF6D36";

function block(
  x: number,
  y: number,
  width: number,
  height: number,
  fill: PossibleColor,
  radius = 0,
) {
  return new Rect({ x, y, width, height, fill, radius });
}

function dot(x: number, y: number, size: number, fill: PossibleColor) {
  return new Circle({ x, y, size, fill });
}

function face(points: Point[], fill: PossibleColor) {
  return new Line({ points, closed: true, fill });
}

function rail(points: Point[], stroke: PossibleColor, lineWidth: number) {
  return new Line({
    points,
    stroke,
    lineWidth,
    lineCap: "round",
    lineJoin: "round",
  });
}

function mono(text: string, x: number, y: number, fill: string, fontSize = 52) {
  return Text({
    text,
    x,
    y,
    fill,
    fontSize,
    fontWeight: 600,
    fontFamily: "Fira Code",
  });
}

function clubFloor(vanishingX: number, horizon: number, color: string) {
  return [
    block(960, (horizon + 1080) / 2, 1920, 1080 - horizon, violet),
    ...Array.from({ length: 13 }, (_, index) => {
      const x = -1300 + index * 400;
      return rail(
        [
          [vanishingX, horizon],
          [x, 1100],
        ],
        color,
        3,
      );
    }),
    ...[36, 79, 145, 242, 380, 530]
      .filter((distance) => horizon + distance < 1079)
      .map((distance) =>
        rail(
          [
            [0, horizon + distance],
            [1920, horizon + distance],
          ],
          color,
          3,
        ),
      ),
  ];
}

// The board is a scenic prop. Its outline and pads are drawn in one oblique plane.
function booth(x: number, y: number, scale: number) {
  const children: Node[] = [];
  const at = (u: number, v: number): Point => [
    u - v * 0.32,
    u * 0.12 + v * 0.54,
  ];
  const plate = (
    u: number,
    v: number,
    w: number,
    h: number,
    fill: string,
    depth = 0,
  ) =>
    face(
      [at(u, v), at(u + w, v), at(u + w, v + h), at(u, v + h)].map(
        ([px, py]): Point => [px, py + depth],
      ),
      fill,
    );

  children.push(
    plate(-40, 32, 680, 308, "#090717", 32),
    plate(0, 0, 620, 260, "#111041", 26),
    plate(0, 0, 620, 260, "#4374C2", 10),
    plate(0, 0, 620, 260, "#293B91"),
    plate(22, 16, 576, 227, "#374FB1"),
    plate(198, 77, 170, 126, "#10183D", 7),
    plate(198, 77, 170, 126, "#151D53"),
    plate(222, 91, 123, 5, "#506BCD"),
    plate(383, 105, 68, 73, "#242962"),
    plate(468, 151, 40, 32, "#161A52"),
    plate(488, 90, 62, 33, "#182252"),
    plate(-24, 87, 110, 92, "#1A2046", 13),
    plate(-24, 87, 110, 92, "#A5BDDB"),
    plate(-22, 144, 97, 33, "#7D91B8"),
    plate(-23, 150, 61, 23, "#24294C"),
    plate(577, 80, 20, 84, "#A3ABC8"),
  );
  for (const [v, flip] of [
    [34, 1],
    [216, -1],
  ]) {
    for (let index = 0; index < 14; index++) {
      const u = 100 + index * 34;
      children.push(
        plate(u, v, 18, 19, "#CCA761"),
        plate(u + 5, v + 5, 8, 9, "#26244E"),
      );
      if (index < 11) {
        children.push(
          rail(
            [
              at(u + 10, v + 9),
              at(u + 10, v + 30 * flip),
              at(u + 22, v + 48 * flip),
            ],
            "#5E75C6",
            1.5,
          ),
        );
      }
    }
  }
  const [ledX, ledY] = at(535, 194);
  children.push(
    new Circle({
      x: ledX,
      y: ledY,
      size: 120,
      scaleY: 0.6,
      fill: new Gradient({
        type: "radial",
        fromRadius: 2,
        toRadius: 60,
        stops: [
          { offset: 0, color: "#FFB849CC" },
          { offset: 0.4, color: "#FFB84955" },
          { offset: 1, color: "#FFB84900" },
        ],
      }),
    }),
    plate(519, 182, 32, 24, amber),
    plate(523, 185, 23, 15, butter),
  );
  return new Node({ x, y, scale, children });
}

function ledFrame() {
  return [
    block(960, 540, 1920, 1080, "#171451"),
    face(
      [
        [0, 45],
        [1010, 250],
        [1415, 552],
        [0, 570],
      ],
      cobalt,
    ),
    face(
      [
        [1920, 0],
        [1240, 250],
        [1445, 550],
        [1920, 565],
      ],
      "#211767",
    ),
    ...clubFloor(1230, 532, "#373077"),
    face(
      [
        [1400, 0],
        [1536, 0],
        [1735, 888],
        [632, 818],
      ],
      "#6250E847",
    ),
    new Circle({ x: 1110, y: 790, width: 1250, height: 250, fill: "#4C36A1" }),
    new Circle({ x: 1128, y: 792, width: 1070, height: 186, fill: "#654BB7" }),
    new Circle({ x: 1130, y: 808, width: 864, height: 119, fill: "#37286E" }),
    rail(
      [
        [0, 945],
        [264, 928],
        [432, 776],
        [666, 704],
        [845, 703],
      ],
      "#0D0922",
      38,
    ),
    rail(
      [
        [0, 938],
        [264, 920],
        [432, 769],
        [666, 698],
        [845, 697],
      ],
      "#5854B2",
      7,
    ),
    booth(874, 593, 1.12),
    face(
      [
        [143, 230],
        [166, 211],
        [782, 211],
        [782, 314],
        [761, 340],
        [143, 340],
      ],
      "#0D0A35",
    ),
    block(447, 271, 610, 105, "#26227F", 8),
    rail(
      [
        [143, 222],
        [751, 222],
      ],
      "#7A80F0",
      3,
    ),
    mono("/devices/gpio/d13", 447, 270, butter, 52),
    rail(
      [
        [756, 333],
        [805, 392],
        [1254, 392],
        [1401, 728],
        [1401, 751],
      ],
      amber,
      4,
    ),
    dot(1401, 751, 9, amber),
  ];
}

function digitsFrame() {
  const card = new Node({
    x: 535,
    y: 494,
    rotation: -13,
    children: [
      face(
        [
          [-301, -227],
          [298, -227],
          [298, 230],
          [-301, 230],
        ],
        "#160A26",
      ),
      face(
        [
          [-315, -244],
          [309, -244],
          [309, 191],
          [272, 215],
          [-315, 215],
        ],
        "#F5DBAC",
      ),
      face(
        [
          [309, 191],
          [272, 215],
          [272, 184],
        ],
        "#C38E75",
      ),
      ...Array.from({ length: 7 }, (_, i) =>
        rail(
          [
            [-281, -178 + 53 * i],
            [271, -178 + 53 * i],
          ],
          "#DCB39B",
          2,
        ),
      ),
      rail(
        [
          [-205, -243],
          [-205, 214],
        ],
        "#D99087",
        3,
      ),
      new Line({
        points: [
          [-110, -92],
          [-38, -117],
          [58, -119],
          [140, -137],
          [87, -55],
          [47, 21],
          [22, 107],
        ],
        stroke: "#281941",
        lineWidth: 30,
        lineCap: "round",
        lineJoin: "round",
      }),
      rail(
        [
          [-27, 11],
          [26, 2],
          [104, -11],
        ],
        "#281941",
        20,
      ),
    ],
  });

  return [
    block(960, 540, 1920, 1080, "#2F113B"),
    face(
      [
        [0, 690],
        [1920, 415],
        [1920, 1080],
        [0, 1080],
      ],
      "#6D224D",
    ),
    face(
      [
        [0, 774],
        [1920, 448],
        [1920, 582],
        [0, 953],
      ],
      "#9B2C58",
    ),
    face(
      [
        [0, 901],
        [1920, 582],
        [1920, 633],
        [0, 1042],
      ],
      "#52204B",
    ),
    new Circle({ x: 1053, y: 839, width: 1490, height: 191, fill: "#220F2B" }),
    face(
      [
        [971, 279],
        [1679, 279],
        [1782, 385],
        [1782, 824],
        [1063, 824],
        [974, 740],
      ],
      "#170D29",
    ),
    face(
      [
        [971, 279],
        [1679, 279],
        [1782, 385],
        [1063, 385],
      ],
      "#C65B83",
    ),
    face(
      [
        [1063, 385],
        [1782, 385],
        [1782, 793],
        [1063, 793],
      ],
      "#582B65",
    ),
    face(
      [
        [971, 279],
        [1063, 385],
        [1063, 793],
        [971, 704],
      ],
      "#37204E",
    ),
    block(1422, 548, 658, 200, "#29153F", 12),
    block(1422, 551, 617, 151, "#130B23", 8),
    block(1422, 470, 617, 8, pink, 4),
    block(1422, 612, 617, 25, "#381845", 4),
    block(1422, 603, 617, 5, "#A04C7D", 3),
    block(1422, 666, 619, 65, "#7E4374", 4),
    mono("/devices/nn/digits", 1422, 666, "#FFF0DE", 50),
    block(1422, 757, 618, 8, "#A05383", 4),
    face(
      [
        [791, 538],
        [1114, 501],
        [1114, 590],
        [815, 609],
      ],
      "#EC688345",
    ),
    card,
  ];
}

function lightbox(
  text: string,
  x: number,
  y: number,
  width: number,
  accent: string,
  size: number,
) {
  return new Node({
    x,
    y,
    children: [
      block(16, 24, width, 200, "#080518", 4),
      block(0, 0, width, 194, "#765CA1", 4),
      block(0, 2, width - 13, 181, "#201236"),
      block(0, 2, width - 27, 162, "#160D29"),
      block(0, -75, width - 24, 4, "#885C92"),
      face(
        [
          [-width / 2 + 10, -83],
          [width / 2 - 10, -83],
          [width / 2 - 42, -58],
          [-width / 2 + 42, -58],
        ],
        "#583970",
      ),
      dot(-width / 2 + 23, 65, 9, "#946FB0"),
      dot(width / 2 - 23, 65, 9, "#946FB0"),
      Text({
        text,
        y: 9,
        fill: "#542557",
        fontSize: size,
        fontWeight: 900,
        scaleX: 0.8,
      }),
      Text({
        text,
        y: 2,
        fill: accent,
        fontSize: size,
        fontWeight: 900,
        scaleX: 0.8,
      }),
      block(0, 84, width - 26, 3, accent),
    ],
  });
}

function hookFrame() {
  return [
    block(960, 540, 1920, 1080, "#151033"),
    face(
      [
        [0, 0],
        [205, 115],
        [205, 604],
        [0, 778],
      ],
      "#35276A",
    ),
    face(
      [
        [1920, 0],
        [1715, 115],
        [1715, 604],
        [1920, 778],
      ],
      "#37276B",
    ),
    block(960, 57, 1920, 106, "#0E0922"),
    block(960, 100, 1720, 22, "#794C92"),
    block(960, 111, 1720, 14, "#22123B"),
    ...[392, 765, 1155, 1528].flatMap((x) => [
      block(x, 137, 14, 69, "#654883"),
      block(x, 161, 62, 26, "#160E2B", 4),
      block(x, 164, 27, 7, cyan, 3),
    ]),
    block(960, 385, 1510, 540, "#241944"),
    ...clubFloor(960, 649, "#48367B"),
    face(
      [
        [306, 638],
        [737, 638],
        [620, 1080],
        [0, 1080],
      ],
      "#29B0D03B",
    ),
    face(
      [
        [794, 638],
        [1047, 638],
        [1102, 1080],
        [759, 1080],
      ],
      "#FF5D9433",
    ),
    face(
      [
        [1103, 638],
        [1600, 638],
        [1920, 1080],
        [1200, 1080],
      ],
      "#FFB8493C",
    ),
    rail(
      [
        [55, 1080],
        [322, 661],
        [1602, 661],
        [1865, 1080],
      ],
      "#8264C5",
      6,
    ),
    lightbox("EVERYTHING", 960, 271, 1318, cyan, 171),
    lightbox("IS", 521, 500, 440, cyan, 159),
    lightbox("A", 891, 500, 252, pink, 159),
    lightbox("FILE", 1343, 500, 552, amber, 159),
    new Circle({ x: 956, y: 851, width: 403, height: 122, fill: "#29183D" }),
    new Circle({ x: 954, y: 840, width: 367, height: 104, fill: "#66404A" }),
    new Circle({ x: 953, y: 836, width: 281, height: 76, fill: "#936343" }),
    booth(871, 796, 0.28),
    rail(
      [
        [0, 1038],
        [538, 1014],
        [849, 872],
        [923, 847],
      ],
      "#100A22",
      14,
    ),
  ];
}

function route(points: Point[], color: string) {
  return [
    rail(points, "#0A081C", 44),
    rail(points, "#644782", 23),
    rail(points, color, 8),
  ];
}

function trapFrame() {
  return [
    block(960, 540, 1920, 1080, "#26164A"),
    ...Array.from({ length: 15 }, (_, i) =>
      rail(
        [
          [0, i * 80],
          [1920, i * 80],
        ],
        "#332052",
        2,
      ),
    ),
    ...Array.from({ length: 25 }, (_, i) =>
      rail(
        [
          [i * 80, 0],
          [i * 80, 1080],
        ],
        "#332052",
        2,
      ),
    ),
    ...route(
      [
        [960, 916],
        [960, 518],
      ],
      butter,
    ),
    ...route(
      [
        [960, 518],
        [420, 518],
        [420, 303],
      ],
      amber,
    ),
    ...route(
      [
        [960, 518],
        [960, 303],
      ],
      cyan,
    ),
    ...route(
      [
        [960, 518],
        [1500, 518],
        [1500, 303],
      ],
      pink,
    ),
    ...route(
      [
        [960, 730],
        [1509, 730],
        [1509, 778],
      ],
      "#955271",
    ),
    ...route(
      [
        [960, 730],
        [680, 730],
        [680, 811],
        [385, 811],
      ],
      cyan,
    ),
    dot(960, 518, 116, "#21173B"),
    dot(960, 518, 89, amber),
    dot(960, 518, 48, butter),
    dot(960, 518, 17, "#251236"),
    block(582, 518, 76, 10, amber, 4),
    dot(532, 518, 32, butter),
    block(960, 445, 10, 51, cyan, 4),
    block(1294, 518, 72, 10, pink, 4),
    dot(960, 395, 32, "#BCFAFC"),
    dot(1343, 518, 32, "#FFC2D6"),
    dot(680, 774, 32, "#BCFAFC"),
    block(385, 811, 181, 101, "#12102B", 14),
    block(385, 811, 148, 66, "#2E5899", 5),
    dot(431, 812, 23, cyan),
    block(420, 253, 150, 145, "#110B24", 14),
    face(
      [
        [386, 210],
        [438, 210],
        [456, 229],
        [456, 292],
        [386, 292],
      ],
      amber,
    ),
    face(
      [
        [438, 210],
        [456, 229],
        [438, 229],
      ],
      "#AD6535",
    ),
    rail(
      [
        [400, 249],
        [443, 249],
      ],
      "#714F47",
      4,
    ),
    rail(
      [
        [400, 266],
        [435, 266],
      ],
      "#714F47",
      4,
    ),
    block(960, 253, 150, 145, "#110B24", 14),
    block(960, 253, 77, 77, cyan, 9),
    block(960, 253, 46, 46, "#337AAD", 4),
    dot(960, 253, 25, "#A9FDFF"),
    block(1500, 253, 150, 145, "#110B24", 14),
    rail(
      [
        [1474, 224],
        [1474, 276],
        [1531, 276],
      ],
      pink,
      31,
    ),
    rail(
      [
        [1474, 225],
        [1474, 276],
        [1531, 276],
      ],
      "#B34C83",
      12,
    ),
    mono("Files", 420, 134, butter),
    mono("Devices", 960, 134, cyan),
    mono("Pipes", 1500, 134, "#FFACCC"),
    new Circle({ x: 960, y: 923, width: 235, height: 128, fill: "#493262" }),
    booth(903, 895, 0.2),
    block(1509, 757, 252, 80, "#100A22", 8),
    block(1509, 753, 234, 62, "#781D49", 6),
    mono("MY APP", 1509, 750, "#FFACCC", 50),
    block(1521, 887, 492, 142, "#0E091F", 10),
    block(1509, 871, 492, 142, "#7C2C50", 10),
    block(1509, 871, 475, 124, "#291433", 4),
    rail(
      [
        [1278, 815],
        [1740, 815],
      ],
      red,
      4,
    ),
    mono("unreachable", 1509, 869, "#FF8297", 54),
  ];
}

function endFrame() {
  const lockup = Logo({ light: true, lockup: true, width: 635 });
  lockup.position([960, 428]);

  return [
    block(960, 540, 1920, 1080, orange),
    face(
      [
        [0, 0],
        [180, 0],
        [0, 383],
      ],
      "#F45732",
    ),
    face(
      [
        [0, 725],
        [325, 0],
        [417, 0],
        [0, 918],
      ],
      "#FA6033",
    ),
    face(
      [
        [1920, 366],
        [1920, 578],
        [1695, 1080],
        [1597, 1080],
      ],
      "#F65D31",
    ),
    face(
      [
        [1920, 830],
        [1920, 1080],
        [1804, 1080],
      ],
      "#E84F34",
    ),
    lockup,
    Text({
      text: "Runs in your browser. Right now.",
      x: 960,
      y: 667,
      fontSize: 59,
      fontWeight: 750,
      fill: ink,
    }),
    mono("xila.dev", 960, 800, ink, 52),
  ];
}

export default makeScene2D(function* (view) {
  for (const frame of [ledFrame, digitsFrame, hookFrame, trapFrame, endFrame]) {
    const set = new Node({ x: -960, y: -540, children: frame() });
    view.add(set);
    yield* waitFor(1);
    set.remove();
  }
});
