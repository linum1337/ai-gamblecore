import { useMemo, useState } from "react";
import { createRoll, generate } from "./api";
import type { GenerateResponse, ProviderConfig, RollItem } from "./types";

const CATEGORY_META: Record<string, { icon: string; title: string }> = {
  translation: { icon: "文", title: "Перевод" },
  quality: { icon: "◆", title: "Качество" },
  style: { icon: "✦", title: "Стиль" },
  format: { icon: "▦", title: "Формат" },
  language: { icon: "あ", title: "Язык" },
  chaos: { icon: "⚡", title: "Мутация" },
};

const EMPTY_REELS = Object.keys(CATEGORY_META).map((category) => ({
  category,
  label: "???",
  value: "",
  rarity: "common" as const,
}));

const DEFAULT_PROVIDER: ProviderConfig = {
  base_url: "https://api.openai.com/v1",
  model: "gpt-4.1-mini",
  api_key: "",
};

function effectClassForRoll(roll: RollItem): string {
  const safeValue = roll.value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  return `effect-${roll.category}-${safeValue}`;
}

function App() {
  const [prompt, setPrompt] = useState("");
  const [demo, setDemo] = useState(true);
  const [provider, setProvider] = useState(DEFAULT_PROVIDER);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [rolls, setRolls] = useState<RollItem[]>(EMPTY_REELS);
  const [revealed, setRevealed] = useState(0);
  const [result, setResult] = useState<GenerateResponse | null>(null);
  const [status, setStatus] = useState<"idle" | "rolling" | "generating">("idle");
  const [error, setError] = useState("");

  const canPlay = prompt.trim().length >= 3 && status === "idle" && (demo || provider.api_key.length > 0);
  const buttonText = useMemo(() => {
    if (status === "rolling") return "БАРАБАНЫ КРУТЯТСЯ";
    if (status === "generating") return "МОДЕЛЬ ВЫЖИВАЕТ";
    return "КРУТИТЬ";
  }, [status]);

  async function play() {
    if (!canPlay) return;
    setError("");
    setResult(null);
    setRevealed(0);
    setRolls(EMPTY_REELS);
    setStatus("rolling");

    try {
      const roll = await createRoll();
      setRolls(roll.rolls);
      for (let index = 1; index <= roll.rolls.length; index += 1) {
        await new Promise((resolve) => window.setTimeout(resolve, 310));
        setRevealed(index);
      }
      setStatus("generating");
      const generation = await generate(prompt.trim(), roll.roll_id, demo, provider);
      setResult(generation);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Что-то пошло не так");
    } finally {
      setStatus("idle");
    }
  }

  function updateProvider(field: keyof ProviderConfig, value: string) {
    setProvider((current) => ({ ...current, [field]: value }));
  }

  return (
    <main className="app-shell">
      <div className="noise" aria-hidden="true" />
      <header className="topbar">
        <a className="brand" href="#play" aria-label="AI Gamblecore — начало">
          <span className="brand-mark">AG</span>
          <span>AI GAMBLECORE</span>
        </a>
        <div className="topbar-actions">
          <span className={`connection ${demo ? "demo" : "live"}`}>
            <span className="connection-dot" /> {demo ? "DEMO" : "LIVE"}
          </span>
          <button className="icon-button" onClick={() => setSettingsOpen(!settingsOpen)} aria-expanded={settingsOpen}>
            <span aria-hidden="true">⚙</span><span className="desktop-label"> МОДЕЛЬ</span>
          </button>
        </div>
      </header>

      <section className="game-layout" id="play">
        <div className="intro-strip">
          <span className="eyebrow">НЕЙРОСЕТЬ РЕШАЕТ. СЛУЧАЙ РЕШАЕТ БОЛЬШЕ.</span>
          <span className="odds">6 НЕЗАВИСИМЫХ РОЛЛОВ</span>
        </div>

        {settingsOpen && (
          <section className="settings-panel" aria-label="Настройки модели">
            <div className="mode-switch" role="group" aria-label="Режим генерации">
              <button className={demo ? "active" : ""} onClick={() => setDemo(true)}>DEMO</button>
              <button className={!demo ? "active" : ""} onClick={() => setDemo(false)}>LIVE API</button>
            </div>
            {!demo && (
              <div className="provider-grid">
                <label>API URL<input value={provider.base_url} onChange={(e) => updateProvider("base_url", e.target.value)} /></label>
                <label>Модель<input value={provider.model} onChange={(e) => updateProvider("model", e.target.value)} /></label>
                <label>API-ключ<input type="password" autoComplete="off" value={provider.api_key} onChange={(e) => updateProvider("api_key", e.target.value)} placeholder="sk-..." /></label>
              </div>
            )}
            <p>Ключ существует только в памяти этой вкладки и не сохраняется.</p>
          </section>
        )}

        <section className={`machine ${status === "rolling" ? "is-rolling" : ""}`}>
          <div className="machine-head">
            <div>
              <span className="machine-kicker">PROMPT MUTATION UNIT</span>
              <h1>СДЕЛАЙ СТАВКУ<br /><i>НА СМЫСЛ</i></h1>
            </div>
            <div className="jackpot">
              <small>ДЖЕКПОТ</small>
              <strong>ЧИСТЫЙ ПРОМПТ</strong>
              <span>ШАНС 0.08%</span>
            </div>
          </div>

          <div className="reels" aria-live="polite">
            {rolls.map((roll, index) => {
              const meta = CATEGORY_META[roll.category];
              const visible = index < revealed;
              return (
                <article
                  className={`reel ${visible ? `revealed ${roll.rarity} ${effectClassForRoll(roll)}` : "spinning"}`}
                  key={roll.category}
                >
                  <div className="reel-label"><span>{meta.icon}</span>{meta.title}</div>
                  <div className="reel-window">
                    <span className="effect-layer" aria-hidden="true" />
                    <div className="reel-value">{visible ? roll.label : "???"}</div>
                    {visible && <span className="rarity">{roll.rarity}</span>}
                  </div>
                </article>
              );
            })}
          </div>

          <div className="prompt-zone">
            <label htmlFor="prompt">ВАШ ПРОМПТ</label>
            <div className="prompt-box">
              <textarea
                id="prompt"
                value={prompt}
                onChange={(event) => setPrompt(event.target.value)}
                placeholder="Напиши то, что боишься доверить случаю..."
                maxLength={10000}
                disabled={status !== "idle"}
              />
              <span className="counter">{prompt.length} / 10 000</span>
            </div>
            <button className="pull-button" disabled={!canPlay} onClick={play}>
              <span className="button-glare" />
              <span className="button-main">{buttonText}</span>
              <span className="button-sub">{demo ? "БЕСПЛАТНАЯ ПОПЫТКА" : "ЗАПРОС К ВАШЕЙ МОДЕЛИ"}</span>
            </button>
          </div>
        </section>

        {error && <div className="error-message" role="alert">ОШИБКА СТОЛА: {error}</div>}

        {result && (
          <section className="result-panel">
            <div className="result-head">
              <span>РЕЗУЛЬТАТ РАУНДА</span>
              <span className="ticket">#{Date.now().toString(36).toUpperCase()}</span>
            </div>
            {result.translations.length > 0 && (
              <details className="transcript">
                <summary>ЦЕПОЧКА ПЕРЕВОДОВ · {result.translations.length}</summary>
                {result.translations.map((step, index) => (
                  <div className="translation-step" key={`${step.language}-${index}`}>
                    <span>{String(index + 1).padStart(2, "0")} / {step.language}</span>
                    <p>{step.text}</p>
                  </div>
                ))}
              </details>
            )}
            <div className="answer"><p>{result.answer}</p></div>
            <details className="transcript final-prompt">
              <summary>ПОКАЗАТЬ ИТОГОВЫЙ ПРОМПТ</summary>
              <pre>{result.final_prompt}</pre>
            </details>
          </section>
        )}
      </section>

      <footer><span>18+ ЭМОЦИОНАЛЬНО</span><span>ДЕНЬГИ НЕ ПРИНИМАЕМ · СМЫСЛ НЕ ВОЗВРАЩАЕМ</span></footer>
    </main>
  );
}

export default App;
