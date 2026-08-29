import type { Metadata } from "next";
import "./globals.css";
import { QueryProvider } from "@/lib/query/provider";
import { AuthProvider } from "@/lib/auth/context";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";

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
    <html lang="en" className="light">
      <body className="bg-[#f1f6f5] text-slate-800 min-h-screen font-sans antialiased">
        <QueryProvider>
          <AuthProvider>
            <div className="flex">
              <Sidebar />
              <div className="flex-1 ml-64 flex flex-col min-h-screen">
                <Header />
                <main className="flex-1 p-8 overflow-y-auto">
                  {children}
                </main>
              </div>
            </div>
          </AuthProvider>
        </QueryProvider>
      </body>
    </html>
  );
}
