import { useEffect, useMemo, useRef, useState } from "react";
import { createRoll, generate } from "./api";
import type { ChatMessage, ChatTurn, Conversation, ProviderConfig, RollItem } from "./types";

const STORAGE_KEY = "ai-gamblecore:conversations:v1";
const MAX_SAVED_CONVERSATIONS = 20;
const MAX_SAVED_TURNS = 30;

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

function createId(): string {
  return crypto.randomUUID();
}

function loadConversations(): Conversation[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed: unknown = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed
      .filter((item): item is Conversation => (
        typeof item === "object" && item !== null
        && typeof (item as Conversation).id === "string"
        && typeof (item as Conversation).title === "string"
        && Array.isArray((item as Conversation).turns)
        && typeof (item as Conversation).createdAt === "string"
        && typeof (item as Conversation).updatedAt === "string"
      ))
      .sort((a, b) => b.updatedAt.localeCompare(a.updatedAt))
      .slice(0, MAX_SAVED_CONVERSATIONS);
  } catch {
    return [];
  }
}

function conversationTitle(prompt: string): string {
  const compact = prompt.replace(/\s+/g, " ").trim();
  return compact.length > 52 ? `${compact.slice(0, 49)}…` : compact;
}

function formatSavedDate(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "недавно";
  return new Intl.DateTimeFormat("ru-RU", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

function App() {
  const initialChatState = useRef<{ conversations: Conversation[]; activeId: string } | null>(null);
  if (!initialChatState.current) {
    const saved = loadConversations();
    initialChatState.current = { conversations: saved, activeId: saved[0]?.id ?? createId() };
  }
  const [prompt, setPrompt] = useState("");
  const [demo, setDemo] = useState(true);
  const [provider, setProvider] = useState(DEFAULT_PROVIDER);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [adultMode, setAdultMode] = useState(false);
  const [allowTokenBurn, setAllowTokenBurn] = useState(false);
  const [rolls, setRolls] = useState<RollItem[]>(EMPTY_REELS);
  const [revealed, setRevealed] = useState(0);
  const [conversations, setConversations] = useState<Conversation[]>(initialChatState.current.conversations);
  const [activeConversationId, setActiveConversationId] = useState(initialChatState.current.activeId);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [storageWarning, setStorageWarning] = useState("");
  const [pendingPrompt, setPendingPrompt] = useState("");
  const [status, setStatus] = useState<"idle" | "rolling" | "generating">("idle");
  const [error, setError] = useState("");
  const chatEndRef = useRef<HTMLDivElement>(null);
  const activeConversation = conversations.find((conversation) => conversation.id === activeConversationId);
  const turns = activeConversation?.turns ?? [];

  const canPlay = prompt.trim().length >= 3 && status === "idle" && (demo || provider.api_key.length > 0);
  const buttonText = useMemo(() => {
    if (status === "rolling") return "БАРАБАНЫ КРУТЯТСЯ";
    if (status === "generating") return "МОДЕЛЬ ВЫЖИВАЕТ";
    return "ОТПРАВИТЬ";
  }, [status]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [turns, pendingPrompt, status]);

  useEffect(() => {
    try {
      if (conversations.length === 0) {
        localStorage.removeItem(STORAGE_KEY);
      } else {
        const snapshot = conversations.slice(0, MAX_SAVED_CONVERSATIONS).map((conversation) => ({
          ...conversation,
          turns: conversation.turns.slice(-MAX_SAVED_TURNS),
        }));
        localStorage.setItem(STORAGE_KEY, JSON.stringify(snapshot));
      }
      setStorageWarning("");
    } catch {
      setStorageWarning("Хранилище браузера заполнено — новые ходы могут не сохраниться.");
    }
  }, [conversations]);

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
      const turn: ChatTurn = { id: createId(), prompt: currentPrompt, result: generation };
      const now = new Date().toISOString();
      setConversations((current) => {
        const existing = current.find((conversation) => conversation.id === activeConversationId);
        const updated: Conversation = existing
          ? { ...existing, turns: [...existing.turns, turn], updatedAt: now }
          : {
              id: activeConversationId,
              title: conversationTitle(currentPrompt),
              turns: [turn],
              createdAt: now,
              updatedAt: now,
            };
        return [updated, ...current.filter((conversation) => conversation.id !== activeConversationId)]
          .slice(0, MAX_SAVED_CONVERSATIONS);
      });
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
    setActiveConversationId(createId());
    setPrompt("");
    setError("");
    setRolls(EMPTY_REELS);
    setRevealed(0);
    setHistoryOpen(false);
  }

  function selectConversation(conversation: Conversation) {
    if (status !== "idle") return;
    const lastTurn = conversation.turns.at(-1);
    setActiveConversationId(conversation.id);
    setPrompt("");
    setError("");
    setRolls(lastTurn?.result.rolls ?? EMPTY_REELS);
    setRevealed(lastTurn?.result.rolls.length ?? 0);
    setHistoryOpen(false);
  }

  function deleteConversation(id: string) {
    if (status !== "idle" || !window.confirm("Удалить этот диалог без возможности восстановления?")) return;
    const remaining = conversations.filter((conversation) => conversation.id !== id);
    setConversations(remaining);
    if (id === activeConversationId) {
      const next = remaining[0];
      setActiveConversationId(next?.id ?? createId());
      setRolls(next?.turns.at(-1)?.result.rolls ?? EMPTY_REELS);
      setRevealed(next?.turns.at(-1)?.result.rolls.length ?? 0);
      setPrompt("");
      setError("");
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
          <button className="icon-button" onClick={() => setHistoryOpen(!historyOpen)} aria-expanded={historyOpen}>
            <span aria-hidden="true">▤</span><span className="desktop-label"> ИСТОРИЯ · {conversations.length}</span>
          </button>
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

        {historyOpen && (
          <section className="history-panel" aria-label="Сохранённые диалоги">
            <header>
              <div><span>АРХИВ СТОЛА</span><small>Хранится только в этом браузере</small></div>
              <button onClick={resetConversation} disabled={status !== "idle"}>+ НОВЫЙ ДИАЛОГ</button>
            </header>
            {conversations.length === 0 ? (
              <p className="history-empty">Здесь появятся завершённые ходы. Они переживут перезагрузку страницы.</p>
            ) : (
              <div className="history-list">
                {conversations.map((conversation) => (
                  <article className={conversation.id === activeConversationId ? "active" : ""} key={conversation.id}>
                    <button className="history-select" onClick={() => selectConversation(conversation)} disabled={status !== "idle"}>
                      <strong>{conversation.title}</strong>
                      <span>{conversation.turns.length} ходов · {formatSavedDate(conversation.updatedAt)}</span>
                    </button>
                    <button className="history-delete" onClick={() => deleteConversation(conversation.id)} disabled={status !== "idle"} aria-label={`Удалить диалог «${conversation.title}»`}>×</button>
                  </article>
                ))}
              </div>
            )}
          </section>
        )}

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
        {storageWarning && <div className="storage-warning" role="status">{storageWarning}</div>}
      </section>

      <footer><span>18+ ЭМОЦИОНАЛЬНО</span><span>ДЕНЬГИ НЕ ПРИНИМАЕМ · СМЫСЛ НЕ ВОЗВРАЩАЕМ</span></footer>
    </main>
  );
}

export default App;
