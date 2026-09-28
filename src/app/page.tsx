import { LifeOf911 } from "@/components/life-of-911";
import { STOPS } from "@/data/stops";

export default function Home() {
  return <LifeOf911 stops={STOPS} />;
}
