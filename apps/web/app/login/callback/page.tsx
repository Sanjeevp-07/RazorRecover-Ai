"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase";
import { ShieldCheck, Loader2 } from "lucide-react";

export default function AuthCallbackPage() {
  const router = useRouter();
  const [statusMsg, setStatusMsg] = useState("Completing Google authentication...");

  useEffect(() => {
    async function handleCallback() {
      try {
        const { data, error } = await supabase.auth.getSession();
        if (error) {
          throw error;
        }

        if (data?.session) {
          localStorage.setItem("access_token", data.session.access_token);
          if (data.session.refresh_token) {
            localStorage.setItem("refresh_token", data.session.refresh_token);
          }
          setStatusMsg("Authenticated! Redirecting to Merchant Dashboard...");
          setTimeout(() => {
            router.push("/dashboard");
          }, 800);
        } else {
          router.push("/login");
        }
      } catch (err: any) {
        setStatusMsg(`Authentication failed: ${err.message || "Unknown error"}`);
        setTimeout(() => {
          router.push("/login");
        }, 2000);
      }
    }

    handleCallback();
  }, [router]);

  return (
    <div className="min-h-[80vh] flex items-center justify-center">
      <div className="w-full max-w-sm p-8 glass-card rounded-2xl border border-slate-800 text-center space-y-4">
        <div className="w-14 h-14 mx-auto rounded-2xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center shadow-lg shadow-indigo-500/30">
          <ShieldCheck className="w-8 h-8 text-white" />
        </div>
        <div className="flex items-center justify-center gap-2 text-indigo-400">
          <Loader2 className="w-5 h-5 animate-spin" />
          <span className="text-sm font-semibold text-white">Google OAuth Authentication</span>
        </div>
        <p className="text-xs text-slate-400">{statusMsg}</p>
      </div>
    </div>
  );
}
