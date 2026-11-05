// Calcula, com o esqueleto do pixelfx, onde ficam mãos, pés, quadril e peito em cada quadro da ginga.
// Saída: JSON com as juntas em pixels do sprite (y para baixo, pés em y = 0). Quem anima é rig_pengaro.py.
// Uso: node trajetoria.mjs ginga N SAIDA.json
import { writeFileSync } from "node:fs";
import { skeleton, ESCALA } from "./rig.js";
import { ginga } from "./renderizar_pengaro.mjs";

const [, , anim, n, destino] = process.argv, N = +n, quadros = [];
for (let i = 0; i < N; i++) {
  const j = skeleton({ ginga }[anim](2 * Math.PI * i / N)).joints, q = {};
  for (const k of ["pelvis", "chest", "head", "handN", "handF", "ankleN", "ankleF", "elbowN", "elbowF", "kneeN", "kneeF"]) q[k] = [j[k][0], j[k][1]];
  quadros.push(q);
}
writeFileSync(destino, JSON.stringify(quadros));
