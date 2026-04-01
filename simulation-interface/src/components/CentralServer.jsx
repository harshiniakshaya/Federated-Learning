import { useState } from "react"
import { central } from "../api"

export default function CentralServer() {
  const [loading, setLoading] = useState(false)
  const [output, setOutput]   = useState("")
  const [runCount, setRunCount] = useState(0)

  const aggregate = async () => {
    setLoading(true)
    setOutput("")
    try {
      const res = await central.post("/aggregate")
      setOutput(JSON.stringify(res.data, null, 2))
      setRunCount((c) => c + 1)
    } catch (err) {
      setOutput(`Error: ${err.message}`)
    }
    setLoading(false)
  }

  return (
    <div className="space-y-6">

      {/* Header Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-center justify-center">
            <span className="text-2xl">🖥️</span>
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-100 tracking-tight">Central Server</h2>
            <p className="text-xs text-slate-500 mt-0.5 tracking-widest uppercase">Aggregation Node · Global Model</p>
          </div>
        </div>
        <div className="text-right">
          <div className="text-xs text-slate-500 tracking-widest uppercase">Aggregations Run</div>
          <div className="text-2xl font-mono font-black text-amber-400 mt-0.5">{runCount}</div>
        </div>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: "Connected Nodes", value: "2", color: "cyan" },
          { label: "Model Version",   value: `v${runCount}`,  color: "amber" },
          { label: "Protocol",        value: "FedAvg", color: "emerald" },
        ].map(({ label, value, color }) => (
          <div key={label} className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <div className="text-[10px] font-bold tracking-widest uppercase text-slate-500 mb-1">{label}</div>
            <div className={`text-2xl font-black font-mono
              ${color === "cyan"    ? "text-cyan-400"    : ""}
              ${color === "amber"   ? "text-amber-400"   : ""}
              ${color === "emerald" ? "text-emerald-400" : ""}
            `}>
              {value}
            </div>
          </div>
        ))}
      </div>

      {/* Aggregation Panel */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="border-b border-slate-800 px-6 py-4">
          <h3 className="text-sm font-bold tracking-widest uppercase text-slate-300">Federated Aggregation</h3>
          <p className="text-xs text-slate-500 mt-1">
            Collects local model weights from all nodes and computes the aggregated global model.
          </p>
        </div>

        <div className="p-6 space-y-6">
          {/* Flow Diagram */}
          <div className="flex items-center justify-center gap-3 py-4">
            {["Hospital A", "Hospital B"].map((node, i) => (
              <div key={node} className="flex items-center gap-3">
                <div className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-center">
                  <div className="text-lg">🏥</div>
                  <div className="text-[10px] font-bold tracking-widest text-slate-400 mt-1 uppercase">{node}</div>
                </div>
                <div className={`flex flex-col items-center gap-1 ${loading ? "opacity-100" : "opacity-40"}`}>
                  <div className={`text-xs text-amber-400 ${loading ? "animate-pulse" : ""}`}>▶</div>
                </div>
              </div>
            ))}
            <div className={`bg-amber-500/10 border-2 rounded-lg px-6 py-4 text-center transition-all ${
              loading ? "border-amber-400 shadow-lg shadow-amber-500/20" : "border-amber-500/30"
            }`}>
              <div className="text-xl">🖥️</div>
              <div className="text-[10px] font-bold tracking-widest text-amber-400 mt-1 uppercase">Central</div>
            </div>
          </div>

          <button
            onClick={aggregate}
            disabled={loading}
            className={`
              w-full py-4 rounded-xl text-sm font-black tracking-widest uppercase transition-all
              ${loading
                ? "bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700"
                : "bg-amber-500 hover:bg-amber-400 text-slate-950 shadow-lg shadow-amber-500/25"
              }
            `}
          >
            {loading ? (
              <span className="flex items-center justify-center gap-3">
                <span className="w-4 h-4 rounded-full border-2 border-slate-500 border-t-slate-300 animate-spin" />
                Aggregating Models...
              </span>
            ) : (
              "▶ Run Federated Aggregation"
            )}
          </button>
        </div>
      </div>

      {/* Output */}
      {(loading || output) && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
          <div className="border-b border-slate-800 px-6 py-3 flex items-center gap-2">
            {loading
              ? <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
              : <span className="w-2 h-2 rounded-full bg-emerald-400" />
            }
            <span className="text-xs font-bold tracking-widest uppercase text-slate-400">
              {loading ? "Aggregating..." : "Aggregation Result"}
            </span>
          </div>
          <pre className="p-6 text-xs text-amber-300 font-mono overflow-auto max-h-96 leading-relaxed">
            {loading ? "Processing federated weights from all nodes..." : output}
          </pre>
        </div>
      )}
    </div>
  )
}