"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth/context";
import { ShieldCheck, Lock, Mail, Building, AlertCircle } from "lucide-react";

export default function RegisterPage() {
  const [merchantName, setMerchantName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isGoogleSubmitting, setIsGoogleSubmitting] = useState(false);
  const { register, loginWithGoogle } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      await register(merchantName, email, password);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Registration failed");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleGoogleSignup = async () => {
    setError(null);
    setIsGoogleSubmitting(true);
    try {
      await loginWithGoogle();
    } catch (err: any) {
      const msg = err?.message || "";
      if (msg.includes("provider is not enabled") || msg.includes("Unsupported provider")) {
        setError(
          "Google Auth Provider is not enabled in your Supabase Dashboard yet. Please go to Supabase Dashboard > Authentication > Providers > Google, enable it, and add Client Credentials."
        );
      } else {
        setError(msg || "Google sign up failed");
      }
      setIsGoogleSubmitting(false);
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center">
      <div className="w-full max-w-md p-8 glass-card rounded-2xl border border-slate-200 bg-white shadow-lg space-y-6">
        <div className="text-center">
          <div className="w-14 h-14 mx-auto mb-4 rounded-2xl bg-blue-600 flex items-center justify-center shadow-md shadow-blue-500/20">
            <ShieldCheck className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Create Merchant Account</h2>
          <p className="text-xs text-slate-500 font-medium mt-1">Start automated AI revenue recovery for your store</p>
        </div>

        {error && (
          <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Google OAuth Single Sign-On Button */}
        <button
          type="button"
          onClick={handleGoogleSignup}
          disabled={isGoogleSubmitting}
          className="w-full py-3 px-4 rounded-xl bg-white hover:bg-slate-50 border border-slate-300 font-bold text-xs text-slate-700 flex items-center justify-center gap-3 transition-all hover:border-slate-400 shadow-2xs cursor-pointer disabled:opacity-50"
        >
          <svg className="w-5 h-5" viewBox="0 0 24 24">
            <path
              fill="#4285F4"
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
            />
            <path
              fill="#34A853"
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            />
            <path
              fill="#FBBC05"
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
            />
            <path
              fill="#EA4335"
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
            />
          </svg>
          <span>{isGoogleSubmitting ? "Connecting to Google..." : "Sign up with Google"}</span>
        </button>

        <div className="relative flex items-center justify-center my-2">
          <div className="border-t border-slate-200 w-full" />
          <span className="bg-white px-3 text-[10px] text-slate-400 uppercase font-bold tracking-wider">
            or sign up with email
          </span>
          <div className="border-t border-slate-200 w-full" />
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-bold uppercase text-slate-500 mb-2">
              Merchant Business Name
            </label>
            <div className="relative">
              <Building className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
              <input
                type="text"
                required
                value={merchantName}
                onChange={(e) => setMerchantName(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl py-2.5 pl-10 pr-4 text-sm text-slate-800 font-medium focus:outline-none focus:border-blue-500"
                placeholder="Acme Commerce Pvt Ltd"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold uppercase text-slate-500 mb-2">
              Merchant Email
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl py-2.5 pl-10 pr-4 text-sm text-slate-800 font-medium focus:outline-none focus:border-blue-500"
                placeholder="owner@acme.com"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold uppercase text-slate-500 mb-2">
              Password
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl py-2.5 pl-10 pr-4 text-sm text-slate-800 font-medium focus:outline-none focus:border-blue-500"
                placeholder="••••••••"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm transition-all shadow-md shadow-blue-600/20 disabled:opacity-50 cursor-pointer"
          >
            {isSubmitting ? "Creating Account..." : "Create Account & Start Trial"}
          </button>
        </form>

        <div className="text-center text-xs text-slate-500 font-medium pt-2">
          Already have an account?{" "}
          <Link href="/login" className="text-blue-600 hover:underline font-bold">
            Sign In Here
          </Link>
        </div>
      </div>
    </div>
  );
}
