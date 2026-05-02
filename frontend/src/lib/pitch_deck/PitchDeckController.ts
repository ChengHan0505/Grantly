import type { GrantPitchDeckData } from "./GeminiPitchService";
import { GeminiPitchService } from "./GeminiPitchService";
import { PptxGeneratorService, type PptxGeneratorOptions } from "./PptxGeneratorService";

export interface PitchDeckControllerOptions {
  geminiService?: GeminiPitchService;
  pptxService?: PptxGeneratorService;
  pptxOptions?: PptxGeneratorOptions;
}

export interface GeneratedPitchDeckResult {
  fileName: string;
  mimeType: string;
  buffer: Buffer;
  structuredDeckData: GrantPitchDeckData;
}

export interface MinimalRequestLike {
  body?: unknown;
}

export interface MinimalResponseLike {
  setHeader(name: string, value: string): void;
  status(code: number): MinimalResponseLike;
  json(payload: unknown): void;
  send(payload: Buffer): void;
}

export class PitchDeckController {
  private readonly geminiService: GeminiPitchService;
  private readonly pptxService: PptxGeneratorService;
  private readonly pptxOptions: PptxGeneratorOptions;

  constructor(options: PitchDeckControllerOptions = {}) {
    this.geminiService = options.geminiService ?? new GeminiPitchService();
    this.pptxService = options.pptxService ?? new PptxGeneratorService();
    this.pptxOptions = options.pptxOptions ?? {};
  }

  async generatePitchDeck(rawSmeJson: unknown): Promise<GeneratedPitchDeckResult> {
    const structuredDeckData = await this.geminiService.extractPitchDeckData(rawSmeJson);
    const buffer = await this.pptxService.generatePitchDeck(
      structuredDeckData,
      this.pptxOptions,
    );

    return {
      fileName: this.createFileName(structuredDeckData.titleSlide.companyName),
      mimeType: PPTX_MIME_TYPE,
      buffer,
      structuredDeckData,
    };
  }

  async generatePitchDeckHttp(
    req: MinimalRequestLike,
    res: MinimalResponseLike,
  ): Promise<void> {
    try {
      const result = await this.generatePitchDeck(req.body);

      res.setHeader("Content-Type", result.mimeType);
      res.setHeader(
        "Content-Disposition",
        `attachment; filename="${result.fileName}"`,
      );
      res.setHeader("Content-Length", String(result.buffer.length));
      res.send(result.buffer);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Pitch deck generation failed.";
      res.status(500).json({
        error: "PITCH_DECK_GENERATION_FAILED",
        message,
      });
    }
  }

  private createFileName(companyName: string): string {
    const slug = companyName
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/(^-|-$)/g, "");
    return `${slug || "sme"}-grant-pitch-deck.pptx`;
  }
}

export const pitchDeckController = {
  generatePitchDeck(rawSmeJson: unknown): Promise<GeneratedPitchDeckResult> {
    return new PitchDeckController().generatePitchDeck(rawSmeJson);
  },
  generatePitchDeckHttp(
    req: MinimalRequestLike,
    res: MinimalResponseLike,
  ): Promise<void> {
    return new PitchDeckController().generatePitchDeckHttp(req, res);
  },
};

const PPTX_MIME_TYPE = "application/vnd.openxmlformats-officedocument.presentationml.presentation";
