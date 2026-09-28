type Listener = (position: number) => void;

const STIFFNESS = 210;
const DAMPING = 29;
const REST_DISTANCE = 0.0004;
const REST_VELOCITY = 0.002;
// How far (in seconds) a flick's velocity is projected before snapping.
const FLICK_PROJECTION = 0.14;

/**
 * Owns the continuous timeline position (0 … stopCount - 1, fractional while
 * morphing between two stops). Lives outside React so the 3D stage and the
 * scrubber can read it every frame without re-rendering the tree.
 */
export class TimelineController {
  readonly stopCount: number;
  private position: number;
  private velocity = 0;
  private target: number | null = null;
  private frame = 0;
  private lastTime = 0;
  private listeners = new Set<Listener>();

  constructor(stopCount: number, initial = 0) {
    this.stopCount = stopCount;
    this.position = initial;
  }

  get value() {
    return this.position;
  }

  get max() {
    return this.stopCount - 1;
  }

  get activeIndex() {
    return Math.round(this.position);
  }

  subscribe(listener: Listener) {
    this.listeners.add(listener);
    listener(this.position);
    return () => {
      this.listeners.delete(listener);
    };
  }

  /** Follow the pointer directly while dragging. */
  scrubTo(position: number, velocity = 0) {
    this.cancel();
    this.velocity = velocity;
    this.set(this.clamp(position));
  }

  /** Spring to a position (usually a stop index). */
  animateTo(position: number) {
    this.target = this.clamp(position);
    this.start();
  }

  /** Release after a drag: project the flick, then settle on a real stop. */
  release(velocity: number) {
    this.velocity = velocity;
    const projected = this.position + velocity * FLICK_PROJECTION;
    this.animateTo(Math.round(this.clamp(projected)));
  }

  step(delta: number) {
    const base = this.target ?? this.activeIndex;
    this.animateTo(Math.round(base) + delta);
  }

  dispose() {
    this.cancel();
    this.listeners.clear();
  }

  private clamp(position: number) {
    return Math.min(this.max, Math.max(0, position));
  }

  private set(position: number) {
    this.position = position;
    for (const listener of this.listeners) listener(position);
  }

  private cancel() {
    if (this.frame) cancelAnimationFrame(this.frame);
    this.frame = 0;
    this.target = null;
  }

  private start() {
    if (this.frame) return;
    this.lastTime = performance.now();
    this.frame = requestAnimationFrame(this.tick);
  }

  private tick = (now: number) => {
    const target = this.target;
    if (target === null) {
      this.frame = 0;
      return;
    }
    // Fixed sub-steps keep the spring stable on slow frames.
    let remaining = Math.min(0.064, (now - this.lastTime) / 1000);
    this.lastTime = now;
    let position = this.position;
    while (remaining > 0) {
      const dt = Math.min(remaining, 1 / 240);
      const accel = -STIFFNESS * (position - target) - DAMPING * this.velocity;
      this.velocity += accel * dt;
      position += this.velocity * dt;
      remaining -= dt;
    }
    if (
      Math.abs(position - target) < REST_DISTANCE &&
      Math.abs(this.velocity) < REST_VELOCITY
    ) {
      this.velocity = 0;
      this.target = null;
      this.frame = 0;
      this.set(target);
      return;
    }
    this.set(this.clamp(position));
    this.frame = requestAnimationFrame(this.tick);
  };
}
