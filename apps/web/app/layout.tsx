import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "RazorRecover AI — AI Revenue Recovery Agent",
  description: "Identify, analyze, and recover lost revenue from failed payments with deterministic policy guardrails.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}
