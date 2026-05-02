"use client";

import { useState } from "react";

interface GenerateDeckButtonProps {
  smeData: object;
}

export default function GenerateDeckButton({ smeData }: GenerateDeckButtonProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/generate-pitch", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(smeData),
      });

      if (!response.ok) {
        let message = "Failed to generate pitch deck.";
        try {
          const payload = await response.json();
          message = payload?.message ?? message;
        } catch {
          // The API normally returns JSON errors, but keep a safe fallback.
        }
        throw new Error(message);
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = "Grantly_Grant_Proposal.pptx";
      anchor.style.display = "none";
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Something went wrong.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-start gap-3">
      <button
        type="button"
        onClick={handleGenerate}
        disabled={isLoading}
        className="rounded-xl bg-gradient-to-r from-[#006780] to-[#16a34a] px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-teal-900/20 transition hover:scale-[1.01] hover:shadow-xl disabled:cursor-not-allowed disabled:opacity-70 disabled:hover:scale-100"
      >
        {isLoading ? "AI is Drafting..." : "Generate Submission Package"}
      </button>

      {error && (
        <p className="max-w-xl rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">
          {error}
        </p>
      )}
    </div>
  );
}
