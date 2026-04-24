import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Grantly — The Malaysia SME Grant Copilot",
  description:
    "An AI-powered workflow copilot that automates the entire grant readiness process. Fluid, intelligent, and designed for technical storytelling.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,1,0&display=swap"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
