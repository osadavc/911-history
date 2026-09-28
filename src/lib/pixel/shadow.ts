import * as THREE from "three";

/**
 * A contact shadow under the car: a solid core and one lighter rim, with a
 * dithered edge so it reads as pixel art. It never writes depth, so the
 * outline pass ignores it.
 */
export function createShadow(background: THREE.ColorRepresentation) {
  const material = new THREE.ShaderMaterial({
    uniforms: {
      uBackground: { value: new THREE.Color(background) },
      uSize: { value: new THREE.Vector2(4.4, 1.8) },
      uStrength: { value: 0.12 },
    },
    vertexShader: /* glsl */ `
      varying vec2 vPos;
      void main() {
        vPos = position.xy;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: /* glsl */ `
      uniform vec3 uBackground;
      uniform vec2 uSize;
      uniform float uStrength;
      varying vec2 vPos;
      float bayer4(vec2 p) {
        ivec2 i = ivec2(mod(p, 4.0));
        int idx = i.x + i.y * 4;
        float m[16] = float[16](0., 8., 2., 10., 12., 4., 14., 6., 3., 11., 1., 9., 15., 7., 13., 5.);
        return (m[idx] + 0.5) / 16.0;
      }
      void main() {
        vec2 q = vPos / (uSize * 0.5);
        // Rounded-rectangle footprint: a solid core and one lighter rim, no noise.
        vec2 d = abs(q) - vec2(0.78, 0.62);
        float dist = length(max(d, 0.0)) + min(max(d.x, d.y), 0.0);
        float edge = bayer4(gl_FragCoord.xy) * 0.06;
        float level = dist < 0.06 + edge ? 1.0 : (dist < 0.18 + edge ? 0.45 : 0.0);
        if (level <= 0.0) discard;
        gl_FragColor = vec4(uBackground * (1.0 - uStrength * level), 1.0);
      }
    `,
    depthWrite: false,
  });
  const mesh = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), material);
  mesh.rotation.x = -Math.PI / 2;
  mesh.renderOrder = -1;
  return {
    mesh,
    setSize(length: number, width: number) {
      mesh.scale.set(length * 1.02, width * 1.08, 1);
      material.uniforms.uSize.value.set(1, 1);
    },
    setBackground(color: THREE.ColorRepresentation) {
      (material.uniforms.uBackground.value as THREE.Color).set(color);
    },
    dispose() {
      mesh.geometry.dispose();
      material.dispose();
    },
  };
}
