import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Life of a 911",
  description:
    "Drag through every generation of the Porsche 911, from the 1963 prototype to today, as one pixel-art car that morphs between them.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
