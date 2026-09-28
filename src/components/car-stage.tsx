"use client";

import { useEffect, useRef } from "react";
import * as THREE from "three";
import type { Stop } from "@/data/types";
import { CarModel } from "@/lib/car/model";
import { createShadow } from "@/lib/pixel/shadow";
import { PixelStage } from "@/lib/pixel/stage";
import type { TimelineController } from "@/lib/timeline";

export type ViewName = "three-quarter" | "side" | "front" | "rear" | "top";

export const VIEWS: Record<ViewName, { azimuth: number; elevation: number }> = {
  "three-quarter": { azimuth: 0.66, elevation: 0.2 },
  side: { azimuth: Math.PI / 2, elevation: 0.04 },
  front: { azimuth: 0, elevation: 0.1 },
  rear: { azimuth: Math.PI, elevation: 0.14 },
  top: { azimuth: Math.PI / 2, elevation: 1.45 },
};

type Props = {
  controller: TimelineController;
  stops: Stop[];
  /** Selected colour hex per stop. */
  paints: string[];
  /** Preset camera; null while the user orbits freely. */
  view: ViewName | null;
  background: string;
  pixelSize: number;
  onUserOrbit?: () => void;
};

const TARGET = new THREE.Vector3(0, 0.56, 0);
const DISTANCE = 10.4;

export function CarStage({
  controller,
  stops,
  paints,
  view,
  background,
  pixelSize,
  onUserOrbit,
}: Props) {
  const hostRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const paintsRef = useRef(paints);
  const viewRef = useRef<ViewName>(view ?? "three-quarter");
  const orbitRef = useRef<{
    setView: (v: ViewName) => void;
    invalidate: () => void;
    setPixelSize: (size: number) => void;
  } | null>(null);
  const pixelSizeRef = useRef(pixelSize);
  const onOrbitRef = useRef(onUserOrbit);

  useEffect(() => {
    onOrbitRef.current = onUserOrbit;
  }, [onUserOrbit]);

  useEffect(() => {
    paintsRef.current = paints;
    orbitRef.current?.invalidate();
  }, [paints]);

  useEffect(() => {
    pixelSizeRef.current = pixelSize;
    orbitRef.current?.setPixelSize(pixelSize);
  }, [pixelSize]);

  useEffect(() => {
    if (!view) return;
    viewRef.current = view;
    orbitRef.current?.setView(view);
  }, [view]);

  useEffect(() => {
    const host = hostRef.current;
    const canvas = canvasRef.current;
    if (!host || !canvas) return;

    const stage = new PixelStage(canvas, {
      pixelSize: pixelSizeRef.current,
      background,
      outline: "#1b1a18",
    });
    const model = new CarModel(stops.map((s) => s.car));
    const shadow = createShadow(background);
    stage.scene.add(shadow.mesh, model.group);

    // Orbit state (spherical around the car), with spring-follow and inertia.
    const start = VIEWS[viewRef.current];
    let azimuth = start.azimuth;
    let elevation = start.elevation;
    let goalAz = azimuth;
    let goalEl = elevation;
    let velAz = 0;
    let dragging = false;
    let lastX = 0;
    let lastY = 0;
    let dirty = true;
    let lastPosition = -1;

    const paintA = new THREE.Color();
    const paintB = new THREE.Color();
    const target = TARGET.clone();

    const fit = () => {
      const rect = host.getBoundingClientRect();
      stage.resize(rect.width, rect.height, window.devicePixelRatio || 1);
      dirty = true;
    };
    fit();
    const observer = new ResizeObserver(fit);
    observer.observe(host);

    const unsubscribe = controller.subscribe(() => {
      dirty = true;
    });

    orbitRef.current = {
      setView(v) {
        const next = VIEWS[v];
        // Take the short way round.
        let delta = next.azimuth - goalAz;
        delta = Math.atan2(Math.sin(delta), Math.cos(delta));
        goalAz += delta;
        goalEl = next.elevation;
        velAz = 0;
        dirty = true;
      },
      invalidate() {
        dirty = true;
      },
      setPixelSize(size) {
        stage.pixelSize = size;
        fit();
      },
    };

    const onDown = (e: PointerEvent) => {
      if (e.button !== 0) return;
      dragging = true;
      lastX = e.clientX;
      lastY = e.clientY;
      velAz = 0;
      canvas.setPointerCapture(e.pointerId);
      onOrbitRef.current?.();
    };
    const onMove = (e: PointerEvent) => {
      if (!dragging) return;
      const dx = e.clientX - lastX;
      const dy = e.clientY - lastY;
      lastX = e.clientX;
      lastY = e.clientY;
      const k = 0.0085;
      goalAz -= dx * k;
      velAz = -dx * k;
      goalEl = Math.min(1.45, Math.max(0.02, goalEl + dy * k * 0.7));
      dirty = true;
    };
    const onUp = () => {
      dragging = false;
    };
    canvas.addEventListener("pointerdown", onDown);
    canvas.addEventListener("pointermove", onMove);
    canvas.addEventListener("pointerup", onUp);
    canvas.addEventListener("pointercancel", onUp);

    let frame = 0;
    const loop = () => {
      frame = requestAnimationFrame(loop);
      if (!dragging && Math.abs(velAz) > 0.00005) {
        goalAz += velAz;
        velAz *= 0.92;
        dirty = true;
      }
      const ease = dragging ? 0.45 : 0.14;
      const dAz = goalAz - azimuth;
      const dEl = goalEl - elevation;
      if (Math.abs(dAz) > 1e-4 || Math.abs(dEl) > 1e-4) {
        azimuth += dAz * ease;
        elevation += dEl * ease;
        dirty = true;
      }
      const position = controller.value;
      if (position !== lastPosition) {
        lastPosition = position;
        dirty = true;
      }
      if (!dirty) return;
      dirty = false;

      const i = Math.max(0, Math.min(stops.length - 2, Math.floor(position)));
      const j = Math.min(stops.length - 1, i + 1);
      const t = Math.min(1, Math.max(0, position - i));
      const list = paintsRef.current;
      paintA.set(list[i] ?? "#bbbbbb");
      paintB.set(list[j] ?? "#bbbbbb");
      model.update(position, paintA, paintB);

      // Keep the shadow and the orbit target on the middle of the body.
      const a = stops[i].car;
      const b = stops[j].car;
      const lerp = (x: number, y: number) => x + (y - x) * t;
      const length = lerp(a.length, b.length);
      const middle =
        lerp((a.frontAxle + a.rearAxle) / 2, (b.frontAxle + b.rearAxle) / 2) -
        length / 2;
      shadow.setSize(length, lerp(a.trackRear, b.trackRear) + 0.35);
      shadow.mesh.position.x = middle;
      target.set(middle, TARGET.y, 0);

      const camera = stage.camera;
      // Pull back on narrow (portrait) stages so the whole car always fits.
      const halfV = THREE.MathUtils.degToRad(camera.fov / 2);
      const halfH = Math.atan(Math.tan(halfV) * camera.aspect);
      const distance = Math.max(
        DISTANCE,
        (length * 0.58) / Math.tan(halfH) + 1.2,
      );
      const ce = Math.cos(elevation);
      camera.position.set(
        target.x + Math.cos(azimuth) * ce * distance,
        target.y + Math.sin(elevation) * distance,
        target.z + Math.sin(azimuth) * ce * distance,
      );
      camera.lookAt(target);
      stage.render();
    };
    frame = requestAnimationFrame(loop);

    return () => {
      cancelAnimationFrame(frame);
      unsubscribe();
      observer.disconnect();
      canvas.removeEventListener("pointerdown", onDown);
      canvas.removeEventListener("pointermove", onMove);
      canvas.removeEventListener("pointerup", onUp);
      canvas.removeEventListener("pointercancel", onUp);
      orbitRef.current = null;
      model.dispose();
      shadow.dispose();
      stage.dispose();
    };
  }, [controller, stops, background]);

  return (
    <div
      ref={hostRef}
      className="absolute inset-0 flex items-center justify-center"
    >
      <canvas
        ref={canvasRef}
        className="cursor-grab touch-none active:cursor-grabbing"
        style={{ imageRendering: "pixelated" }}
        aria-label="Pixel-art 3D Porsche 911. Drag to rotate."
      />
    </div>
  );
}
