// Renderiza o Pengaró com o esqueleto 3D do pixelfx (rig.js) e pinta com as cores dele.
// Uso: node renderizar_pengaro.mjs ginga N SAIDA.rgba   (N quadros do ciclo; saída: cabeçalho w,h,n + RGBA cru)
import { writeFileSync } from "node:fs";
import { posed } from "./rig.js"; // o rig já sai na escala de 112 px (ESCALA em rig.js)
import { hex } from "./color.js";
import { DUMMY_PAL } from "./actor.js";

const H = (k) => hex(DUMMY_PAL[k]) >>> 0;
const INK = H("k"), SEAM = H("J");
const rgb = (s) => [parseInt(s.slice(1, 3), 16), parseInt(s.slice(3, 5), 16), parseInt(s.slice(5, 7), 16)];
// rampas de 6 tons, do mais claro ao mais escuro
const PELE = ["#eaa878", "#d68d5c", "#bd7249", "#9a5836", "#774127", "#552c1d"].map(rgb);
const CALCA = ["#ffffff", "#f1eff4", "#d9d5e2", "#b6b0c6", "#8f89a2", "#6c6680"].map(rgb);
const FAIXA = ["#3fb8a4", "#2fa392", "#238276", "#1a6159", "#114540", "#0b302c"].map(rgb);
const CABELO = ["#5a4146", "#443138", "#34252c", "#241a22", "#1a1219", "#120c12"].map(rgb);
const CANELEIRA = ["#5a9468", "#487a54", "#355c41", "#264530", "#1b3222", "#12221a"].map(rgb);
const VERDE = ["#2fa35a", "#278a4b", "#1d6c3a", "#17552d", "#103c20", "#0b2a16"].map(rgb);
const AMARELO = ["#ffe066", "#f2c93a", "#d3a526", "#a8801c", "#7d5e14", "#58410d"].map(rgb);
const TRACO = rgb("#281925"), OLHO = rgb("#1a1018"), BOCA = rgb("#7a3a2c");
const K = 3;
const RAMPA = { 1: CALCA, 2: FAIXA, 3: PELE, 4: PELE, 5: CABELO, 6: PELE, 15: CALCA, 16: CALCA, 17: CALCA, 18: PELE, 19: CALCA, 20: CALCA, 21: CANELEIRA, 22: PELE };
const idxTom = (t) => (t > 0.86 ? 0 : t > 0.66 ? 1 : t > 0.46 ? 2 : t > 0.26 ? 3 : t > 0.08 ? 4 : 5);
const escurece = (rampa, i, n = 1) => rampa[Math.min(5, i + n)];

export function pinta(r) {
  const out = [];
  for (let i = 0; i < r.n; i++) {
    const c = r.color[i] >>> 0, p = r.part[i], lx = r.lx[i], ly = r.ly[i], lz = r.lz[i];
    if (r.ink[i] || c === INK) { out.push([r.xs[i], r.ys[i], TRACO]); continue; }
    const braco = p >= 7 && p <= 14;
    let rampa = RAMPA[p] ?? (braco ? PELE : PELE);
    let t = idxTom(r.tone[i]);
    if (c === SEAM) t = Math.min(5, t + 1);
    let col;
    const perna = (p >= 15 && p <= 17) || (p >= 19 && p <= 21);
    if (perna && p !== 21) {
      // listra verde e amarela na lateral da calça, de cima até o joelho
      const d = ly + 0.1 * K;
      if (d > -0.55 * K && d < 0.25 * K) rampa = VERDE;
      else if (d >= 0.25 * K && d < 0.8 * K) rampa = AMARELO;
    }
    if (p === 2) {
      // faixa azul-petróleo com o cordão amarelo embaixo
      if (ly < -0.2 * K) rampa = AMARELO;
    }
    if (p === 3 && lx > 8) {
      // peitoral e abdômen: linhas escuras na frente do peito
      const linhaCentral = Math.abs(lz) < 0.9 && ly < 4 && ly > -9;
      const abs = ly < 3 && ly > -9 && Math.abs(lz) < 5.5 && [-1, -4, -7].some((y) => Math.abs(ly - y) < 0.8);
      const peito = ly > 3 && ly < 7 && Math.abs(lz) < 7 && Math.abs(ly - (5.2 - 0.25 * Math.abs(lz))) < 0.8;
      if (linhaCentral || abs || peito) t = Math.min(5, t + 1);
    }
    if (p === 6 && lx > 7.2) {
      // rosto de perfil: olho, sobrancelha e boca
      const olho = Math.hypot(ly - 1.8, Math.abs(lz) - 6.0) < 1.7;
      const sobr = Math.abs(ly - 4.4) < 0.8 && Math.abs(lz) > 4.2;
      const boca = Math.abs(ly + 4.8) < 0.7 && Math.abs(lz) < 5.5 && lx > 8.4;
      if (olho || sobr) { out.push([r.xs[i], r.ys[i], OLHO]); continue; }
      if (boca) { out.push([r.xs[i], r.ys[i], BOCA]); continue; }
    }
    col = rampa[t];
    out.push([r.xs[i], r.ys[i], col]);
  }
  return out;
}

const LARG = 130, ALT = 128, PX = 65, PY = 120; // quadro em pixels do pixelfx, pés em (PX, PY)
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
    // mão de trás recolhida na frente do peito, a da frente alta; as duas se revezam no balanço
    fx: 5 + 2 * Math.cos(a + 0.6), fy: -17 + 3 * Math.sin(a + 0.6), bx: 13 - 2 * c, by: -26 - 2.5 * s,
  };
}

if (process.argv[2]) {
  const [, , anim, n, destino] = process.argv, N = +n, lista = [];
  for (let i = 0; i < N; i++) lista.push(quadro({ ginga }[anim](2 * Math.PI * i / N)));
  const cab = Buffer.alloc(12);
  cab.writeUInt32LE(LARG, 0); cab.writeUInt32LE(ALT, 4); cab.writeUInt32LE(N, 8);
  writeFileSync(destino, Buffer.concat([cab, ...lista]));
}
