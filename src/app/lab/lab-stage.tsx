"use client";

import { useEffect, useRef } from "react";
import * as THREE from "three";
import { CarModel } from "@/lib/car/model";
import type { CarDef } from "@/lib/car/types";
import { createMaterial } from "@/lib/pixel/materials";
import { PixelStage } from "@/lib/pixel/stage";
import { testCar } from "./test-car";

export function LabStage() {
  const hostRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const host = hostRef.current;
    const canvas = canvasRef.current;
    if (!host || !canvas) return;
    const stage = new PixelStage(canvas, {
      pixelSize: 3,
      background: "#f4f3ef",
      outline: "#1d1c1a",
    });
    const paint = createMaterial("paint", "#c8102e");
    const knot = new THREE.Mesh(
      new THREE.TorusKnotGeometry(0.8, 0.28, 180, 32),
      paint,
    );
    knot.position.set(-1.4, 1.1, 0);
    const chrome = new THREE.Mesh(
      new THREE.SphereGeometry(0.6, 48, 32),
      createMaterial("chrome"),
    );
    chrome.position.set(0.6, 0.6, 0.4);
    const glass = new THREE.Mesh(
      new THREE.BoxGeometry(1, 1, 1),
      createMaterial("glass", "#1b242c"),
    );
    glass.position.set(1.9, 0.5, -0.4);
    const tyre = new THREE.Mesh(
      new THREE.TorusGeometry(0.4, 0.16, 16, 48),
      createMaterial("rubber", "#2a2a2a"),
    );
    tyre.position.set(0.2, 0.5, 1.6);
    const params = new URLSearchParams(window.location.search);
    const carIds = (params.get("car") ?? "").split(",").filter(Boolean);
    let disposed = false;
    const setup = (defs: CarDef[]) => {
      if (disposed) return;
      const model = new CarModel(defs.length === 1 ? [defs[0], defs[0]] : defs);
      const morph = Number(params.get("t") ?? 0);
      const az = Number(params.get("az") ?? 0.66);
      const el = Number(params.get("el") ?? 0.2);
      const dist = Number(params.get("d") ?? 11);
      const paintHex = params.get("paint") ?? "#c8102e";
      model.update(morph, new THREE.Color(paintHex), new THREE.Color(paintHex));
      if (params.has("shapes")) stage.scene.add(knot, chrome, glass, tyre);
      else stage.scene.add(model.group);
      const first = defs[0];
      const cx = (first.frontAxle + first.rearAxle) / 2 - first.length / 2;
      stage.camera.position.set(
        cx + Math.cos(az) * Math.cos(el) * dist,
        0.55 + Math.sin(el) * dist,
        Math.sin(az) * Math.cos(el) * dist,
      );
      stage.camera.lookAt(cx, 0.55, 0);
      (window as unknown as { __labReady: boolean }).__labReady = true;
    };
    stage.pixelSize = Number(params.get("px") ?? 3);
    if (carIds.length) {
      Promise.all(
        carIds.map((id) =>
          fetch(`/lab/car?id=${id}`).then((r) => r.json() as Promise<CarDef>),
        ),
      ).then(setup);
    } else {
      setup([
        testCar("a", 4.2, 1.3, "fuchs"),
        testCar("b", 4.5, 1.26, "twin-spoke"),
      ]);
    }
    const fit = () => {
      const rect = host.getBoundingClientRect();
      stage.resize(rect.width, rect.height, window.devicePixelRatio || 1);
    };
    fit();
    const observer = new ResizeObserver(fit);
    observer.observe(host);
    let frame = 0;
    const loop = (t: number) => {
      knot.rotation.y = t * 0.0004;
      stage.render();
      frame = requestAnimationFrame(loop);
    };
    frame = requestAnimationFrame(loop);
    return () => {
      disposed = true;
      cancelAnimationFrame(frame);
      observer.disconnect();
      stage.dispose();
    };
  }, []);

  return (
    <div
      ref={hostRef}
      className="flex h-[50vh] w-[90vw] items-center justify-center"
    >
      <canvas ref={canvasRef} style={{ imageRendering: "pixelated" }} />
    </div>
  );
}
