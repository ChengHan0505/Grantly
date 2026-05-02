import pptxgen from "pptxgenjs";
import path from "path";
import type { GrantPitchDeckData } from "./GeminiPitchService";

export interface PptxGeneratorOptions {
  backgroundPath?: string;
  author?: string;
}

// Template is a dark, minimalist proposal deck with a bottom-center sunburst.
// All coordinates assume PowerPoint widescreen: 10" x 5.625".
const SLIDE_W = 10;
const SLIDE_H = 5.625;

// The creative brief reads as a clean, high-contrast sans-serif proposal style.
const FONT = "Helvetica";
const BG = "202020";
const TEXT = "F5F5F5";
const MUTED = "E2E8F0";
const SUBTLE = "94A3B8";
const TABLE_HEADER = "F1F5F9";
const TABLE_TEXT = "1E293B";

const TITLE = { x: 0.55, y: 0.58, w: 8.25, h: 0.62 };
const BODY = { x: 0.72, y: 1.42, w: 8.45, h: 2.62 };

const MISSING_PLACEHOLDER = "—";
const MISSING_VALUES = new Set([
  "",
  "not specified",
  "to be confirmed",
  "tbc",
  "n/a",
  "na",
  "none",
  "null",
  "undefined",
]);

type Box = { x: number; y: number; w: number; h: number };

export class PptxGeneratorService {
  async generatePitchDeck(
    deckData: GrantPitchDeckData,
    options: PptxGeneratorOptions = {},
  ): Promise<Buffer> {
    const pptx = new pptxgen();
    pptx.layout = "LAYOUT_16x9";
    pptx.author = options.author ?? "Grantly";
    pptx.company = "Grantly";
    pptx.subject = "Government Grant Pitch Deck";
    pptx.title = `${safe(deckData.titleSlide.companyName)} Grant Pitch Deck`;
    pptx.theme = { headFontFace: FONT, bodyFontFace: FONT };

    const backgroundPath =
      options.backgroundPath ?? path.join(process.cwd(), "public", "slide-bg.png");

    this.addTitleSlide(pptx, deckData, backgroundPath);
    this.addProblemSlide(pptx, deckData, backgroundPath);
    this.addSolutionSlide(pptx, deckData, backgroundPath);
    this.addMarketSlide(pptx, deckData, backgroundPath);
    this.addBudgetSlide(pptx, deckData, backgroundPath);
    this.addTeamSlide(pptx, deckData, backgroundPath);

    const buffer = await pptx.write({ outputType: "nodebuffer" });
    return Buffer.isBuffer(buffer) ? buffer : Buffer.from(buffer as ArrayBuffer);
  }

  private addTitleSlide(pptx: pptxgen, data: GrantPitchDeckData, bgPath: string): void {
    const slide = this.master(pptx, bgPath);

    slide.addText(safe(data.titleSlide.companyName), {
      x: 0.9, // X: wide centered title area; nudge right/left here.
      y: 1.62, // Y: vertical hero placement above the sunburst.
      w: 8.2, // W: constrained centered width to prevent edge bleed.
      h: 0.82, // H: one-line company name; wraps if needed.
      fontFace: FONT,
      fontSize: 34,
      bold: true,
      color: TEXT,
      align: "center",
      valign: "top",
      wrap: true,
      fit: "shrink",
    });

    slide.addText(safe(data.titleSlide.tagline), {
      x: 1.35, // X: narrower centered tagline column.
      y: 2.52, // Y: directly below company name.
      w: 7.3, // W: premium short-line tagline width.
      h: 0.48, // H: single tagline line.
      fontFace: FONT,
      fontSize: 17,
      color: MUTED,
      align: "center",
      valign: "top",
      wrap: true,
      fit: "shrink",
    });

    slide.addText(`Requested Grant: ${safe(data.titleSlide.requestedGrantAmount)}`, {
      x: 1.6, // X: centered grant-ask label.
      y: 3.38, // Y: safely above sunburst graphic.
      w: 6.8, // W: centered financial label width.
      h: 0.42, // H: one-line grant amount.
      fontFace: FONT,
      fontSize: 15,
      color: SUBTLE,
      align: "center",
      valign: "top",
      wrap: true,
      fit: "shrink",
    });
  }

  private addProblemSlide(pptx: pptxgen, data: GrantPitchDeckData, bgPath: string): void {
    const slide = this.master(pptx, bgPath);
    this.title(slide, "INTRODUCTION");
    this.kicker(slide, "Problem context");
    this.summary(slide, data.problemSlide.macroProblem, { x: 0.72, y: 1.45, w: 8.45, h: 0.62 });
    this.body(slide, data.problemSlide.specificPainPoint, { x: 0.72, y: 2.2, w: 8.45, h: 0.46 });
    this.bullets(slide, data.problemSlide.bulletPoints, { x: 0.82, y: 2.92, w: 8.05, h: 1.12 });
  }

  private addSolutionSlide(pptx: pptxgen, data: GrantPitchDeckData, bgPath: string): void {
    const slide = this.master(pptx, bgPath);
    this.title(slide, "OUR STRATEGY");
    this.kicker(slide, "Solution & innovation");
    this.summary(slide, data.solutionSlide.productOrService, { x: 0.72, y: 1.45, w: 8.45, h: 0.62 });
    this.body(slide, data.solutionSlide.innovativeEdge, { x: 0.72, y: 2.2, w: 8.45, h: 0.46 });
    this.bullets(slide, data.solutionSlide.bulletPoints, { x: 0.82, y: 2.92, w: 8.05, h: 1.12 });
  }

  private addMarketSlide(pptx: pptxgen, data: GrantPitchDeckData, bgPath: string): void {
    const slide = this.master(pptx, bgPath);
    this.title(slide, "THE STORY");
    this.kicker(slide, "Market & traction");

    const metrics = [
      ["TAM", data.marketSlide.tam],
      ["SAM", data.marketSlide.sam],
      ["SOM", data.marketSlide.som],
    ].filter(([, value]) => hasValue(value));

    metrics.slice(0, 3).forEach(([label, value], index) => {
      const x = 0.72 + index * 2.88; // X: three metric columns.
      this.microLabel(slide, label, { x, y: 1.45, w: 2.35, h: 0.2 });
      this.metric(slide, safe(value), { x, y: 1.78, w: 2.35, h: 0.48 });
    });

    this.body(slide, data.marketSlide.currentTraction, { x: 0.72, y: 2.6, w: 8.45, h: 0.46 });
    this.bullets(slide, data.marketSlide.bulletPoints, { x: 0.82, y: 3.22, w: 8.05, h: 0.9 });
  }

  private addBudgetSlide(pptx: pptxgen, data: GrantPitchDeckData, bgPath: string): void {
    const slide = this.master(pptx, bgPath);
    this.title(slide, "CORE VALUES");
    this.kicker(slide, "Use of funds");
    this.body(slide, data.budgetSlide.grantUtilizationSummary, { x: 0.72, y: 1.38, w: 8.45, h: 0.44 });

    const table = {
      x: 0.72, // X: table left edge.
      y: 2.05, // Y: table begins below summary.
      w: 8.56, // W: table stays inside safe area.
      rowH: 0.43, // H: each row height; adjust for density.
    };
    const col = {
      category: table.w * 0.3, // W: 30% category column.
      amount: table.w * 0.2, // W: 20% amount column.
      purpose: table.w * 0.5, // W: 50% purpose column.
    };
    const xAmount = table.x + col.category;
    const xPurpose = xAmount + col.amount;

    slide.addShape("rect", {
      x: table.x,
      y: table.y,
      w: table.w,
      h: table.rowH,
      fill: { color: TABLE_HEADER },
      line: { color: TABLE_HEADER, transparency: 100 },
    });
    this.tableHeader(slide, "CATEGORY", { x: table.x + 0.08, y: table.y + 0.08, w: col.category - 0.12, h: 0.24 });
    this.tableHeader(slide, "AMOUNT", { x: xAmount + 0.08, y: table.y + 0.08, w: col.amount - 0.12, h: 0.24 });
    this.tableHeader(slide, "PURPOSE", { x: xPurpose + 0.08, y: table.y + 0.08, w: col.purpose - 0.12, h: 0.24 });

    const rows = data.budgetSlide.budgetBreakdown
      .filter((item) => hasValue(item.category) || hasValue(item.amount) || hasValue(item.purpose))
      .slice(0, 4);

    rows.forEach((item, index) => {
      const y = table.y + table.rowH + index * table.rowH; // Y: row top.
      if (index % 2 === 0) {
        slide.addShape("rect", {
          x: table.x,
          y,
          w: table.w,
          h: table.rowH,
          fill: { color: "FFFFFF", transparency: 92 },
          line: { color: "FFFFFF", transparency: 100 },
        });
      }

      this.tableCell(slide, item.category, { x: table.x + 0.08, y: y + 0.08, w: col.category - 0.12, h: 0.24 }, true);
      this.tableCell(slide, item.amount, { x: xAmount + 0.08, y: y + 0.08, w: col.amount - 0.12, h: 0.24 }, true);
      this.tableCell(slide, item.purpose, { x: xPurpose + 0.08, y: y + 0.08, w: col.purpose - 0.12, h: 0.24 }, false);
    });
  }

  private addTeamSlide(pptx: pptxgen, data: GrantPitchDeckData, bgPath: string): void {
    const slide = this.master(pptx, bgPath);
    this.title(slide, "MEET OUR TEAM");
    this.kicker(slide, "Execution capability");
    this.summary(slide, data.teamSlide.coreTeamCapability, { x: 0.72, y: 1.45, w: 8.45, h: 0.62 });
    this.bullets(slide, data.teamSlide.bulletPoints, { x: 0.82, y: 2.22, w: 8.05, h: 0.8 });
    this.microLabel(slide, "12-MONTH ROADMAP", { x: 0.72, y: 3.28, w: 3.0, h: 0.22 });
    this.bullets(slide, data.teamSlide.roadmap12Months, { x: 0.82, y: 3.58, w: 8.05, h: 0.72 });
  }

  private master(pptx: pptxgen, bgPath: string): pptxgen.Slide {
    const slide = pptx.addSlide();
    slide.background = { color: BG };
    slide.addImage({
      path: bgPath,
      x: 0, // X: background starts at slide edge.
      y: 0, // Y: background starts at slide top.
      w: SLIDE_W, // W: full 10" slide width.
      h: SLIDE_H, // H: full 5.625" slide height.
    });
    return slide;
  }

  private title(slide: pptxgen.Slide, text: string): void {
    slide.addText(text, {
      x: TITLE.x, // X: consistent title left alignment.
      y: TITLE.y, // Y: title baseline near top.
      w: TITLE.w, // W: allows long section labels to wrap.
      h: TITLE.h, // H: enough for one bold uppercase title.
      fontFace: FONT,
      fontSize: 27,
      bold: true,
      color: TEXT,
      align: "left",
      valign: "top",
      wrap: true,
      fit: "shrink",
    });
  }

  private kicker(slide: pptxgen.Slide, text: string): void {
    slide.addText(text.toUpperCase(), {
      x: 0.72, // X: aligns with body content.
      y: 1.18, // Y: small metadata label above body.
      w: 5.2, // W: compact label width.
      h: 0.18, // H: single tiny label line.
      fontFace: FONT,
      fontSize: 8,
      bold: true,
      color: SUBTLE,
      align: "left",
      valign: "top",
      wrap: true,
    });
  }

  private summary(slide: pptxgen.Slide, text: string, box: Box): void {
    slide.addText(safe(text), {
      x: box.x, // X: summary left.
      y: box.y, // Y: summary top.
      w: box.w, // W: summary wrap width.
      h: box.h, // H: capped to protect sunburst.
      fontFace: FONT,
      fontSize: 16,
      bold: true,
      color: TEXT,
      align: "left",
      valign: "top",
      wrap: true,
      fit: "shrink",
    });
  }

  private body(slide: pptxgen.Slide, text: string, box: Box): void {
    slide.addText(safe(text), {
      x: box.x, // X: body text left.
      y: box.y, // Y: body text top.
      w: box.w, // W: body wrapping width.
      h: box.h, // H: body text height.
      fontFace: FONT,
      fontSize: 12,
      color: MUTED,
      align: "left",
      valign: "top",
      wrap: true,
      fit: "shrink",
    });
  }

  private bullets(slide: pptxgen.Slide, items: string[], box: Box): void {
    const lines = cleanList(items).slice(0, 4).map((item) => ({
      text: item,
      options: { bullet: { type: "bullet" as const }, breakLine: true },
    }));
    if (lines.length === 0) {
      this.body(slide, MISSING_PLACEHOLDER, box);
      return;
    }

    slide.addText(lines, {
      x: box.x, // X: bullet block left.
      y: box.y, // Y: bullet block top.
      w: box.w, // W: bullet wrap width.
      h: box.h, // H: bullet block capped above sunburst.
      fontFace: FONT,
      fontSize: 12,
      color: MUTED,
      align: "left",
      valign: "top",
      wrap: true,
      fit: "shrink",
      paraSpaceAfter: 4,
    });
  }

  private microLabel(slide: pptxgen.Slide, text: string, box: Box): void {
    slide.addText(text, {
      x: box.x, // X: small label left.
      y: box.y, // Y: small label top.
      w: box.w, // W: label width.
      h: box.h, // H: label height.
      fontFace: FONT,
      fontSize: 8,
      bold: true,
      color: SUBTLE,
      align: "left",
      valign: "top",
      wrap: true,
      fit: "shrink",
    });
  }

  private metric(slide: pptxgen.Slide, text: string, box: Box): void {
    slide.addText(text, {
      x: box.x, // X: metric value left.
      y: box.y, // Y: metric value top.
      w: box.w, // W: metric column width.
      h: box.h, // H: metric value height.
      fontFace: FONT,
      fontSize: 13,
      bold: true,
      color: TEXT,
      align: "left",
      valign: "top",
      wrap: true,
      fit: "shrink",
    });
  }

  private tableHeader(slide: pptxgen.Slide, text: string, box: Box): void {
    slide.addText(text, {
      x: box.x, // X: header cell left.
      y: box.y, // Y: header cell top.
      w: box.w, // W: header cell width.
      h: box.h, // H: header cell height.
      fontFace: FONT,
      fontSize: 8,
      bold: true,
      color: TABLE_TEXT,
      align: "left",
      valign: "top",
      wrap: true,
      fit: "shrink",
    });
  }

  private tableCell(slide: pptxgen.Slide, text: string, box: Box, bold: boolean): void {
    slide.addText(safe(text), {
      x: box.x, // X: data cell left.
      y: box.y, // Y: data cell top.
      w: box.w, // W: data cell width.
      h: box.h, // H: data cell height.
      fontFace: FONT,
      fontSize: 8.5,
      bold,
      color: MUTED,
      align: "left",
      valign: "top",
      wrap: true,
      fit: "shrink",
    });
  }
}

function hasValue(value: unknown): boolean {
  if (value === null || value === undefined) return false;
  const normalized = String(value).trim().toLowerCase();
  return !MISSING_VALUES.has(normalized);
}

function safe(value: unknown): string {
  return hasValue(value) ? String(value).trim() : MISSING_PLACEHOLDER;
}

function cleanList(items: string[]): string[] {
  return items.filter(hasValue).map((item) => item.trim());
}
