import { useState } from "react"
import HospitalA from "./components/HospitalA"
import HospitalB from "./components/HospitalB"
import CentralServer from "./components/CentralServer"

export default function App() {
  const [tab, setTab] = useState("A")

  const tabs = [
    { id: "A", label: "Hospital A", icon: "🏥" },
    { id: "B", label: "Hospital B", icon: "🏥" },
    { id: "C", label: "Central Server", icon: "🖥️" },
  ]

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-mono">

      {/* Background grid */}
      <div
        className="fixed inset-0 opacity-[0.03] pointer-events-none"
        style={{
          backgroundImage:
            "linear-gradient(rgba(148,163,184,1) 1px, transparent 1px), linear-gradient(90deg, rgba(148,163,184,1) 1px, transparent 1px)",
          backgroundSize: "40px 40px",
        }}
      />

      {/* Header */}
      <header className="relative border-b border-slate-800 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-sm bg-cyan-500 flex items-center justify-center">
              <span className="text-slate-950 text-xs font-black">CKD</span>
            </div>
            <div>
              <h1 className="text-sm font-bold tracking-widest text-slate-100 uppercase">
                Federated CKD Dashboard
              </h1>
              <p className="text-xs text-slate-500 tracking-wider">
                Chronic Kidney Disease · Federated Learning Network
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
            <span className="text-xs text-slate-400 tracking-widest uppercase">Live</span>
          </div>
        </div>
      </header>

      {/* Tab Bar */}
      <div className="relative max-w-6xl mx-auto px-6 mt-8">
        <div className="flex gap-1 bg-slate-900 border border-slate-800 rounded-lg p-1 w-fit">
          {tabs.map((t) => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`
                flex items-center gap-2 px-5 py-2.5 rounded-md text-xs font-bold tracking-widest uppercase transition-all duration-200
                ${tab === t.id
                  ? "bg-cyan-500 text-slate-950 shadow-lg shadow-cyan-500/20"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800"
                }
              `}
            >
              <span>{t.icon}</span>
              <span>{t.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <main className="relative max-w-6xl mx-auto px-6 py-8">
        {tab === "A" && <HospitalA />}
        {tab === "B" && <HospitalB />}
        {tab === "C" && <CentralServer />}
      </main>
    </div>
  )
}