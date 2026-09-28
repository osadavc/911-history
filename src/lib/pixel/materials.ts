import * as THREE from "three";

export type Finish =
  | "paint"
  | "chrome"
  | "glass"
  | "rubber"
  | "satin"
  | "lens"
  | "emissive";

/** Uniforms shared by every material in the scene (one object, many materials). */
export const shared = {
  uPass: { value: 0 }, // 0 = beauty, 1 = view-space normals for edge detection
  uLightDir: { value: new THREE.Vector3(-0.45, 0.8, 0.55).normalize() },
};

export const FINISH_ID: Record<Finish, number> = {
  paint: 0,
  chrome: 1,
  glass: 2,
  rubber: 3,
  satin: 4,
  lens: 5,
  emissive: 6,
};

/** GLSL shared by every pixel material: dithering, posterising and the shading model. */
export const SHADING_GLSL = /* glsl */ `
  uniform float uPass;
  uniform vec3 uLightDir;

  float bayer4(vec2 p) {
    ivec2 i = ivec2(mod(p, 4.0));
    int idx = i.x + i.y * 4;
    float m[16] = float[16](0., 8., 2., 10., 12., 4., 14., 6., 3., 11., 1., 9., 15., 7., 13., 5.);
    return (m[idx] + 0.5) / 16.0;
  }

  // Posterise into (steps + 1) levels; dither only a thin band at each edge.
  float quantize(float v, float steps, float dither) {
    float q = v * steps + (dither - 0.5) * 0.12;
    return clamp(floor(q + 0.5) / steps, 0.0, 1.0);
  }

  // Stylised studio: bright softbox sky, crisp horizon, warm grey floor.
  vec3 studio(vec3 r) {
    float y = r.y;
    vec3 sky = mix(vec3(0.93, 0.95, 0.98), vec3(0.72, 0.78, 0.86), smoothstep(0.05, 0.9, y));
    vec3 floorC = mix(vec3(0.36, 0.35, 0.34), vec3(0.2, 0.2, 0.21), smoothstep(-0.05, -0.7, y));
    return y > -0.02 ? sky : floorC;
  }

  vec3 shade(int finish, vec3 base, vec3 N, vec3 worldPos, float dither) {
    vec3 V = normalize(cameraPosition - worldPos);
    vec3 L = normalize(uLightDir);
    vec3 H = normalize(L + V);
    vec3 R = reflect(-V, N);
    float ndl = dot(N, L);
    float fres = pow(1.0 - clamp(dot(N, V), 0.0, 1.0), 3.0);
    float spec = pow(max(dot(N, H), 0.0), 70.0);
    vec3 env = studio(R);
    vec3 col;
    if (finish == 0) {
      // Car paint: light bands (dithered only at band edges), a crisp
      // studio-horizon reflection and hard-edged glints.
      float diff = clamp(ndl * 0.55 + 0.5, 0.0, 1.0);
      float band = quantize(diff, 3.0, dither);
      vec3 shadow = base * vec3(0.46, 0.46, 0.54);
      vec3 lit = base * 1.07 + 0.035;
      col = mix(shadow, lit, band);
      float refl = floor(mix(0.04, 0.42, fres) * 3.0 + 0.5) / 3.0;
      float lum = max(base.r, max(base.g, base.b));
      col = mix(col, env * (0.3 + 0.75 * lum), refl);
      col += step(0.55, spec) * 0.5;
    } else if (finish == 1) {
      // Chrome: all reflection, stepped for a pixel-art read.
      float l = dot(env, vec3(0.333));
      col = quantize(l, 4.0, dither) * vec3(0.95, 0.97, 1.0) + 0.04;
      col += step(0.4, spec) * 0.5;
    } else if (finish == 2) {
      // Glass: dark tint, sky reflection that grows at grazing angles.
      float refl = floor(mix(0.1, 0.55, fres) * 3.0 + 0.5) / 3.0;
      col = mix(base, env * 0.8, refl);
      col += step(0.6, spec) * 0.6;
    } else if (finish == 3) {
      float diff = clamp(ndl * 0.5 + 0.5, 0.0, 1.0);
      col = base * (0.55 + 0.5 * quantize(diff, 2.0, dither));
    } else if (finish == 4) {
      float diff = clamp(ndl * 0.5 + 0.5, 0.0, 1.0);
      col = base * (0.5 + 0.6 * quantize(diff, 3.0, dither));
      col += step(0.7, spec) * 0.25;
    } else if (finish == 5) {
      // Lamp lens: bright core with a reflective rim.
      col = mix(base, env, 0.35 * fres) + step(0.5, spec) * 0.5;
    } else {
      col = base;
    }
    return clamp(col, 0.0, 1.0);
  }

  vec4 normalOutput(vec3 viewNormal) {
    vec3 vn = normalize(viewNormal);
    if (!gl_FrontFacing) vn = -vn;
    return vec4(vn * 0.5 + 0.5, 1.0);
  }
`;

const vertexShader = /* glsl */ `
  varying vec3 vWorldPos;
  varying vec3 vWorldNormal;
  varying vec3 vViewNormal;
  void main() {
    vec4 world = modelMatrix * vec4(position, 1.0);
    vWorldPos = world.xyz;
    vWorldNormal = normalize(mat3(modelMatrix) * normal);
    vViewNormal = normalize(normalMatrix * normal);
    gl_Position = projectionMatrix * viewMatrix * world;
  }
`;

const fragmentShader = /* glsl */ `
  ${SHADING_GLSL}
  uniform vec3 uColor;
  uniform float uFinish;
  uniform float uVisibility;
  varying vec3 vWorldPos;
  varying vec3 vWorldNormal;
  varying vec3 vViewNormal;

  void main() {
    float dither = bayer4(gl_FragCoord.xy);
    if (uVisibility < 0.999 && dither >= uVisibility) discard;
    if (uPass > 0.5) {
      gl_FragColor = normalOutput(vViewNormal);
      return;
    }
    vec3 N = normalize(vWorldNormal);
    if (!gl_FrontFacing) N = -N;
    gl_FragColor = vec4(shade(int(uFinish + 0.5), uColor, N, vWorldPos, dither), 1.0);
  }
`;

export type PixelMaterial = THREE.ShaderMaterial & {
  uniforms: {
    uColor: { value: THREE.Color };
    uFinish: { value: number };
    uVisibility: { value: number };
  };
};

export function createMaterial(
  finish: Finish,
  color: THREE.ColorRepresentation = "#ffffff",
  options: { side?: THREE.Side } = {},
): PixelMaterial {
  const material = new THREE.ShaderMaterial({
    vertexShader,
    fragmentShader,
    uniforms: {
      uPass: shared.uPass,
      uLightDir: shared.uLightDir,
      uColor: { value: new THREE.Color(color) },
      uFinish: { value: FINISH_ID[finish] },
      uVisibility: { value: 1 },
    },
    side: options.side ?? THREE.FrontSide,
  });
  return material as PixelMaterial;
}
