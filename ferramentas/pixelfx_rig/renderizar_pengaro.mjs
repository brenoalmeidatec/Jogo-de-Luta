// Renderiza o Pengaró com o esqueleto 3D do pixelfx (rig.js) e pinta com as cores dele.
// Uso: node renderizar_pengaro.mjs ginga N SAIDA.rgba   (N quadros do ciclo; saída: cabeçalho w,h,n + RGBA cru)
import { writeFileSync } from "node:fs";
import { posed } from "./rig.js";
import { hex } from "./color.js";
import { DUMMY_PAL } from "./actor.js";

const H = (k) => hex(DUMMY_PAL[k]) >>> 0;
const TOM = new Map([["A", 0], ["B", 1], ["C", 2], ["D", 3], ["E", 0], ["F", 1], ["G", 3]].map(([k, t]) => [H(k), t]));
const INK = H("k"), SEAM = H("J"), MARK = H("m");
const rgb = (s) => [parseInt(s.slice(1, 3), 16), parseInt(s.slice(3, 5), 16), parseInt(s.slice(5, 7), 16)];
const PELE = ["#e0a070", "#c47e50", "#9c5a38", "#6e3b26"].map(rgb);
const CALCA = ["#ffffff", "#ebe8ee", "#c3bfcf", "#8f89a2"].map(rgb);
const FAIXA = ["#2fa392", "#238276", "#1a6159", "#114540"].map(rgb);
const CABELO = ["#4a3438", "#34252c", "#241a22", "#241a22"].map(rgb);
const CANELEIRA = ["#487a54", "#355c41", "#264530", "#1b3222"].map(rgb);
const TRACO = rgb("#281925"), COSTURA = rgb("#5c4b66");
// 1 pelve 2 cintura 3 peito 4 pescoço 5 cabeça 6 rosto 7-10 braço perto 11-14 braço longe
// 15-18 perna perto (coxa, joelho, canela, pé) 19-22 perna longe
const RAMPA = { 1: CALCA, 2: FAIXA, 3: PELE, 4: PELE, 5: CABELO, 6: PELE, 15: CALCA, 16: CALCA, 17: CALCA, 18: PELE, 19: CALCA, 20: CALCA, 21: CANELEIRA, 22: PELE };
const braco = (p) => (p >= 7 && p <= 14 ? PELE : null);

export function pinta(r) {
  const out = [];
  for (let i = 0; i < r.n; i++) {
    const c = r.color[i] >>> 0, p = r.part[i];
    let col;
    if (r.ink[i] || c === INK) col = TRACO;
    else if (c === SEAM) col = COSTURA;
    else if (c === MARK) col = PELE[2];
    else col = (RAMPA[p] ?? braco(p) ?? PELE)[TOM.get(c) ?? 1];
    out.push([r.xs[i], r.ys[i], col]);
  }
  return out;
}

const EIXO = 3, LARG = 40, ALT = 44, PX = 20, PY = 40; // quadro em pixels do pixelfx, pés em (PX, PY)
function quadro(pose) {
  const buf = new Uint8Array(LARG * ALT * 4);
  for (const [x, y, c] of pinta(posed(pose))) {
    const X = PX + x, Y = PY + y;
    if (X < 0 || Y < 0 || X >= LARG || Y >= ALT) continue;
    buf.set([c[0], c[1], c[2], 255], (Y * LARG + X) * 4);
  }
  return buf;
}

export function ginga(a) {
  const c = Math.cos(a), s = Math.sin(a);
  return {
    crouch: 2.5 + 1.2 * Math.cos(2 * a), lean: 1.5 + 1.2 * s,
    ffx: 6 + 3 * c, ffy: -4 - 2.5 * Math.max(0, s), fbx: -6 - 3 * c, fby: -4 - 2.5 * Math.max(0, -s),
    fx: 11 + 2 * Math.cos(a + 0.6), fy: -21 + 2.5 * Math.sin(a + 0.6), bx: 9 - 2 * c, by: -21 - 2.5 * s,
  };
}

if (process.argv[2]) {
  const [, , anim, n, destino] = process.argv, N = +n, lista = [];
  for (let i = 0; i < N; i++) lista.push(quadro({ ginga }[anim](2 * Math.PI * i / N)));
  const cab = Buffer.alloc(12);
  cab.writeUInt32LE(LARG, 0); cab.writeUInt32LE(ALT, 4); cab.writeUInt32LE(N, 8);
  writeFileSync(destino, Buffer.concat([cab, ...lista]));
}
