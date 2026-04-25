"use client";

import React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { signInWithEmailAndPassword, signInWithPopup } from "firebase/auth";
import { auth, googleProvider } from "@/lib/firebase";
import { createBackendSession } from "@/services/grantlySession";
import styles from "./page.module.css";

function MI({ name, size = 24, color }: { name: string; size?: number; color?: string }) {
  return <span className="material-icon" style={{ fontSize: size, color }}>{name}</span>;
}

export default function LoginPage() {
  const [width, setWidth] = React.useState(1200);
  React.useEffect(() => {
    const update = () => setWidth(window.innerWidth);
    update();
    window.addEventListener("resize", update);
    return () => window.removeEventListener("resize", update);
  }, []);

  const isWide = width >= 1024;

  return (
    <div className={styles.root}>
      <div className={styles.bgWrap}>
        {isWide && (
          <div className={styles.leftBg}>
            <div className={styles.meshLayer}>
              <div className={styles.glow} style={{ left: "42%", top: "20%", width: 420, height: 300, background: "radial-gradient(circle, rgba(0,103,128,0.5), transparent)" }} />
              <div className={styles.glow} style={{ left: "80%", top: "2%", width: 360, height: 280, background: "radial-gradient(circle, rgba(69,177,212,0.4), transparent)" }} />
              <div className={styles.glow} style={{ left: "2%", top: "48%", width: 380, height: 320, background: "radial-gradient(circle, rgba(73,75,214,0.4), transparent)" }} />
              <div className={styles.glow} style={{ left: "78%", top: "50%", width: 300, height: 260, background: "radial-gradient(circle, rgba(254,147,44,0.25), transparent)" }} />
            </div>
            <div className={styles.leftFade} />
          </div>
        )}
        <div className={styles.rightBg}>
          <div className={styles.meshLayerLight}>
            <div className={styles.glow} style={{ left: "42%", top: "20%", width: 420, height: 300, background: "radial-gradient(circle, rgba(0,103,128,0.12), transparent)" }} />
            <div className={styles.glow} style={{ left: "80%", top: "2%", width: 360, height: 280, background: "radial-gradient(circle, rgba(69,177,212,0.1), transparent)" }} />
          </div>
        </div>
      </div>

      <Link href="/" className={styles.backBtn}>
        <MI name="arrow_back" size={18} color="#006780" />
        <span>Return to Home</span>
      </Link>

      <div className={styles.content}>
        <div className={styles.inner}>
          {isWide && <LeftPane />}
          <div className={styles.formSide}>
            <div className={styles.formScroll}>
              <LoginCard />
              <div style={{ height: 24 }} />
              <RegisterLink />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function LeftPane() {
  return (
    <div className={styles.leftPane}>
      <div className={styles.leftContent}>
        <h1 className={styles.leftTitle}>The Intelligent</h1>
        <h1 className={styles.etherGradient}>Ether.</h1>
        <div style={{ height: 16 }} />
        <p className={styles.leftSub}>
          Weave data into narrative. Dissolve the friction{"\n"}between insight and impact.
        </p>
      </div>
    </div>
  );
}

function LoginCard() {
  const [rememberMe, setRememberMe] = React.useState(false);
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [loading, setLoading] = React.useState(false);
  const [googleLoading, setGoogleLoading] = React.useState(false);
  const [error, setError] = React.useState("");
  const router = useRouter();

  const authErrorMessage = (err: unknown): string => {
    const code = typeof err === "object" && err !== null && "code" in err ? String((err as { code?: string }).code) : "";
    if (code.includes("auth/invalid-credential") || code.includes("auth/wrong-password") || code.includes("auth/user-not-found")) {
      return "Email or password is incorrect.";
    }
    if (code.includes("auth/invalid-email")) return "Enter a valid email address.";
    if (code.includes("auth/too-many-requests")) return "Too many attempts. Please wait a moment and try again.";
    if (code.includes("auth/operation-not-allowed")) return "Email/password login is not enabled for this Firebase project.";
    return err instanceof Error ? err.message : "Unable to sign in. Please try again.";
  };

  const handleEmailSignIn = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!email.trim()) {
      setError("Enter your email address to open the workspace.");
      return;
    }
    if (!password) {
      setError("Enter your password to open the workspace.");
      return;
    }

    setLoading(true);
    setError("");
    try {
      const credential = await signInWithEmailAndPassword(auth, email.trim(), password);
      if (!credential.user.email) {
        throw new Error("Firebase did not return an email address for this account.");
      }
      await createBackendSession({
        email: credential.user.email,
        displayName: credential.user.displayName || credential.user.email.split("@")[0],
        externalAuthId: credential.user.uid,
      });
      router.push("/dashboard");
    } catch (err: unknown) {
      setError(authErrorMessage(err));
      setLoading(false);
    }
  };

  const handleGoogleSignIn = async () => {
    setGoogleLoading(true);
    setError("");
    try {
      const credential = await signInWithPopup(auth, googleProvider);
      if (!credential.user.email) {
        throw new Error("Google did not return an email address for this account.");
      }
      await createBackendSession({
        email: credential.user.email,
        displayName: credential.user.displayName,
        externalAuthId: credential.user.uid,
      });
      router.push("/dashboard");
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Google sign-in failed. Please try again.";
      setError(message);
      setGoogleLoading(false);
    }
  };

  return (
    <form className={`${styles.loginCard} glass-strong`} onSubmit={handleEmailSignIn}>
      <h2 className={styles.cardTitle}>Grantly</h2>
      <p className={styles.cardSub}>Enter your credentials to access the workspace.</p>
      <div style={{ height: 24 }} />

      <GhostField label="EMAIL ADDRESS" hint="jane@example.com" value={email} onChange={setEmail} />
      <div style={{ height: 16 }} />
      <GhostField label="PASSWORD" hint="Password" value={password} onChange={setPassword} forgotText="Forgot?" obscure />
      <div style={{ height: 16 }} />

      <label className={styles.remember}>
        <input type="checkbox" checked={rememberMe} onChange={(e) => setRememberMe(e.target.checked)} className={styles.checkbox} />
        <span>Remember me on this device</span>
      </label>
      <div style={{ height: 20 }} />

      {error && (
        <div style={{ background: "#fff0f0", border: "1px solid #fca5a5", borderRadius: 8, padding: "10px 14px", marginBottom: 16, fontSize: 13, color: "#BA1A1A" }}>
          {error}
        </div>
      )}

      <button
        type="submit"
        disabled={loading || googleLoading}
        className="btn-gradient"
        style={{ height: 48, width: "100%", border: "none", display: "flex", alignItems: "center", justifyContent: "center", cursor: loading ? "wait" : "pointer", opacity: loading ? 0.72 : 1 }}
      >
        {loading ? "Opening Workspace..." : "Access Workspace"}
      </button>
      <div style={{ height: 24 }} />

      <div className={styles.dividerRow}>
        <div className={styles.dividerLine} />
        <span className={styles.dividerText}>OR</span>
        <div className={styles.dividerLine} />
      </div>
      <div style={{ height: 24 }} />

      <button
        type="button"
        onClick={handleGoogleSignIn}
        disabled={googleLoading || loading}
        className={styles.googleBtn}
        style={{ width: "100%", border: "none", cursor: googleLoading ? "wait" : "pointer", opacity: googleLoading ? 0.7 : 1 }}
      >
        {googleLoading ? (
          <span style={{ display: "flex", alignItems: "center", gap: 8, justifyContent: "center" }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" style={{ animation: "spin 0.8s linear infinite" }}>
              <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
            </svg>
            Signing in...
          </span>
        ) : (
          <>
            <div className={styles.googleMark}>G</div>
            <span>Continue with Google</span>
          </>
        )}
      </button>
      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </form>
  );
}

function GhostField({
  label,
  hint,
  forgotText,
  obscure,
  value,
  onChange,
}: {
  label: string;
  hint: string;
  forgotText?: string;
  obscure?: boolean;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <div className="ghost-field">
      <div className={styles.fieldHeader}>
        <label>{label}</label>
        {forgotText && <button type="button" className={styles.forgotBtn}>{forgotText}</button>}
      </div>
      <input type={obscure ? "password" : "email"} placeholder={hint} value={value} onChange={(event) => onChange(event.target.value)} />
    </div>
  );
}

function RegisterLink() {
  return (
    <Link href="/initialize" className={styles.registerLink}>
      <span>New user? Register now.</span>
      <MI name="arrow_forward" size={16} color="#904D00" />
    </Link>
  );
}
