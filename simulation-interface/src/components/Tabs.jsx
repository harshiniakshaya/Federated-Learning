export default function Tabs({ tabs, active, onChange }) {
  return (
    <div className="flex gap-1 bg-slate-900 border border-slate-800 rounded-lg p-1 w-fit">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          className={`
            flex items-center gap-2 px-5 py-2.5 rounded-md text-xs font-bold tracking-widest uppercase transition-all duration-200
            ${active === tab.id
              ? "bg-cyan-500 text-slate-950 shadow-lg shadow-cyan-500/20"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-800"
            }
          `}
        >
          {tab.icon && <span>{tab.icon}</span>}
          <span>{tab.label}</span>
        </button>
      ))}
    </div>
  )
}