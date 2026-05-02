import { NextResponse } from "next/server";

import { pitchDeckController } from "@/lib/pitch_deck/PitchDeckController";

export const runtime = "nodejs";

const PPTX_MIME_TYPE =
  "application/vnd.openxmlformats-officedocument.presentationml.presentation";
const FILE_NAME = "Grantly_Grant_Proposal.pptx";

export async function POST(request: Request) {
  try {
    const smeData = await request.json();
    const result = await pitchDeckController.generatePitchDeck(smeData);

    return new NextResponse(new Uint8Array(result.buffer), {
      status: 200,
      headers: {
        "Content-Type": PPTX_MIME_TYPE,
        "Content-Disposition": `attachment; filename="${FILE_NAME}"`,
        "Content-Length": String(result.buffer.length),
      },
    });
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "Failed to generate pitch deck.";

    return NextResponse.json(
      {
        error: "PITCH_DECK_GENERATION_FAILED",
        message,
      },
      { status: 500 },
    );
  }
}
