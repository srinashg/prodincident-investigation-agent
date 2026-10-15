import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Incident Investigation Console",
  description: "Local console for the production incident investigation agent",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
