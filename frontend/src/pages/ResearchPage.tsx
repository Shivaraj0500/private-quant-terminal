import {
  BookOpen,
  CheckCircle2,
  ClipboardList,
  FileSearch,
  Search,
  ShieldCheck,
} from "lucide-react";

const researchItems = [
  {
    title: "NIFTY 50 Momentum Research",
    description:
      "Evidence review of momentum persistence across multiple market conditions.",
    status: "Validated",
    confidence: "High",
    updated: "Today",
  },
  {
    title: "Banking Sector Relative Strength",
    description:
      "Researching sector rotation and relative performance signals.",
    status: "In Progress",
    confidence: "Medium",
    updated: "Today",
  },
  {
    title: "Mean Reversion Behaviour Study",
    description:
      "Testing price deviation behaviour across different volatility regimes.",
    status: "Testing",
    confidence: "Medium",
    updated: "Yesterday",
  },
];

const evidenceItems = [
  {
    label: "Hypotheses Defined",
    value: "8",
    icon: ClipboardList,
  },
  {
    label: "Evidence Records",
    value: "24",
    icon: FileSearch,
  },
  {
    label: "Validated Findings",
    value: "6",
    icon: CheckCircle2,
  },
  {
    label: "Research Dossiers",
    value: "3",
    icon: BookOpen,
  },
];

export function ResearchPage() {
  return (
    <section className="workspace-page">
      <div className="workspace-header">
        <div>
          <span className="workspace-eyebrow">RESEARCH INTELLIGENCE</span>
          <h1>Research Workspace</h1>
          <p>
            Build evidence-backed investment and trading research from hypothesis
            to validation.
          </p>
        </div>

        <div className="workspace-mode-card">
          <div className="workspace-mode-icon">
            <Search size={22} />
          </div>

          <div>
            <span>Research Engine</span>
            <strong>Evidence First</strong>
          </div>
        </div>
      </div>

      <div className="metric-grid">
        {evidenceItems.map((item) => {
          const Icon = item.icon;

          return (
            <article className="metric-card" key={item.label}>
              <div className="metric-card-top">
                <span>{item.label}</span>

                <div className="metric-icon">
                  <Icon size={20} />
                </div>
              </div>

              <strong>{item.value}</strong>

              <p>Research workspace</p>
            </article>
          );
        })}
      </div>

      <div className="research-grid">
        <article className="panel-card research-registry">
          <div className="panel-header">
            <div>
              <span className="panel-eyebrow">RESEARCH REGISTRY</span>
              <h2>Active Research</h2>
            </div>

            <span className="panel-badge">3 ACTIVE</span>
          </div>

          <div className="research-list">
            {researchItems.map((item) => (
              <div className="research-item" key={item.title}>
                <div className="research-item-icon">
                  <FileSearch size={20} />
                </div>

                <div className="research-item-content">
                  <div className="research-item-title-row">
                    <h3>{item.title}</h3>
                    <span>{item.updated}</span>
                  </div>

                  <p>{item.description}</p>

                  <div className="research-tags">
                    <span>{item.status}</span>
                    <span>{item.confidence} Confidence</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </article>

        <article className="panel-card">
          <div className="panel-header">
            <div>
              <span className="panel-eyebrow">VALIDATION</span>
              <h2>Research Workflow</h2>
            </div>
          </div>

          <div className="workflow-list">
            <div className="workflow-item">
              <div className="workflow-icon workflow-complete">
                <CheckCircle2 size={18} />
              </div>

              <div>
                <strong>Hypothesis Defined</strong>
                <span>Research question and assumptions documented</span>
              </div>
            </div>

            <div className="workflow-item">
              <div className="workflow-icon workflow-complete">
                <CheckCircle2 size={18} />
              </div>

              <div>
                <strong>Evidence Collected</strong>
                <span>Supporting and contradicting evidence reviewed</span>
              </div>
            </div>

            <div className="workflow-item">
              <div className="workflow-icon workflow-active">
                <Search size={18} />
              </div>

              <div>
                <strong>Robustness Analysis</strong>
                <span>Current research undergoing validation</span>
              </div>
            </div>

            <div className="workflow-item">
              <div className="workflow-icon">
                <ShieldCheck size={18} />
              </div>

              <div>
                <strong>Research Conclusion</strong>
                <span>Awaiting final evidence assessment</span>
              </div>
            </div>
          </div>
        </article>
      </div>

      <div className="research-bottom-grid">
        <article className="panel-card">
          <div className="panel-header">
            <div>
              <span className="panel-eyebrow">EVIDENCE INTELLIGENCE</span>
              <h2>Evidence Summary</h2>
            </div>
          </div>

          <div className="evidence-summary">
            <div className="evidence-row">
              <span>Supporting Evidence</span>
              <strong>16</strong>
            </div>

            <div className="evidence-row">
              <span>Contradicting Evidence</span>
              <strong>5</strong>
            </div>

            <div className="evidence-row">
              <span>Neutral Observations</span>
              <strong>3</strong>
            </div>

            <div className="evidence-conclusion">
              <span>RESEARCH POSITION</span>
              <strong>
                Current evidence supports further validation before deployment.
              </strong>
            </div>
          </div>
        </article>

        <article className="panel-card">
          <div className="panel-header">
            <div>
              <span className="panel-eyebrow">RESEARCH ACTIVITY</span>
              <h2>Recent Updates</h2>
            </div>
          </div>

          <div className="activity-list">
            <div>
              <span className="activity-dot" />
              <p>
                <strong>Momentum hypothesis evidence updated</strong>
                Historical sample review completed
              </p>
              <time>Just now</time>
            </div>

            <div>
              <span className="activity-dot" />
              <p>
                <strong>New sector research initiated</strong>
                Banking relative strength analysis added
              </p>
              <time>Today</time>
            </div>

            <div>
              <span className="activity-dot" />
              <p>
                <strong>Mean reversion test updated</strong>
                Volatility regime analysis in progress
              </p>
              <time>Yesterday</time>
            </div>
          </div>
        </article>
      </div>
    </section>
  );
}
