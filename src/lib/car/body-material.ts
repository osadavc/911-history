import * as THREE from "three";
import { SHADING_GLSL, shared } from "@/lib/pixel/materials";

export const MAX_DECALS = 64;
/** Texels per decal in the parameter texture: shape, material, colour, clip. */
export const DECAL_TEXELS = 4;
export const MAX_POINTS = 1024;

/**
 * Decals are flat 2D shapes projected onto the body along one axis. They
 * turn body pixels into glass, trim, lamps or panel gaps, and because they are
 * just point lists they morph between generations like everything else.
 *
 * plane: 0 side (X,Y)  1 top (X,|Z|)  2 front (|Z|,Y)  3 rear (|Z|,Y)
 * kind:  0 filled polygon  1 polyline (1 art-pixel line)  2 polygon rim band
 */
const vertexShader = /* glsl */ `
  attribute float aUnder;
  varying vec3 vWorldPos;
  varying vec3 vWorldNormal;
  varying vec3 vViewNormal;
  varying vec3 vLocal;
  varying vec3 vLocalNormal;
  varying float vUnder;
  void main() {
    vec4 world = modelMatrix * vec4(position, 1.0);
    vWorldPos = world.xyz;
    vWorldNormal = normalize(mat3(modelMatrix) * normal);
    vViewNormal = normalize(normalMatrix * normal);
    vLocal = position;
    vLocalNormal = normal;
    vUnder = aUnder;
    gl_Position = projectionMatrix * viewMatrix * world;
  }
`;

const fragmentShader = /* glsl */ `
  ${SHADING_GLSL}
  #define MAX_DECALS ${MAX_DECALS}
  #define MAX_POINTS ${MAX_POINTS}
  uniform vec3 uPaint;
  uniform vec3 uUnderColor;
  uniform float uVisibility;
  uniform sampler2D uPts; // MAX_POINTS x 1, RG = decal outline points
  // Decal parameters live in a float texture (not uniform arrays) so the decal
  // count isn't capped by low-end GPUs' uniform limits. Per decal, 4 texels:
  //   0 start, count, plane, kind
  //   1 finish, alpha, width (m), facing
  //   2 r, g, b, side (0 both, 1 right +Z only, -1 left -Z only)
  //   3 depth min, depth max, stripe period (m, sign = axis), stripe duty
  uniform sampler2D uDecals;
  uniform int uDecalCount;
  varying vec3 vWorldPos;
  varying vec3 vWorldNormal;
  varying vec3 vViewNormal;
  varying vec3 vLocal;
  varying vec3 vLocalNormal;
  varying float vUnder;

  float segDist(vec2 p, vec2 a, vec2 b) {
    vec2 pa = p - a, ba = b - a;
    float h = clamp(dot(pa, ba) / max(dot(ba, ba), 1e-9), 0.0, 1.0);
    return length(pa - ba * h);
  }

  void main() {
    // Derivatives must be taken in uniform control flow: once dithered
    // dissolves make neighbouring pixels branch differently, fwidth() inside
    // the decal loop returns garbage and thin lines swell across the body.
    vec3 fw = fwidth(vLocal);
    float dither = bayer4(gl_FragCoord.xy);
    if (uVisibility < 0.999 && dither >= uVisibility) discard;
    if (uPass > 0.5) {
      gl_FragColor = normalOutput(vViewNormal);
      return;
    }

    vec3 N = normalize(vWorldNormal);
    vec3 n = normalize(vLocalNormal);
    if (!gl_FrontFacing) { N = -N; n = -n; }

    int finish = 0;
    vec3 base = uPaint;
    if (vUnder > 0.5) { finish = 3; base = uUnderColor; }

    for (int d = 0; d < MAX_DECALS; d++) {
      if (d >= uDecalCount) break;
      vec4 info = texelFetch(uDecals, ivec2(d * 4, 0), 0);
      vec4 mat = texelFetch(uDecals, ivec2(d * 4 + 1, 0), 0);
      vec4 tint = texelFetch(uDecals, ivec2(d * 4 + 2, 0), 0);
      vec4 clip = texelFetch(uDecals, ivec2(d * 4 + 3, 0), 0);
      if (mat.y < 0.999 && dither >= mat.y) continue;
      int plane = int(info.z + 0.5);
      int kind = int(info.w + 0.5);
      vec2 p; float facing; float depth;
      if (plane == 0) { p = vLocal.xy; facing = abs(n.z); depth = abs(vLocal.z); }
      else if (plane == 1) { p = vec2(vLocal.x, abs(vLocal.z)); facing = n.y; depth = vLocal.y; }
      else if (plane == 2) { p = vec2(abs(vLocal.z), vLocal.y); facing = n.x; depth = vLocal.x; }
      else { p = vec2(abs(vLocal.z), vLocal.y); facing = -n.x; depth = vLocal.x; }
      if (facing < mat.w) continue;
      float sideOnly = tint.w;
      if (sideOnly != 0.0 && sideOnly * vLocal.z < 0.0) continue;
      if (depth < clip.x || depth > clip.y) continue;

      int start = int(info.x + 0.5);
      int count = int(info.y + 0.5);
      bool inside = false;
      float dist = 1e9;
      for (int k = 0; k < MAX_POINTS; k++) {
        if (k >= count) break;
        vec2 a = texelFetch(uPts, ivec2(start + k, 0), 0).xy;
        int kn = k + 1;
        if (kn >= count) {
          if (kind == 1) break;
          kn = 0;
        }
        vec2 b = texelFetch(uPts, ivec2(start + kn, 0), 0).xy;
        if (kind != 1 && ((a.y > p.y) != (b.y > p.y)) &&
            (p.x < (b.x - a.x) * (p.y - a.y) / (b.y - a.y + 1e-9) + a.x)) inside = !inside;
        dist = min(dist, segDist(p, a, b));
      }
      // One art pixel, measured in this plane, so thin lines never vanish.
      vec2 fwp = plane == 0 ? fw.xy : (plane == 1 ? fw.xz : fw.zy);
      float px = max(fwp.x, fwp.y) * 0.5;
      bool hit;
      if (kind == 0) hit = inside;
      else if (kind == 1) hit = dist < max(mat.z, px);
      else hit = (inside || dist < px * 0.5) && dist < max(mat.z, px);
      if (!hit) continue;

      finish = int(mat.x + 0.5);
      base = tint.rgb;
      // Panel gaps read as a darker shade of the surrounding paint, not black.
      if (kind == 1 && finish == 4) { finish = 0; base = uPaint * 0.42; }
      if (clip.z != 0.0) {
        // Positive period: slats across the car; negative: lengthwise louvres.
        bool across = clip.z > 0.0;
        float along = (plane == 1) == across ? p.x : p.y;
        if (fract(along / abs(clip.z)) < clip.w) base *= 0.35;
      }
    }

    gl_FragColor = vec4(shade(finish, base, N, vWorldPos, dither), 1.0);
  }
`;

export type BodyMaterial = THREE.ShaderMaterial & {
  uniforms: {
    uPaint: { value: THREE.Color };
    uUnderColor: { value: THREE.Color };
    uVisibility: { value: number };
    uPts: { value: THREE.DataTexture };
    uDecals: { value: THREE.DataTexture };
    uDecalCount: { value: number };
  };
};

function createDataTexture(width: number, channels: 2 | 4) {
  const texture = new THREE.DataTexture(
    new Float32Array(width * channels),
    width,
    1,
    channels === 2 ? THREE.RGFormat : THREE.RGBAFormat,
    THREE.FloatType,
  );
  texture.minFilter = THREE.NearestFilter;
  texture.magFilter = THREE.NearestFilter;
  texture.needsUpdate = true;
  return texture;
}

export function createBodyMaterial(): BodyMaterial {
  const material = new THREE.ShaderMaterial({
    vertexShader,
    fragmentShader,
    uniforms: {
      uPass: shared.uPass,
      uLightDir: shared.uLightDir,
      uPaint: { value: new THREE.Color("#c0c0c0") },
      uUnderColor: { value: new THREE.Color("#1e1e1f") },
      uVisibility: { value: 1 },
      uPts: { value: createDataTexture(MAX_POINTS, 2) },
      uDecals: { value: createDataTexture(MAX_DECALS * DECAL_TEXELS, 4) },
      uDecalCount: { value: 0 },
    },
    side: THREE.DoubleSide,
  });
  return material as BodyMaterial;
}
