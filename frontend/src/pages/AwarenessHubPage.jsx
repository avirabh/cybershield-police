import React, { useEffect, useState } from "react";
import { GraduationCap, Send, ShieldCheck } from "lucide-react";
import { api } from "../api.js";
import { getStoredUser } from "../auth.js";
import LoadingState from "../components/LoadingState.jsx";
import LanguageSelector from "../components/LanguageSelector.jsx";
import { useLanguage } from "../i18n/LanguageContext.jsx";

export default function AwarenessHubPage() {
  const { t } = useLanguage();
  const user = getStoredUser();
  const [quiz, setQuiz] = useState(null);
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);

  useEffect(() => {
    api.getQuiz().then(setQuiz).catch(() => setQuiz({ questions: [] }));
  }, []);

  async function submit() {
    setResult(await api.submitQuiz({ user_email: user?.email || "citizen@example.com", answers }));
  }

  if (!quiz) return <LoadingState label={`${t("common.loading")} awareness quiz`} />;

  const tips = t("awareness.tips");
  const content = t("awareness.content");

  return (
    <section className="page-stack">
      <div className="page-heading">
        <div className="heading-with-control">
          <span className="eyebrow">{t("awareness.eyebrow")}</span>
          <LanguageSelector compact />
        </div>
        <h1>{t("awareness.title")}</h1>
        <p>{t("awareness.subtitle")}</p>
      </div>
      <div className="role-action-grid">
        {(Array.isArray(tips) ? tips : []).map((tip) => (
          <article className="role-action-card" key={tip}><ShieldCheck size={22} /><strong>{tip}</strong><span>{t("citizen.cyberDostText")}</span></article>
        ))}
      </div>
      <section className="panel">
        <div className="panel-heading"><h2>{t("awareness.title")}</h2><span>{t("common.safeData")}</span></div>
        <div className="awareness-content-grid">
          {(Array.isArray(content) ? content : []).map(([title, body]) => (
            <article className="awareness-card" key={title}>
              <ShieldCheck size={19} />
              <strong>{title}</strong>
              <p>{body}</p>
            </article>
          ))}
        </div>
      </section>
      <section className="panel">
        <div className="panel-heading"><h2>{t("awareness.quiz")}</h2><span>{t("awareness.quizSub")}</span></div>
        <div className="quiz-stack">
          {quiz.questions.map((question) => (
            <div className="quiz-card" key={question.id}>
              <strong>{question.question}</strong>
              <div className="quiz-options">
                {question.options.map((option) => (
                  <label key={option}><input type="radio" name={question.id} value={option} onChange={() => setAnswers((current) => ({ ...current, [question.id]: option }))} />{option}</label>
                ))}
              </div>
            </div>
          ))}
        </div>
        <button className="button button-primary" type="button" onClick={submit}><Send size={18} /> {t("awareness.submitQuiz")}</button>
        {result && <div className="success-banner"><GraduationCap size={18} /> Score: {result.score}/{result.total} - {result.message}</div>}
      </section>
    </section>
  );
}
