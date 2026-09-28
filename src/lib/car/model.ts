import * as THREE from "three";
import {
  createMaterial,
  FINISH_ID,
  type PixelMaterial,
} from "@/lib/pixel/materials";
import {
  BODY_VERTEX_COUNT,
  buildBodyIndex,
  buildBodyPositions,
  RING,
  ringToHalf,
  STATIONS,
  UNDERBODY_END,
} from "./body";
import { type BodyMaterial, createBodyMaterial } from "./body-material";
import { sample } from "./curve";
import { applyDecals, type FlatDecal, mixOklab, pairDecals } from "./decals";
import {
  buildLampLocal,
  createLampIndex,
  createLampMaterial,
  createLampParts,
  graphicId,
  LAMP_VERTS,
  type LampMaterial,
} from "./lamps";
import type { CarDef, WheelDef } from "./types";
import {
  applyRim,
  createFaceGeometry,
  createRimMaterial,
  createTyreGeometry,
  RIM_DESIGNS,
  type RimMaterial,
  type RimParams,
} from "./wheels";

type StopData = {
  def: CarDef;
  positions: Float32Array;
  normals: Float32Array;
  lampPos: Float32Array;
  lampNormal: Float32Array;
  lampUv: Float32Array;
  lampMatrix: THREE.Matrix4;
};

type WheelMeshes = {
  pivot: THREE.Group;
  tyre: THREE.Mesh;
  faces: [THREE.Mesh, THREE.Mesh];
  rims: [RimMaterial, RimMaterial];
};

const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

function computeNormals(
  positions: Float32Array,
  index: Uint32Array | number[],
) {
  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  geo.setIndex(
    Array.isArray(index) ? index : new THREE.BufferAttribute(index, 1),
  );
  geo.computeVertexNormals();
  const normals = (geo.getAttribute("normal") as THREE.BufferAttribute)
    .array as Float32Array;
  geo.dispose();
  return normals;
}

function lerpRim(a: RimParams, b: RimParams, t: number): RimParams {
  return {
    spokes: t < 0.5 ? a.spokes : b.spokes,
    widthHub: lerp(a.widthHub, b.widthHub, t),
    widthRim: lerp(a.widthRim, b.widthRim, t),
    twist: lerp(a.twist, b.twist, t),
    split: lerp(a.split, b.split, t),
    hub: lerp(a.hub, b.hub, t),
    lip: lerp(a.lip, b.lip, t),
    disc: t < 0.5 ? a.disc : b.disc,
    holeSize: lerp(a.holeSize, b.holeSize, t),
    holeRing: lerp(a.holeRing, b.holeRing, t),
    holeAspect: lerp(a.holeAspect, b.holeAspect, t),
  };
}

/**
 * The morphing 911. Every stop is precomputed into vertex arrays that share
 * one topology; showing a fractional timeline position is just a lerp.
 */
export class CarModel {
  readonly group = new THREE.Group();
  private stops: StopData[] = [];
  private pairs: [FlatDecal[], FlatDecal[]][] = [];
  private body: THREE.Mesh;
  private bodyGeo = new THREE.BufferGeometry();
  private bodyMaterial: BodyMaterial;
  private lampGeo = new THREE.BufferGeometry();
  private lamps: THREE.Mesh[] = [];
  private lampMaterial: LampMaterial;
  private wheels: WheelMeshes[] = [];
  private mirrorMaterial: PixelMaterial;
  private mirrors: THREE.Mesh[] = [];
  private wing: THREE.Mesh;
  private wingGeo = new THREE.BufferGeometry();
  private wingMaterial: PixelMaterial;
  private lip: THREE.Mesh;
  private lipMaterial: PixelMaterial;
  private exhausts: THREE.Mesh[] = [];
  private paint = new THREE.Color();

  constructor(defs: CarDef[]) {
    const index = buildBodyIndex();
    const under = new Float32Array(BODY_VERTEX_COUNT);
    for (let i = 0; i < STATIONS; i++) {
      for (let j = 0; j < RING; j++) {
        const [h] = ringToHalf(j);
        under[i * RING + j] = h < UNDERBODY_END ? 1 : 0;
      }
    }

    const lampIndex = createLampIndex();
    for (const def of defs) {
      const positions = new Float32Array(BODY_VERTEX_COUNT * 3);
      buildBodyPositions(def.body, def, positions);
      const normals = computeNormals(positions, index);
      const lamp = buildLampLocal(def.headlight);
      const lampNormal = computeNormals(lamp.pos, lampIndex);
      this.stops.push({
        def,
        positions,
        normals,
        lampPos: lamp.pos,
        lampNormal,
        lampUv: lamp.uv,
        lampMatrix: this.placeLamp(def, positions, index),
      });
    }
    for (let i = 0; i < defs.length - 1; i++)
      this.pairs.push(pairDecals(defs[i], defs[i + 1]));
    if (defs.length === 1) this.pairs.push(pairDecals(defs[0], defs[0]));

    this.bodyGeo.setAttribute(
      "position",
      new THREE.BufferAttribute(new Float32Array(BODY_VERTEX_COUNT * 3), 3),
    );
    this.bodyGeo.setAttribute(
      "normal",
      new THREE.BufferAttribute(new Float32Array(BODY_VERTEX_COUNT * 3), 3),
    );
    this.bodyGeo.setAttribute("aUnder", new THREE.BufferAttribute(under, 1));
    this.bodyGeo.setIndex(new THREE.BufferAttribute(index, 1));
    this.bodyMaterial = createBodyMaterial();
    this.body = new THREE.Mesh(this.bodyGeo, this.bodyMaterial);
    this.body.frustumCulled = false;
    this.group.add(this.body);

    // Headlights (mirrored pair).
    this.lampGeo.setAttribute(
      "position",
      new THREE.BufferAttribute(new Float32Array(LAMP_VERTS * 3), 3),
    );
    this.lampGeo.setAttribute(
      "normal",
      new THREE.BufferAttribute(new Float32Array(LAMP_VERTS * 3), 3),
    );
    this.lampGeo.setAttribute(
      "aLens",
      new THREE.BufferAttribute(new Float32Array(LAMP_VERTS * 2), 2),
    );
    this.lampGeo.setAttribute(
      "aPart",
      new THREE.BufferAttribute(createLampParts(), 1),
    );
    this.lampGeo.setIndex(lampIndex);
    this.lampMaterial = createLampMaterial();
    for (const side of [1, -1]) {
      const lamp = new THREE.Mesh(this.lampGeo, this.lampMaterial);
      lamp.matrixAutoUpdate = false;
      lamp.frustumCulled = false;
      lamp.userData.side = side;
      this.lamps.push(lamp);
      this.group.add(lamp);
    }

    // Wheels.
    const tyreGeo = createTyreGeometry(0.66);
    const faceGeo = createFaceGeometry();
    const tyreMat = createMaterial("rubber", "#262626", {
      side: THREE.DoubleSide,
    });
    for (let w = 0; w < 4; w++) {
      const pivot = new THREE.Group();
      const tyre = new THREE.Mesh(tyreGeo, tyreMat);
      const rims: [RimMaterial, RimMaterial] = [
        createRimMaterial(),
        createRimMaterial(),
      ];
      const faces: [THREE.Mesh, THREE.Mesh] = [
        new THREE.Mesh(faceGeo, rims[0]),
        new THREE.Mesh(faceGeo, rims[1]),
      ];
      pivot.add(tyre, faces[0], faces[1]);
      this.wheels.push({ pivot, tyre, faces, rims });
      this.group.add(pivot);
    }

    // Mirrors: an ellipsoid head on a short stalk, sized per generation.
    this.mirrorMaterial = createMaterial("paint", "#cccccc");
    const mirrorGeo = new THREE.SphereGeometry(0.5, 16, 10);
    for (let m = 0; m < 2; m++) {
      const mirror = new THREE.Mesh(mirrorGeo, this.mirrorMaterial);
      this.mirrors.push(mirror);
      this.group.add(mirror);
    }

    // Rear wing (whale tail / tea tray): an extruded side profile with an
    // upswept trailing edge plus a rubber lip, dissolved in and out.
    this.wingMaterial = createMaterial("paint", "#cccccc", {
      side: THREE.DoubleSide,
    });
    this.wingGeo.setAttribute(
      "position",
      new THREE.BufferAttribute(new Float32Array(8 * 3), 3),
    );
    this.wingGeo.setIndex([
      0, 1, 2, 0, 2, 3, 4, 6, 5, 4, 7, 6, 0, 4, 5, 0, 5, 1, 1, 5, 6, 1, 6, 2, 2,
      6, 7, 2, 7, 3, 3, 7, 4, 3, 4, 0,
    ]);
    this.wing = new THREE.Mesh(this.wingGeo, this.wingMaterial);
    this.wing.frustumCulled = false;
    this.lipMaterial = createMaterial("rubber", "#151515");
    this.lip = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), this.lipMaterial);
    this.group.add(this.wing, this.lip);

    const exhaustGeo = new THREE.CylinderGeometry(1, 1, 1, 12, 1, true);
    exhaustGeo.rotateZ(Math.PI / 2);
    const exhaustMat = createMaterial("chrome", "#aaaaaa", {
      side: THREE.DoubleSide,
    });
    for (let e = 0; e < 2; e++) {
      const ex = new THREE.Mesh(exhaustGeo, exhaustMat);
      this.exhausts.push(ex);
      this.group.add(ex);
    }
  }

  /** Find where the lamp axis meets the fender so the lens sits on the body. */
  private placeLamp(def: CarDef, positions: Float32Array, index: Uint32Array) {
    const centre = (def.frontAxle + def.rearAxle) / 2;
    const [x, y, z] = def.headlight.centre;
    const yaw = THREE.MathUtils.degToRad(def.headlight.yaw);
    const pitch = THREE.MathUtils.degToRad(def.headlight.pitch);
    // Lamp axis in object space: forward (+X) turned outward by yaw, tilted back by pitch.
    const axis = new THREE.Vector3(
      Math.cos(yaw) * Math.cos(pitch),
      Math.sin(pitch),
      Math.sin(yaw) * Math.cos(pitch),
    ).normalize();
    const target = new THREE.Vector3(centre - x, y, z);

    const geo = new THREE.BufferGeometry();
    geo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    geo.setIndex(new THREE.BufferAttribute(index, 1));
    const mesh = new THREE.Mesh(
      geo,
      new THREE.MeshBasicMaterial({ side: THREE.DoubleSide }),
    );
    const w = axis;
    const u = new THREE.Vector3(0, 1, 0).cross(w).normalize();
    const v = w.clone().cross(u).normalize();

    // Seat the lens on the outermost body hit under its centre and rim, so a
    // flat lens on a curved wing never sinks into the paint at its edges.
    let radius = 0;
    for (const [pu, pv] of def.headlight.outline) {
      radius = Math.max(radius, Math.hypot(pu, pv));
    }
    radius += def.headlight.ring;
    const ray = new THREE.Raycaster();
    let depth = Number.NEGATIVE_INFINITY;
    const probes: [number, number][] = [[0, 0]];
    for (let k = 0; k < 8; k++) {
      const ang = (k / 8) * Math.PI * 2;
      probes.push([Math.cos(ang) * radius, Math.sin(ang) * radius]);
    }
    for (const [pu, pv] of probes) {
      const start = target
        .clone()
        .addScaledVector(u, pu)
        .addScaledVector(v, pv)
        .addScaledVector(axis, 0.5);
      ray.set(start, axis.clone().negate());
      ray.far = 1.2;
      const hit = ray.intersectObject(mesh)[0];
      if (hit) depth = Math.max(depth, 0.5 - hit.distance);
    }
    geo.dispose();
    const origin = Number.isFinite(depth)
      ? target.clone().addScaledVector(axis, depth + 0.003)
      : target;
    return new THREE.Matrix4().makeBasis(u, v, w).setPosition(origin);
  }

  get count() {
    return this.stops.length;
  }

  /**
   * Show the car at a fractional timeline position with the given paint
   * colours for the two neighbouring stops.
   */
  update(position: number, paintA: THREE.Color, paintB: THREE.Color) {
    const max = this.stops.length - 1;
    const p = Math.min(max, Math.max(0, position));
    const i = Math.min(max - 1, Math.floor(p));
    const t = max === 0 ? 0 : p - i;
    const a = this.stops[max === 0 ? 0 : i];
    const b = this.stops[max === 0 ? 0 : i + 1];

    mixOklab(paintA, paintB, t, this.paint);

    // Body.
    const pos = this.bodyGeo.getAttribute("position") as THREE.BufferAttribute;
    const nrm = this.bodyGeo.getAttribute("normal") as THREE.BufferAttribute;
    const pa = pos.array as Float32Array;
    const na = nrm.array as Float32Array;
    for (let k = 0; k < pa.length; k++) {
      pa[k] = a.positions[k] + (b.positions[k] - a.positions[k]) * t;
      na[k] = a.normals[k] + (b.normals[k] - a.normals[k]) * t;
    }
    pos.needsUpdate = true;
    nrm.needsUpdate = true;
    this.bodyMaterial.uniforms.uPaint.value.copy(this.paint);
    const [da, db] =
      this.pairs[Math.min(Math.max(0, i), this.pairs.length - 1)];
    applyDecals(this.bodyMaterial, da, db, t, this.paint);

    this.updateLamps(a, b, t);
    this.updateWheels(a.def, b.def, t);
    this.updateMirrors(a.def, b.def, t);
    this.updateWing(a.def, b.def, t);
    this.updateExhausts(a.def, b.def, t);
  }

  private updateLamps(a: StopData, b: StopData, t: number) {
    const pos = this.lampGeo.getAttribute("position") as THREE.BufferAttribute;
    const nrm = this.lampGeo.getAttribute("normal") as THREE.BufferAttribute;
    const uv = this.lampGeo.getAttribute("aLens") as THREE.BufferAttribute;
    const pa = pos.array as Float32Array;
    const na = nrm.array as Float32Array;
    const ua = uv.array as Float32Array;
    for (let k = 0; k < pa.length; k++) {
      pa[k] = a.lampPos[k] + (b.lampPos[k] - a.lampPos[k]) * t;
      na[k] = a.lampNormal[k] + (b.lampNormal[k] - a.lampNormal[k]) * t;
    }
    for (let k = 0; k < ua.length; k++)
      ua[k] = a.lampUv[k] + (b.lampUv[k] - a.lampUv[k]) * t;
    pos.needsUpdate = true;
    nrm.needsUpdate = true;
    uv.needsUpdate = true;

    const posA = new THREE.Vector3();
    const posB = new THREE.Vector3();
    const qa = new THREE.Quaternion();
    const qb = new THREE.Quaternion();
    const s = new THREE.Vector3();
    a.lampMatrix.decompose(posA, qa, s);
    b.lampMatrix.decompose(posB, qb, s);
    const position = posA.lerp(posB, t);
    const rotation = qa.slerp(qb, t);
    const base = new THREE.Matrix4().compose(
      position,
      rotation,
      new THREE.Vector3(1, 1, 1),
    );
    const mirror = new THREE.Matrix4().makeScale(1, 1, -1);
    for (const lamp of this.lamps) {
      lamp.matrix.copy(
        lamp.userData.side === 1 ? base : mirror.clone().multiply(base),
      );
      lamp.matrixWorldNeedsUpdate = true;
    }

    const u = this.lampMaterial.uniforms;
    (u.uPaint.value as THREE.Color).copy(this.paint);
    const ringA =
      a.def.headlight.ringColor === "paint"
        ? this.paint
        : new THREE.Color(a.def.headlight.ringColor);
    const ringB =
      b.def.headlight.ringColor === "paint"
        ? this.paint
        : new THREE.Color(b.def.headlight.ringColor);
    mixOklab(ringA, ringB, t, u.uRingColor.value as THREE.Color);
    u.uRingFinish.value = FINISH_ID[(t < 0.5 ? a : b).def.headlight.ringFinish];
    mixOklab(
      new THREE.Color(a.def.headlight.lensColor),
      new THREE.Color(b.def.headlight.lensColor),
      t,
      u.uLens.value as THREE.Color,
    );
    u.uGraphicA.value = graphicId(a.def.headlight);
    u.uGraphicB.value = graphicId(b.def.headlight);
    u.uMix.value = t;
  }

  private updateWheels(a: CarDef, b: CarDef, t: number) {
    const halfBaseA = (a.rearAxle - a.frontAxle) / 2;
    const halfBaseB = (b.rearAxle - b.frontAxle) / 2;
    for (let w = 0; w < 4; w++) {
      const front = w < 2;
      const side = w % 2 === 0 ? 1 : -1;
      const wa: WheelDef = front ? a.wheels.front : a.wheels.rear;
      const wb: WheelDef = front ? b.wheels.front : b.wheels.rear;
      const radius = lerp(wa.diameter, wb.diameter, t) / 2;
      const width = lerp(wa.width, wb.width, t);
      const rim = lerp(wa.rim, wb.rim, t) / 2;
      const track = front
        ? lerp(a.trackFront, b.trackFront, t)
        : lerp(a.trackRear, b.trackRear, t);
      const halfBase = lerp(halfBaseA, halfBaseB, t);
      const wheel = this.wheels[w];
      wheel.pivot.position.set(
        front ? halfBase : -halfBase,
        radius,
        (side * track) / 2,
      );
      wheel.tyre.scale.set(radius, radius, width);
      // Rim faces sit just inside the outer sidewall, facing out.
      for (const face of wheel.faces) {
        face.scale.setScalar(rim);
        face.position.z = side * (width / 2 - 0.018);
        face.rotation.y = side === 1 ? 0 : Math.PI;
      }
      const same = wa.design === wb.design;
      if (same) {
        applyRim(
          wheel.rims[0],
          lerpRim(RIM_DESIGNS[wa.design], RIM_DESIGNS[wb.design], t),
          t < 0.5 ? wa : wb,
        );
        wheel.rims[0].uniforms.uVisibility.value = 1;
        wheel.faces[1].visible = false;
      } else {
        applyRim(wheel.rims[0], RIM_DESIGNS[wa.design], wa);
        applyRim(wheel.rims[1], RIM_DESIGNS[wb.design], wb);
        wheel.rims[0].uniforms.uVisibility.value = 1 - t;
        wheel.rims[1].uniforms.uVisibility.value = t;
        wheel.faces[1].visible = true;
        wheel.faces[1].position.z = wheel.faces[0].position.z + side * 0.001;
      }
    }
  }

  private updateMirrors(a: CarDef, b: CarDef, t: number) {
    const centre = lerp(
      (a.frontAxle + a.rearAxle) / 2,
      (b.frontAxle + b.rearAxle) / 2,
      t,
    );
    const ma = a.mirror;
    const mb = b.mirror;
    const x = lerp(ma.at[0], mb.at[0], t);
    const y = lerp(ma.at[1], mb.at[1], t);
    const z = lerp(ma.at[2], mb.at[2], t);
    const sx = lerp(ma.size[0], mb.size[0], t);
    const sy = lerp(ma.size[1], mb.size[1], t);
    const sz = lerp(ma.size[2], mb.size[2], t);
    // A single driver-side mirror scales in/out when neighbours differ.
    const rightA = ma.sides === "left" ? 0 : 1;
    const rightB = mb.sides === "left" ? 0 : 1;
    const right = rightA + (rightB - rightA) * t;
    this.mirrors.forEach((mirror, i) => {
      const side = i === 0 ? 1 : -1;
      const k = side === 1 ? right : 1;
      mirror.visible = k > 0.02;
      mirror.position.set(centre - x, y, side * (z + (sz * k) / 2));
      mirror.scale.set(sx * k, sy * k, sz * k);
    });
    const colA = ma.color === "paint" ? this.paint : new THREE.Color(ma.color);
    const colB = mb.color === "paint" ? this.paint : new THREE.Color(mb.color);
    mixOklab(colA, colB, t, this.mirrorMaterial.uniforms.uColor.value);
    this.mirrorMaterial.uniforms.uFinish.value =
      FINISH_ID[(t < 0.5 ? ma : mb).finish];
  }

  private updateWing(a: CarDef, b: CarDef, t: number) {
    const wa = a.wing;
    const wb = b.wing;
    const visA = wa.kind === "none" ? 0 : 1;
    const visB = wb.kind === "none" ? 0 : 1;
    const vis = lerp(visA, visB, t);
    this.wing.visible = vis > 0.01;
    this.lip.visible = this.wing.visible;
    if (!this.wing.visible) return;
    const src = visA ? wa : wb;
    const dst = visB ? wb : wa;
    const centre = lerp(
      (a.frontAxle + a.rearAxle) / 2,
      (b.frontAxle + b.rearAxle) / 2,
      t,
    );
    const k = (sa: number | undefined, sb: number | undefined, d: number) =>
      lerp(sa ?? d, sb ?? d, t);
    const X0 = centre - lerp(src.x0, dst.x0, t);
    const X1 = centre - lerp(src.x1, dst.x1, t);
    const y = lerp(src.y, dst.y, t);
    const half = lerp(src.halfSpan, dst.halfSpan, t);
    const thick = k(src.thickness, dst.thickness, 0.05);
    const rise = k(src.rise, dst.rise, 0);
    const lipH = k(src.lipHeight, dst.lipHeight, 0);

    // The whale tail / tea tray grows out of the engine lid at its leading
    // edge and overhangs at the back: the underside runs from the traced deck
    // (topY) at the front to the slab's own underside at the trailing edge.
    const srcDef = visA ? a : b;
    const dstDef = visB ? b : a;
    const deck0 = lerp(
      sample(srcDef.body.topY, src.x0),
      sample(dstDef.body.topY, dst.x0),
      t,
    );

    // Side profile: leading edge (X0) → trailing edge (X1) sweeping up by `rise`.
    const profile: [number, number][] = [
      [X0, Math.min(y - thick, deck0 - 0.01)],
      [X0, y],
      [X1, y + rise],
      [X1, y + rise - thick],
    ];
    const pos = this.wingGeo.getAttribute("position") as THREE.BufferAttribute;
    profile.forEach(([px, py], i) => {
      pos.setXYZ(i, px, py, half);
      pos.setXYZ(i + 4, px, py, -half);
    });
    pos.needsUpdate = true;
    this.wingGeo.computeVertexNormals();
    this.wingMaterial.uniforms.uColor.value.copy(this.paint);
    this.wingMaterial.uniforms.uVisibility.value = vis;

    // Rubber lip standing on the trailing edge.
    const lipVisible = lipH > 0.002;
    this.lip.visible = lipVisible;
    if (lipVisible) {
      const depth = Math.min(0.04, Math.abs(X1 - X0) * 0.2);
      this.lip.position.set(
        X1 + Math.sign(X0 - X1) * (depth / 2),
        y + rise + lipH / 2,
        0,
      );
      this.lip.scale.set(depth, lipH, half * 2 + 0.01);
      mixOklab(
        new THREE.Color(src.lip),
        new THREE.Color(dst.lip),
        t,
        this.lipMaterial.uniforms.uColor.value,
      );
      this.lipMaterial.uniforms.uVisibility.value = vis;
    }
  }

  private updateExhausts(a: CarDef, b: CarDef, t: number) {
    const centre = lerp(
      (a.frontAxle + a.rearAxle) / 2,
      (b.frontAxle + b.rearAxle) / 2,
      t,
    );
    this.exhausts.forEach((ex, i) => {
      const ea = a.exhausts[i];
      const eb = b.exhausts[i];
      if (!ea && !eb) {
        ex.visible = false;
        return;
      }
      // A pipe only one car has grows or shrinks in place instead of sweeping
      // across from the other pipe's position.
      const pa = ea ?? eb;
      const pb = eb ?? ea;
      if (!pa || !pb) return;
      const r = lerp(ea ? ea[3] : 0, eb ? eb[3] : 0, t);
      ex.visible = r > 0.002;
      ex.position.set(
        centre - lerp(pa[0], pb[0], t),
        lerp(pa[1], pb[1], t),
        lerp(pa[2], pb[2], t),
      );
      ex.scale.set(0.12, r, r);
    });
  }

  dispose() {
    this.bodyGeo.dispose();
    this.bodyMaterial.dispose();
    this.lampGeo.dispose();
    this.lampMaterial.dispose();
  }
}
