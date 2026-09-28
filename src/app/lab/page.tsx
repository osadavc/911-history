import { notFound } from "next/navigation";
import { LabStage } from "./lab-stage";
import { LabTimeline } from "./lab-timeline";

/**
 * Dev-only render lab used by the tracing tools (research/tools/render_views.sh,
 * render_morphs.sh): /lab?car=<id>[,<id>]&t=&az=&el=&d=&px=&paint=
 */
export default function LabPage() {
  if (process.env.NODE_ENV === "production") notFound();
  return (
    <main className="flex min-h-dvh flex-col items-center justify-center gap-6 bg-[#f4f3ef]">
      <LabStage />
      <LabTimeline />
    </main>
  );
}
