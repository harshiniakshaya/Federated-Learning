import { useState } from "react"
import { hospitalB_local, hospitalB_comm } from "../api"

const FIELDS = [
  { name: "age",            label: "Age",             type: "number" },
  { name: "bp",             label: "Blood Pressure",  type: "number" },
  { name: "sg",             label: "Specific Gravity",type: "number" },
  { name: "al",             label: "Albumin",         type: "number" },
  { name: "su",             label: "Sugar",           type: "number" },
  { name: "rbc",            label: "Red Blood Cells", type: "text"   },
  { name: "pc",             label: "Pus Cell",        type: "text"   },
  { name: "pcc",            label: "Pus Cell Clumps", type: "text"   },
  { name: "ba",             label: "Bacteria",        type: "text"   },
  { name: "bgr",            label: "Blood Glucose",   type: "number" },
  { name: "bu",             label: "Blood Urea",      type: "number" },
  { name: "sc",             label: "Serum Creatinine",type: "number" },
  { name: "sod",            label: "Sodium",          type: "number" },
  { name: "pot",            label: "Potassium",       type: "number" },
  { name: "hemo",           label: "Hemoglobin",      type: "number" },
  { name: "pcv",            label: "Packed Cell Vol", type: "number" },
  { name: "wc",             label: "WBC Count",       type: "number" },
  { name: "rc",             label: "RBC Count",       type: "number" },
  { name: "htn",            label: "Hypertension",    type: "text"   },
  { name: "dm",             label: "Diabetes Mellitus",type: "text"  },
  { name: "cad",            label: "Coronary Artery", type: "text"   },
  { name: "appet",          label: "Appetite",        type: "text"   },
  { name: "pe",             label: "Pedal Edema",     type: "text"   },
  { name: "ane",            label: "Anemia",          type: "text"   },
  { name: "classification", label: "Classification",  type: "text"   },
]

export default function HospitalB() {
  const [loading, setLoading] = useState(false)
  const [output, setOutput]   = useState("")
  const [mode, setMode]       = useState("form")
  const [patient, setPatient] = useState({})
  const [rawData, setRawData] = useState("")
  const [activeAction, setActiveAction] = useState("")

  const handleChange = (e) => setPatient({ ...patient, [e.target.name]: e.target.value })

  const run = async (label, fn) => {
    setLoading(true)
    setActiveAction(label)
    setOutput("")
    try {
      const res = await fn()
      setOutput(JSON.stringify(res.data, null, 2))
    } catch (err) {
      setOutput(`Error: ${err.message}`)
    }
    setLoading(false)
    setActiveAction("")
  }

  const addPatient = () => run("Adding Patient",     async () => {
    const payload = mode === "form" ? patient : JSON.parse(rawData)
    return hospitalB_local.post("/add_patient", payload)
  })
  const trainLocal = () => run("Training Model",     () => hospitalB_local.post("/train_local"))
  const pushModel  = () => run("Pushing to Central", () => hospitalB_comm.post("/push_to_central"))
  const pullModel  = () => run("Pulling Global",     () => hospitalB_comm.get("/pull_from_central"))

  return (
    <div className="space-y-6">

      {/* Header Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-lg bg-violet-500/10 border border-violet-500/30 flex items-center justify-center">
            <span className="text-2xl">🏥</span>
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-100 tracking-tight">Hospital B</h2>
            <p className="text-xs text-slate-500 mt-0.5 tracking-widest uppercase">Local Node · Federated Network</p>
          </div>
        </div>
        <div className="text-right">
          <div className="text-xs text-slate-500 tracking-widest uppercase">Node ID</div>
          <div className="text-sm font-mono text-violet-400 mt-0.5">HOSP-B-002</div>
        </div>
      </div>

      {/* Add Patient Section */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="border-b border-slate-800 px-6 py-4 flex items-center justify-between">
          <h3 className="text-sm font-bold tracking-widest uppercase text-slate-300">Add Patient Record</h3>
          <div className="flex gap-1 bg-slate-950 border border-slate-800 rounded-md p-0.5">
            {["form", "raw"].map((m) => (
              <button
                key={m}
                onClick={() => setMode(m)}
                className={`px-3 py-1.5 rounded text-xs font-bold tracking-widest uppercase transition-all ${
                  mode === m ? "bg-slate-700 text-slate-100" : "text-slate-500 hover:text-slate-300"
                }`}
              >
                {m === "form" ? "Form" : "JSON"}
              </button>
            ))}
          </div>
        </div>

        <div className="p-6">
          {mode === "form" ? (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
              {FIELDS.map((f) => (
                <div key={f.name} className="flex flex-col gap-1">
                  <label className="text-[10px] font-bold tracking-widest uppercase text-slate-500">
                    {f.label}
                  </label>
                  <input
                    name={f.name}
                    type={f.type}
                    onChange={handleChange}
                    className="bg-slate-950 border border-slate-700 rounded-md px-3 py-2 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500/30 transition-all"
                    placeholder={f.name.toUpperCase()}
                  />
                </div>
              ))}
            </div>
          ) : (
            <textarea
              rows={12}
              value={rawData}
              onChange={(e) => setRawData(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-md px-4 py-3 text-sm text-violet-300 font-mono placeholder-slate-600 focus:outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500/30 transition-all resize-none"
              placeholder={'{\n  "age": 45,\n  "bp": 80,\n  ...\n}'}
            />
          )}

          <button
            onClick={addPatient}
            disabled={loading}
            className="mt-4 px-6 py-2.5 bg-violet-500 hover:bg-violet-400 disabled:opacity-40 disabled:cursor-not-allowed text-white text-xs font-black tracking-widest uppercase rounded-lg transition-all shadow-lg shadow-violet-500/20"
          >
            + Add Patient
          </button>
        </div>
      </div>

      {/* Model Actions */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="border-b border-slate-800 px-6 py-4">
          <h3 className="text-sm font-bold tracking-widest uppercase text-slate-300">Model Operations</h3>
        </div>
        <div className="p-6 flex flex-wrap gap-3">
          {[
            { label: "Train Local Model",  fn: trainLocal, color: "emerald" },
            { label: "Push to Central",     fn: pushModel,  color: "violet"  },
            { label: "Pull Global Model",   fn: pullModel,  color: "amber"   },
          ].map(({ label, fn, color }) => (
            <button
              key={label}
              onClick={fn}
              disabled={loading}
              className={`
                px-5 py-2.5 rounded-lg text-xs font-bold tracking-widest uppercase border transition-all disabled:opacity-40 disabled:cursor-not-allowed
                ${color === "emerald" ? "border-emerald-500/40 text-emerald-400 bg-emerald-500/10 hover:bg-emerald-500/20" : ""}
                ${color === "violet"  ? "border-violet-500/40 text-violet-400 bg-violet-500/10 hover:bg-violet-500/20"   : ""}
                ${color === "amber"   ? "border-amber-500/40 text-amber-400 bg-amber-500/10 hover:bg-amber-500/20"       : ""}
              `}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Output */}
      {(loading || output) && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
          <div className="border-b border-slate-800 px-6 py-3 flex items-center gap-2">
            {loading
              ? <span className="w-2 h-2 rounded-full bg-violet-400 animate-pulse" />
              : <span className="w-2 h-2 rounded-full bg-emerald-400" />
            }
            <span className="text-xs font-bold tracking-widest uppercase text-slate-400">
              {loading ? `${activeAction}...` : "Output"}
            </span>
          </div>
          <pre className="p-6 text-xs text-violet-300 font-mono overflow-auto max-h-80 leading-relaxed">
            {loading ? "Awaiting response..." : output}
          </pre>
        </div>
      )}
    </div>
  )
}