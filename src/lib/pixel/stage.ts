import * as THREE from "three";
import { shared } from "./materials";

// Colours are authored and shaded directly in sRGB for a predictable
// pixel-art palette; no linear conversion anywhere in the pipeline.
THREE.ColorManagement.enabled = false;

const compositeVertex = /* glsl */ `
  varying vec2 vUv;
  void main() {
    vUv = uv;
    gl_Position = vec4(position.xy, 0.0, 1.0);
  }
`;

const compositeFragment = /* glsl */ `
  #include <packing>
  uniform sampler2D tColor;
  uniform sampler2D tDepth;
  uniform sampler2D tNormal;
  uniform vec2 uRes;
  uniform vec3 uBackground;
  uniform vec3 uOutline;
  uniform float uNear;
  uniform float uFar;
  varying vec2 vUv;

  float rawDepth(vec2 uv) { return texture2D(tDepth, uv).r; }
  float viewDepth(vec2 uv) {
    float d = rawDepth(uv);
    return -perspectiveDepthToViewZ(d, uNear, uFar);
  }
  vec3 normalAt(vec2 uv) { return texture2D(tNormal, uv).rgb * 2.0 - 1.0; }

  void main() {
    vec2 texel = 1.0 / uRes;
    vec2 uv = (floor(vUv * uRes) + 0.5) * texel;
    vec4 color = texture2D(tColor, uv);
    float d0 = rawDepth(uv);
    bool isObject = d0 < 0.99999;

    vec2 offs[4] = vec2[4](vec2(1.0, 0.0), vec2(-1.0, 0.0), vec2(0.0, 1.0), vec2(0.0, -1.0));

    if (!isObject) {
      // Outer 1px outline: background pixel touching the silhouette.
      bool touches = false;
      for (int i = 0; i < 4; i++) {
        if (rawDepth(uv + offs[i] * texel) < 0.99999) touches = true;
      }
      gl_FragColor = vec4(touches ? uOutline : color.rgb, 1.0);
      return;
    }

    float z = viewDepth(uv);
    vec3 n = normalAt(uv);
    float depthEdge = 0.0;
    float normalEdge = 0.0;
    for (int i = 0; i < 4; i++) {
      vec2 o = uv + offs[i] * texel;
      if (rawDepth(o) >= 0.99999) continue;
      float zn = viewDepth(o);
      // Darken the nearer pixel where the surface steps away behind it.
      if (zn - z > 0.06 * z * 0.12 + 0.035) depthEdge = 1.0;
      vec3 nn = normalAt(o);
      float crease = 1.0 - dot(n, nn);
      // Only the upper/left side of a crease is highlighted (consistent light).
      if (crease > 0.22 && dot(n - nn, vec3(1.0, 1.0, 1.0)) > 0.0) normalEdge = 1.0;
    }
    vec3 c = color.rgb;
    if (depthEdge > 0.5) c = mix(c, uOutline, 0.72);
    else if (normalEdge > 0.5) c = mix(c, vec3(1.0), 0.18);
    gl_FragColor = vec4(c, 1.0);
  }
`;

export type StageOptions = {
  /** Size of one art pixel in CSS pixels. */
  pixelSize: number;
  background: THREE.ColorRepresentation;
  outline: THREE.ColorRepresentation;
};

/**
 * Renders a scene at a low internal resolution and composites it with
 * silhouette/crease outlines. The canvas itself is low-res and upscaled by
 * the browser with `image-rendering: pixelated`, so every art pixel is crisp.
 */
export class PixelStage {
  readonly renderer: THREE.WebGLRenderer;
  readonly scene = new THREE.Scene();
  readonly camera = new THREE.PerspectiveCamera(20, 1, 0.5, 60);
  private colorTarget: THREE.WebGLRenderTarget;
  private normalTarget: THREE.WebGLRenderTarget;
  private composite: THREE.ShaderMaterial;
  private quadScene = new THREE.Scene();
  private quadCamera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  private options: StageOptions;
  private canvas: HTMLCanvasElement;
  width = 1;
  height = 1;

  constructor(canvas: HTMLCanvasElement, options: StageOptions) {
    this.canvas = canvas;
    this.options = options;
    this.renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: false,
      alpha: false,
      powerPreference: "high-performance",
    });
    this.renderer.setPixelRatio(1);
    this.renderer.outputColorSpace = THREE.LinearSRGBColorSpace;

    const makeTarget = (depth: boolean) => {
      const target = new THREE.WebGLRenderTarget(1, 1, {
        minFilter: THREE.NearestFilter,
        magFilter: THREE.NearestFilter,
        type: THREE.HalfFloatType,
      });
      if (depth) target.depthTexture = new THREE.DepthTexture(1, 1);
      return target;
    };
    this.colorTarget = makeTarget(true);
    this.normalTarget = makeTarget(true);

    this.composite = new THREE.ShaderMaterial({
      vertexShader: compositeVertex,
      fragmentShader: compositeFragment,
      uniforms: {
        tColor: { value: this.colorTarget.texture },
        tDepth: { value: this.colorTarget.depthTexture },
        tNormal: { value: this.normalTarget.texture },
        uRes: { value: new THREE.Vector2(1, 1) },
        uBackground: { value: new THREE.Color(options.background) },
        uOutline: { value: new THREE.Color(options.outline) },
        uNear: { value: this.camera.near },
        uFar: { value: this.camera.far },
      },
      depthTest: false,
      depthWrite: false,
    });
    const quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), this.composite);
    quad.frustumCulled = false;
    this.quadScene.add(quad);
    this.scene.background = null;
  }

  /** Fit the art-pixel grid into a CSS box; returns the CSS size actually used. */
  resize(cssWidth: number, cssHeight: number, dpr: number) {
    const devicePixel = Math.max(1, Math.round(this.options.pixelSize * dpr));
    const w = Math.max(16, Math.floor((cssWidth * dpr) / devicePixel));
    const h = Math.max(16, Math.floor((cssHeight * dpr) / devicePixel));
    this.width = w;
    this.height = h;
    this.renderer.setSize(w, h, false);
    this.canvas.style.width = `${(w * devicePixel) / dpr}px`;
    this.canvas.style.height = `${(h * devicePixel) / dpr}px`;
    this.colorTarget.setSize(w, h);
    this.normalTarget.setSize(w, h);
    this.composite.uniforms.uRes.value.set(w, h);
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
    return { width: (w * devicePixel) / dpr, height: (h * devicePixel) / dpr };
  }

  /** Art-pixel size in CSS pixels; takes effect on the next resize(). */
  set pixelSize(size: number) {
    this.options.pixelSize = size;
  }

  setBackground(color: THREE.ColorRepresentation) {
    (this.composite.uniforms.uBackground.value as THREE.Color).set(color);
  }

  render() {
    const { renderer, scene, camera } = this;
    const bg = this.composite.uniforms.uBackground.value as THREE.Color;
    this.composite.uniforms.uNear.value = camera.near;
    this.composite.uniforms.uFar.value = camera.far;

    shared.uPass.value = 0;
    renderer.setRenderTarget(this.colorTarget);
    renderer.setClearColor(bg, 1);
    renderer.clear();
    renderer.render(scene, camera);

    shared.uPass.value = 1;
    renderer.setRenderTarget(this.normalTarget);
    renderer.setClearColor(0x8080ff, 1);
    renderer.clear();
    renderer.render(scene, camera);
    shared.uPass.value = 0;

    renderer.setRenderTarget(null);
    renderer.render(this.quadScene, this.quadCamera);
  }

  dispose() {
    this.colorTarget.dispose();
    this.normalTarget.dispose();
    this.composite.dispose();
    this.renderer.dispose();
  }
}
