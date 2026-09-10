import { useEffect, useMemo, useRef, useState } from "react";
import { createRoll, generate } from "./api";
import type { ChatMessage, ChatTurn, ProviderConfig, RollItem } from "./types";

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
  const [adultMode, setAdultMode] = useState(false);
  const [allowTokenBurn, setAllowTokenBurn] = useState(false);
  const [rolls, setRolls] = useState<RollItem[]>(EMPTY_REELS);
  const [revealed, setRevealed] = useState(0);
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [pendingPrompt, setPendingPrompt] = useState("");
  const [status, setStatus] = useState<"idle" | "rolling" | "generating">("idle");
  const [error, setError] = useState("");
  const chatEndRef = useRef<HTMLDivElement>(null);

  const canPlay = prompt.trim().length >= 3 && status === "idle" && (demo || provider.api_key.length > 0);
  const buttonText = useMemo(() => {
    if (status === "rolling") return "БАРАБАНЫ КРУТЯТСЯ";
    if (status === "generating") return "МОДЕЛЬ ВЫЖИВАЕТ";
    return "ОТПРАВИТЬ";
  }, [status]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [turns, pendingPrompt, status]);

  async function play() {
    if (!canPlay) return;
    const currentPrompt = prompt.trim();
    const history: ChatMessage[] = turns.slice(-10).flatMap((turn) => [
      { role: "user" as const, content: turn.prompt },
      ...(turn.result.burned ? [] : [{ role: "assistant" as const, content: turn.result.answer }]),
    ]);
    setError("");
    setPendingPrompt(currentPrompt);
    setPrompt("");
    setRevealed(0);
    setRolls(EMPTY_REELS);
    setStatus("rolling");

    try {
      const roll = await createRoll(adultMode, allowTokenBurn);
      setRolls(roll.rolls);
      for (let index = 1; index <= roll.rolls.length; index += 1) {
        await new Promise((resolve) => window.setTimeout(resolve, 310));
        setRevealed(index);
      }
      setStatus("generating");
      const generation = await generate(currentPrompt, roll.roll_id, demo, provider, history);
      setTurns((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          prompt: currentPrompt,
          result: generation,
        },
      ]);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Что-то пошло не так");
      setPrompt(currentPrompt);
    } finally {
      setPendingPrompt("");
      setStatus("idle");
    }
  }

  function resetConversation() {
    if (status !== "idle") return;
    setTurns([]);
    setPrompt("");
    setError("");
    setRolls(EMPTY_REELS);
    setRevealed(0);
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
            <div className="risk-controls">
              <label className={`risk-toggle ${adultMode ? "enabled adult" : ""}`}>
                <input type="checkbox" checked={adultMode} onChange={(event) => setAdultMode(event.target.checked)} />
                <span className="toggle-track"><span /></span>
                <span><strong>18+ РЕЖИМ</strong><small>Мат, чёрный юмор и жёсткая подача</small></span>
              </label>
              <label className={`risk-toggle ${allowTokenBurn ? "enabled burn" : ""}`}>
                <input type="checkbox" checked={allowTokenBurn} onChange={(event) => setAllowTokenBurn(event.target.checked)} />
                <span className="toggle-track"><span /></span>
                <span><strong>ПУСТОЙ ПРОКРУТ</strong><small>{demo ? "В demo только симуляция" : "Ответ модели может быть удалён после оплаты токенов"}</small></span>
              </label>
            </div>
            <p>Ключ существует только в памяти вкладки. Опасные исходы включаются только вручную.</p>
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

          <section className="chat-panel" aria-label="Диалог с моделью">
            <header className="chat-head">
              <div>
                <span>ДИАЛОГОВЫЙ СТОЛ</span>
                <small>Каждое сообщение получает новый набор эффектов</small>
              </div>
              <div className="chat-head-actions">
                <span className="context-count">КОНТЕКСТ: {Math.min(turns.length * 2, 20)} / 20</span>
                {turns.length > 0 && <button onClick={resetConversation} disabled={status !== "idle"}>НОВЫЙ ДИАЛОГ</button>}
              </div>
            </header>

            <div className="conversation" aria-live="polite">
              {turns.length === 0 && !pendingPrompt && (
                <div className="chat-empty">
                  <span className="empty-orb">AG</span>
                  <div><strong>СТОЛ ЖДЁТ ПЕРВОЙ СТАВКИ</strong><p>Напиши сообщение. Перед каждым ответом барабаны заново выберут судьбу модели.</p></div>
                </div>
              )}

              {turns.map((turn, turnIndex) => (
                <div className="chat-turn" key={turn.id}>
                  <div className="message user-message">
                    <span className="message-role">ВЫ · ХОД {String(turnIndex + 1).padStart(2, "0")}</span>
                    <p>{turn.prompt}</p>
                  </div>
                  <div className={`message assistant-message ${turn.result.burned ? "burned-message" : ""}`}>
                    <div className="message-meta">
                      <span className="message-role">МОДЕЛЬ · ВЫПАДЕНИЕ</span>
                      <div className="effect-chips">
                        {turn.result.rolls.map((roll) => <span className={roll.rarity} key={roll.category}>{roll.label}</span>)}
                      </div>
                    </div>
                    {turn.result.burned ? (
                      <div className="burned-result compact">
                        <span className="burned-icon" aria-hidden="true">×</span>
                        <div><strong>ОТВЕТ СГОРЕЛ</strong><p>{turn.result.demo ? "Demo-симуляция: токены не потрачены." : "Ответ был создан и удалён. Токены списаны."}</p></div>
                      </div>
                    ) : (
                      <div className="message-answer">{turn.result.answer}</div>
                    )}
                    {(turn.result.translations.length > 0 || turn.result.final_prompt) && (
                      <details className="turn-details">
                        <summary>РАЗОБРАТЬ ЭТОТ ХОД</summary>
                        {turn.result.translations.map((step, index) => (
                          <div className="translation-step" key={`${step.language}-${index}`}>
                            <span>{String(index + 1).padStart(2, "0")} / {step.language}</span><p>{step.text}</p>
                          </div>
                        ))}
                        <pre>{turn.result.final_prompt}</pre>
                      </details>
                    )}
                  </div>
                </div>
              ))}

              {pendingPrompt && (
                <div className="chat-turn pending-turn">
                  <div className="message user-message"><span className="message-role">ВЫ · НОВЫЙ ХОД</span><p>{pendingPrompt}</p></div>
                  <div className="message assistant-message typing-message">
                    <span className="message-role">{status === "rolling" ? "СТОЛ ВЫБИРАЕТ ЭФФЕКТЫ" : "МОДЕЛЬ ПЕЧАТАЕТ"}</span>
                    <span className="typing-dots"><i /><i /><i /></span>
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            <div className="chat-composer">
              <div className="prompt-box">
                <textarea
                  id="prompt"
                  value={prompt}
                  onChange={(event) => setPrompt(event.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" && !event.shiftKey) {
                      event.preventDefault();
                      void play();
                    }
                  }}
                  placeholder={turns.length ? "Продолжи диалог..." : "Напиши то, что боишься доверить случаю..."}
                  maxLength={10000}
                  disabled={status !== "idle"}
                />
                <span className="counter">ENTER — ОТПРАВИТЬ · SHIFT+ENTER — СТРОКА · {prompt.length} / 10 000</span>
              </div>
              <button className="pull-button" disabled={!canPlay} onClick={play}>
                <span className="button-glare" />
                <span className="button-main">{buttonText}</span>
                <span className="button-sub">НОВЫЙ РОЛЛ · {demo ? "DEMO" : "LIVE API"}</span>
              </button>
            </div>
          </section>
        </section>

        {error && <div className="error-message" role="alert">ОШИБКА СТОЛА: {error}</div>}
      </section>

      <footer><span>18+ ЭМОЦИОНАЛЬНО</span><span>ДЕНЬГИ НЕ ПРИНИМАЕМ · СМЫСЛ НЕ ВОЗВРАЩАЕМ</span></footer>
    </main>
  );
}

export default App;
