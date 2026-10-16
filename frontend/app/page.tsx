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
  const [simulatedLatencySeconds, setSimulatedLatencySeconds] = useState(4);
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
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          latency_seconds: simulatedLatencySeconds,
        }),
      });
      const result = (await readJson(response)) as EvaluationResult;
      setEvaluation(result);
      setReport(result.report);
      setSymptom(result.report.symptom);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="container">
      <header>
        <h1>Production Incident Investigation Console</h1>
        <p className="intro">
          Describe a production symptom, then let the investigator collect telemetry,
          recent changes, and troubleshooting guidance to identify a likely cause.
        </p>
      </header>

      <section className="card guideCard" aria-labelledby="how-to-use">
        <h2 id="how-to-use">What you do here</h2>
        <div className="steps">
          <div className="step">
            <span className="stepNumber">1</span>
            <div>
              <strong>Describe the symptom</strong>
              <p>Enter what you are observing, such as checkout requests taking about 4 seconds.</p>
            </div>
          </div>
          <div className="step">
            <span className="stepNumber">2</span>
            <div>
              <strong>Run the investigation</strong>
              <p>The system checks the available telemetry, recent changes, and troubleshooting knowledge.</p>
            </div>
          </div>
          <div className="step">
            <span className="stepNumber">3</span>
            <div>
              <strong>Review the diagnosis</strong>
              <p>Use the evidence, likely cause, confidence, and next checks to understand what may have failed.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="card">
        <h2>Start an investigation</h2>
        <p className="sectionHelp">
          Enter the incident symptom below. Use <strong>Investigate current telemetry</strong> when
          you want to analyze whatever data is already in the simulator.
        </p>

        <form onSubmit={submitInvestigation}>
          <label htmlFor="symptom">What problem are you seeing?</label>
          <textarea
            id="symptom"
            value={symptom}
            onChange={(event) => setSymptom(event.target.value)}
            rows={3}
            placeholder="Example: Checkout requests are taking about 4 seconds"
          />

          <div className="actionGrid">
            <div className="actionOption">
              <button disabled={loading} type="submit">
                {loading ? "Working..." : "Investigate current telemetry"}
              </button>
              <p>
                Analyze the telemetry and changes that currently exist in the checkout simulator.
              </p>
            </div>

            <div className="actionOption">
              <label className="inlineLabel" htmlFor="simulated-latency">
                Simulated checkout latency (seconds)
              </label>
              <input
                id="simulated-latency"
                type="number"
                min="0.1"
                max="60"
                step="0.1"
                value={simulatedLatencySeconds}
                onChange={(event) =>
                  setSimulatedLatencySeconds(Number(event.target.value))
                }
              />
              <button
                disabled={loading || simulatedLatencySeconds <= 0 || simulatedLatencySeconds > 60}
                type="button"
                className="secondary"
                onClick={evaluateKnownScenario}
              >
                Run simulated latency scenario
              </button>
              <p>
                Choose a latency in seconds. The simulator converts it to milliseconds,
                generates matching telemetry and a recent configuration change, then runs
                the investigation against that evidence.
              </p>
            </div>
          </div>
        </form>

        {error && <p className="error">{error}</p>}
      </section>

      {evaluation && (
        <section className="card">
          <h2>Evaluation</h2>
          <p className="sectionHelp">
            This checks the investigation against the known answer for the simulated scenario.
          </p>
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
