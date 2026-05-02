import { GoogleGenAI, Type } from "@google/genai";

export interface GrantPitchDeckData {
  titleSlide: {
    companyName: string;
    tagline: string;
    requestedGrantAmount: string;
  };
  problemSlide: {
    macroProblem: string;
    specificPainPoint: string;
    bulletPoints: string[];
  };
  solutionSlide: {
    productOrService: string;
    innovativeEdge: string;
    bulletPoints: string[];
  };
  marketSlide: {
    tam: string;
    sam: string;
    som: string;
    currentTraction: string;
    bulletPoints: string[];
  };
  budgetSlide: {
    grantUtilizationSummary: string;
    budgetBreakdown: Array<{
      category: string;
      amount: string;
      purpose: string;
    }>;
  };
  teamSlide: {
    coreTeamCapability: string;
    roadmap12Months: string[];
    bulletPoints: string[];
  };
}

export class GeminiPitchService {
  private readonly apiKeys: string[];
  private readonly model: string;

  constructor(options?: { apiKey?: string; model?: string }) {
    const apiKeys = dedupe(
      [
        options?.apiKey,
        process.env.GOOGLE_API_KEY,
        process.env.GEMINI_API_KEY,
        ...csvEnv("GEMINI_FALLBACK_API_KEYS"),
        ...csvEnv("GOOGLE_FALLBACK_API_KEYS"),
      ].filter(Boolean) as string[],
    );
    
    if (apiKeys.length === 0) {
      throw new Error("GOOGLE_API_KEY or GEMINI_API_KEY is required in your .env file.");
    }

    this.apiKeys = apiKeys;
    this.model = options?.model ?? process.env.GEMINI_MODEL ?? "gemini-2.5-flash";
  }

  async extractPitchDeckData(rawSmeJson: unknown): Promise<GrantPitchDeckData> {
    const systemInstruction = [
      "You are an elite Malaysian government grant writer and pitch strategist.",
      "Convert messy SME business JSON into concise, persuasive, premium corporate pitch-deck content.",
      "Frame the SME as highly fundable, innovative, commercially viable, and execution-ready.",
      "Use concrete numbers when available. Do not invent regulatory claims or fake traction.",
      "Return exactly six grant-committee-optimized slides matching the required JSON schema.",
      "CRITICAL FORMATTING RULES: You are writing content for PowerPoint slides.",
      "Keep it extremely brief.",
      "Bullet points MUST be under 15 words each.",
      "Summaries MUST be under 2 sentences.",
      "NEVER write large paragraphs.",
      "Prioritize punchy, high-impact statements over long explanations.",
      "Taglines should be one short sentence.",
      "Budget purposes should be under 10 words.",
    ].join(" ");

    let lastError: unknown;

    for (const [index, apiKey] of this.apiKeys.entries()) {
      try {
        const ai = new GoogleGenAI({ apiKey });
        const response = await ai.models.generateContent({
          model: this.model,
          contents: [
            {
              role: "user",
              parts: [
                {
                  text: `Raw SME JSON:\n${JSON.stringify(rawSmeJson, null, 2)}`,
                },
              ],
            },
          ],
          config: {
            systemInstruction,
            responseMimeType: "application/json",
            responseSchema: GRANT_PITCH_DECK_SCHEMA,
            temperature: 0.35,
          },
        });

        const text = response.text;
        if (!text) {
          throw new Error("Gemini returned an empty response.");
        }

        const parsed = JSON.parse(text) as unknown;
        return assertGrantPitchDeckData(parsed);
      } catch (error) {
        lastError = error;
        if (index < this.apiKeys.length - 1) {
          console.warn(
            `Gemini pitch extraction failed with key ${index + 1}/${this.apiKeys.length}; trying next key.`,
          );
        }
      }
    }

    const message = lastError instanceof Error ? lastError.message : String(lastError);
    throw new Error(`Gemini pitch extraction failed across all configured keys: ${message}`);
  }
}

const stringArraySchema = {
  type: Type.ARRAY,
  items: { type: Type.STRING },
} as const;

const GRANT_PITCH_DECK_SCHEMA = {
  type: Type.OBJECT,
  properties: {
    titleSlide: {
      type: Type.OBJECT,
      properties: {
        companyName: { type: Type.STRING },
        tagline: { type: Type.STRING },
        requestedGrantAmount: { type: Type.STRING },
      },
      required: ["companyName", "tagline", "requestedGrantAmount"],
    },
    problemSlide: {
      type: Type.OBJECT,
      properties: {
        macroProblem: { type: Type.STRING },
        specificPainPoint: { type: Type.STRING },
        bulletPoints: stringArraySchema,
      },
      required: ["macroProblem", "specificPainPoint", "bulletPoints"],
    },
    solutionSlide: {
      type: Type.OBJECT,
      properties: {
        productOrService: { type: Type.STRING },
        innovativeEdge: { type: Type.STRING },
        bulletPoints: stringArraySchema,
      },
      required: ["productOrService", "innovativeEdge", "bulletPoints"],
    },
    marketSlide: {
      type: Type.OBJECT,
      properties: {
        tam: { type: Type.STRING },
        sam: { type: Type.STRING },
        som: { type: Type.STRING },
        currentTraction: { type: Type.STRING },
        bulletPoints: stringArraySchema,
      },
      required: ["tam", "sam", "som", "currentTraction", "bulletPoints"],
    },
    budgetSlide: {
      type: Type.OBJECT,
      properties: {
        grantUtilizationSummary: { type: Type.STRING },
        budgetBreakdown: {
          type: Type.ARRAY,
          items: {
            type: Type.OBJECT,
            properties: {
              category: { type: Type.STRING },
              amount: { type: Type.STRING },
              purpose: { type: Type.STRING },
            },
            required: ["category", "amount", "purpose"],
          },
        },
      },
      required: ["grantUtilizationSummary", "budgetBreakdown"],
    },
    teamSlide: {
      type: Type.OBJECT,
      properties: {
        coreTeamCapability: { type: Type.STRING },
        roadmap12Months: stringArraySchema,
        bulletPoints: stringArraySchema,
      },
      required: ["coreTeamCapability", "roadmap12Months", "bulletPoints"],
    },
  },
  required: [
    "titleSlide",
    "problemSlide",
    "solutionSlide",
    "marketSlide",
    "budgetSlide",
    "teamSlide",
  ],
} as const;

function assertGrantPitchDeckData(value: unknown): GrantPitchDeckData {
  if (!isRecord(value)) {
    throw new Error("AI output is not a JSON object.");
  }

  const requiredSlides = [
    "titleSlide",
    "problemSlide",
    "solutionSlide",
    "marketSlide",
    "budgetSlide",
    "teamSlide",
  ];

  for (const slide of requiredSlides) {
    if (!isRecord(value[slide])) {
      throw new Error(`AI output is missing ${slide}.`);
    }
  }

  return value as unknown as GrantPitchDeckData;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function csvEnv(name: string): string[] {
  const value = process.env[name];
  if (!value) return [];
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function dedupe(values: string[]): string[] {
  return [...new Set(values)];
}
