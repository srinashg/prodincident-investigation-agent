"use client";

import { FormEvent, useState } from "react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type Evidence = {
  id: string;
  source: string;
  summary: string;
};

type ToolStep = {
  tool: string;
  status: string;
  detail: string;
};

type IncidentReport = {
  investigation_id: string;
  symptom: string;
  service: string;
  likely_cause: string;
  confidence: number;
  evidence: Evidence[];
  tool_timeline: ToolStep[];
  recommended_next_checks: string[];
};

type EvaluationResult = {
  scenario_id: string;
  passed: boolean;
  root_cause_match: boolean;
  required_evidence_found: boolean;
  score: number;
  report: IncidentReport;
};

async function readJson(response: Response) {
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.detail ?? "Request failed");
  }
  return payload;
}

export default function Home() {
  const [symptom, setSymptom] = useState("Checkout latency increased to about 4 seconds");
  const [report, setReport] = useState<IncidentReport | null>(null);
  const [evaluation, setEvaluation] = useState<EvaluationResult | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submitInvestigation(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setEvaluation(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/investigations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          symptom,
          service: "checkout",
          time_window_minutes: 5,
        }),
      });
      setReport(await readJson(response));
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  async function evaluateKnownScenario() {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_BASE_URL}/api/evaluations/high-latency`, {
        method: "POST",
      });
      const result = (await readJson(response)) as EvaluationResult;
      setEvaluation(result);
      setReport(result.report);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="container">
      <header>
        <p className="eyebrow">Local MVP</p>
        <h1>Production Incident Investigation Console</h1>
        <p className="intro">
          Investigate the checkout service using local telemetry, recent changes, and a troubleshooting runbook.
        </p>
      </header>

      <section className="card">
        <h2>Start an investigation</h2>
        <form onSubmit={submitInvestigation}>
          <label htmlFor="symptom">Incident symptom</label>
          <textarea
            id="symptom"
            value={symptom}
            onChange={(event) => setSymptom(event.target.value)}
            rows={3}
          />
          <div className="actions">
            <button disabled={loading} type="submit">
              {loading ? "Working..." : "Investigate current telemetry"}
            </button>
            <button disabled={loading} type="button" className="secondary" onClick={evaluateKnownScenario}>
              Evaluate known high-latency scenario
            </button>
          </div>
        </form>
        {error && <p className="error">{error}</p>}
      </section>

      {evaluation && (
        <section className="card">
          <h2>Evaluation</h2>
          <div className="metricGrid">
            <div><strong>{evaluation.passed ? "PASS" : "FAIL"}</strong><span>Overall</span></div>
            <div><strong>{Math.round(evaluation.score * 100)}%</strong><span>Score</span></div>
            <div><strong>{evaluation.root_cause_match ? "Yes" : "No"}</strong><span>Root cause match</span></div>
            <div><strong>{evaluation.required_evidence_found ? "Yes" : "No"}</strong><span>Required evidence</span></div>
          </div>
        </section>
      )}

      {report && (
        <section className="card">
          <h2>Incident report</h2>
          <p><strong>Likely cause:</strong> {report.likely_cause}</p>
          <p><strong>Confidence:</strong> {Math.round(report.confidence * 100)}%</p>

          <h3>Evidence</h3>
          <ul>
            {report.evidence.map((item) => (
              <li key={item.id}><strong>{item.source}:</strong> {item.summary}</li>
            ))}
          </ul>

          <h3>Tool timeline</h3>
          <ol>
            {report.tool_timeline.map((step, index) => (
              <li key={`${step.tool}-${index}`}><strong>{step.tool}</strong> — {step.detail}</li>
            ))}
          </ol>

          <h3>Recommended next checks</h3>
          <ul>
            {report.recommended_next_checks.map((check) => <li key={check}>{check}</li>)}
          </ul>
        </section>
      )}
    </main>
  );
}
