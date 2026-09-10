export type Rarity = "common" | "rare" | "epic" | "legendary";

export interface RollItem {
  category: string;
  label: string;
  value: string;
  rarity: Rarity;
}

export interface RollResponse {
  roll_id: string;
  expires_in: number;
  rolls: RollItem[];
}

export interface TranslationStep {
  language: string;
  text: string;
}

export interface GenerateResponse {
  answer: string;
  final_prompt: string;
  rolls: RollItem[];
  translations: TranslationStep[];
  demo: boolean;
  burned: boolean;
}

export interface ProviderConfig {
  base_url: string;
  model: string;
  api_key: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatTurn {
  id: string;
  prompt: string;
  result: GenerateResponse;
}
