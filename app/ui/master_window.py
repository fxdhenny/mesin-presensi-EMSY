import { useState, useEffect } from "react";

const C = {
  bg: "#f5ede0",
  cream: "#f0e6d3",
  tan: "#b8987a",
  tanLight: "#c9ab8e",
  tanDark: "#a0825f",
  dark: "#5a3e2b",
  darker: "#3d2b1f",
  white: "#ffffff",
  text: "#3d2b1f",
};

const ROMBELS = ["A1","A2","A3","B1","B2","B3","B4","B5","B6"];

const STUDENTS = {
  A1: [
    { nim:"2301001", nama:"Andi Kurniawan",    kelas:"XII TKJ", status:"hadir",  datang:"tepat waktu", pulang:"tepat waktu" },
    { nim:"2301002", nama:"Budi Santoso",      kelas:"XII TKJ", status:"hadir",  datang:"terlambat",   pulang:null },
    { nim:"2301003", nama:"Citra Dewi",        kelas:"XII TKJ", status:"izin",   datang:null,          pulang:null },
    { nim:"2301004", nama:"Dian Permata",      kelas:"XII TKJ", status:"hadir",  datang:"tepat waktu", pulang:"tepat waktu" },
    { nim:"2301005", nama:"Eko Prasetyo",      kelas:"XII TKJ", status:"alfa",   datang:null,          pulang:null },
    { nim:"2301006", nama:"Fajar Nugroho",     kelas:"XII TKJ", status:"sakit",  datang:null,          pulang:null },
    { nim:"2301007", nama:"Gita Lestari",      kelas:"XII TKJ", status:"hadir",  datang:"tepat waktu", pulang:null },
    { nim:"2301008", nama:"Hendra Wijaya",     kelas:"XII TKJ", status:"hadir",  datang:"terlambat",   pulang:null },
    { nim:"2301009", nama:"Ika Rahmawati",     kelas:"XII TKJ", status:"hadir",  datang:"tepat waktu", pulang:"tepat waktu" },
    { nim:"2301010", nama:"Joko Susilo",       kelas:"XII TKJ", status:"alfa",   datang:null,          pulang:null },
    { nim:"2301011", nama:"Kartika Sari",      kelas:"XII TKJ", status:"hadir",  datang:"tepat waktu", pulang:null },
    { nim:"2301012", nama:"Lutfi Hamdani",     kelas:"XII TKJ", status:"izin",   datang:null,          pulang:null },
  ],
};
ROMBELS.forEach(r => { if (!STUDENTS[r]) STUDENTS[r] = STUDENTS["A1"].map((s,i) => ({ ...s, nim: `23${r}${String(i+1).padStart(3,"0")}` })); });

const STATUS_OPTIONS = [
  { key:"hadir",        label:"H", full:"Hadir",       color:"#2d6a4f", bg:"#d8f3dc", border:"#74c69d" },
  { key:"izin",         label:"I", full:"Izin",        color:"#1d4e89", bg:"#dbeafe", border:"#93c5fd" },
  { key:"sakit",        label:"S", full:"Sakit",       color:"#92400e", bg:"#fef3c7", border:"#fcd34d" },
  { key:"alfa",         label:"A", full:"Alfa",        color:"#7f1d1d", bg:"#fee2e2", border:"#fca5a5" },
  { key:"tepat waktu",  label:"✓", full:"Tepat Waktu", color:"#064e3b", bg:"#d1fae5", border:"#6ee7b7" },
  { key:"terlambat",    label:"T", full:"Terlambat",   color:"#78350f", bg:"#ffedd5", border:"#fdba74" },
];

function fmtDate(d) {
  return d.toLocaleDateString("id-ID", { weekday:"long", day:"numeric", month:"long", year:"numeric" });
}
function fmtTime(d) {
  return d.toLocaleTimeString("id-ID", { hour:"2-digit", minute:"2-digit", second:"2-digit" });
}

export default function App() {
  const [screen, setScreen]         = useState("welcome");
  const [selRombel, setSelRombel]   = useState(null);
  const [selIdx, setSelIdx]         = useState(0);
  const [students, setStudents]     = useState(STUDENTS);
  const [scanAnim, setScanAnim]     = useState(false);
  const [exportMsg, setExportMsg]   = useState(null);
  const [toast, setToast]           = useState(null);
  const [now, setNow]               = useState(new Date());

  useEffect(() => {
    const t = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  const showToast = (msg) => {
    setToast(msg);
    setTimeout(() => setToast(null), 2000);
  };

  const handleScan = (type) => {
    setScanAnim(true);
    setTimeout(() => {
      setScanAnim(false);
      setScreen(type === "master" ? "rombel-select" : "rombel-select");
    }, 700);
  };

  const pickRombel = (r) => {
    setSelRombel(r);
    setSelIdx(0);
    setScreen("nim-list");
  };

  const pickNim = (idx) => {
    setSelIdx(idx);
    setScreen("student-detail");
  };

  const updateStatus = (nim, rombel, field, value) => {
    setStudents(prev => {
      const list = [...prev[rombel]];
      const i = list.findIndex(s => s.nim === nim);
      if (i < 0) return prev;
      let updated = { ...list[i] };
      if (field === "status") {
        updated.status = value;
        if (["alfa","izin","sakit"].includes(value)) {
          updated.datang = null; updated.pulang = null;
        }
      } else if (field === "datang") {
        updated.datang = value;
        updated.status = "hadir";
      } else {
        updated.pulang = value;
      }
      list[i] = updated;
      return { ...prev, [rombel]: list };
    });
    showToast(`${field === "status" ? "Status" : field === "datang" ? "Kedatangan" : "Kepulangan"} diperbarui`);
  };

  const curStudents = selRombel ? students[selRombel] : [];
  const curStudent  = curStudents[selIdx] || null;

  return (
    <div style={{ background: C.bg, minHeight: "100vh", fontFamily: "'Nunito', 'Segoe UI', sans-serif", position: "relative", overflow: "hidden" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;800;900&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        .tap-btn { transition: transform 0.1s, opacity 0.1s; cursor: pointer; }
        .tap-btn:active { transform: scale(0.95); opacity: 0.85; }
        .rombel-card { transition: transform 0.12s, background 0.12s; cursor: pointer; }
        .rombel-card:hover { transform: translateY(-3px); background: ${C.tanLight} !important; }
        .rombel-card:active { transform: scale(0.95); }
        .nim-card { transition: transform 0.1s, background 0.1s; cursor: pointer; }
        .nim-card:hover { background: ${C.tanLight} !important; }
        .nim-card:active { transform: scale(0.97); }
        .status-circle { transition: transform 0.1s; cursor: pointer; }
        .status-circle:hover { transform: scale(1.08); }
        .status-circle:active { transform: scale(0.93); }
        .nav-btn { transition: opacity 0.1s; cursor: pointer; }
        .nav-btn:hover { opacity: 0.85; }
        .nav-btn:active { transform: scale(0.96); }
        @keyframes scanPulse { 0%{box-shadow:0 0 0 0 rgba(90,62,43,0.5)} 100%{box-shadow:0 0 0 30px rgba(90,62,43,0)} }
        .scan-pulse { animation: scanPulse 0.7s ease-out; }
        @keyframes fadeUp { from{opacity:0;transform:translateY(16px)} to{opacity:1;transform:none} }
        .fade-up { animation: fadeUp 0.35s ease; }
      `}</style>

      {/* TOAST */}
      {toast && (
        <div style={{ position:"fixed", top:16, left:"50%", transform:"translateX(-50%)", zIndex:9999, background:C.dark, color:C.white, padding:"10px 28px", borderRadius:40, fontSize:14, fontWeight:700, letterSpacing:0.5, boxShadow:"0 4px 20px rgba(0,0,0,0.25)" }}>
          ✓ {toast}
        </div>
      )}

      {/* ═══════════════════ WELCOME SCREEN ═══════════════════ */}
      {screen === "welcome" && (
        <div style={{ minHeight:"100vh", display:"flex", flexDirection:"column" }} className="fade-up">
          {/* Top bar */}
          <div style={{ background: C.tan, padding:"14px 32px", display:"flex", justifyContent:"space-between", alignItems:"center" }}>
            <span style={{ color:C.white, fontWeight:700, fontSize:18 }}>{fmtDate(now)}</span>
            <span style={{ color:C.white, fontWeight:700, fontSize:18 }}>{fmtTime(now)}</span>
          </div>

          {/* Center content */}
          <div style={{ flex:1, display:"flex", flexDirection:"column", alignItems:"center", justifyContent:"center", gap:32 }}>
            <div style={{ fontFamily:"'Nunito', sans-serif", fontWeight:900, fontSize:120, color:C.dark, lineHeight:1, letterSpacing:-2, userSelect:"none" }}>
              WELCOME
            </div>
            <div className={scanAnim ? "scan-pulse" : ""} style={{ border:`2.5px solid ${C.darker}`, borderRadius:40, padding:"14px 48px" }}>
              <span style={{ fontWeight:700, fontSize:20, color:C.darker }}>Please scan your Rfid!</span>
            </div>

            {/* Demo tap zone */}
            <div style={{ display:"flex", gap:16, marginTop:32 }}>
              <div className="tap-btn" onClick={() => handleScan("rombel")}
                style={{ background: C.tan, borderRadius:14, padding:"12px 28px", color:C.white, fontWeight:800, fontSize:14, letterSpacing:1, boxShadow:"0 3px 12px rgba(90,62,43,0.3)" }}>
                TAP — KARTU ROMBEL
              </div>
              <div className="tap-btn" onClick={() => handleScan("master")}
                style={{ background: C.dark, borderRadius:14, padding:"12px 28px", color:C.white, fontWeight:800, fontSize:14, letterSpacing:1, boxShadow:"0 3px 12px rgba(90,62,43,0.4)" }}>
                TAP — KARTU MASTER
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ═══════════════════ ROMBEL SELECT SCREEN ═══════════════════ */}
      {screen === "rombel-select" && (
        <div style={{ minHeight:"100vh", display:"flex" }} className="fade-up">
          {/* Left sidebar */}
          <div style={{ width:80, background:C.dark, display:"flex", alignItems:"center", justifyContent:"center", flexShrink:0 }}>
            <span style={{ color:C.white, fontWeight:900, fontSize:28, letterSpacing:8, writingMode:"vertical-rl", transform:"rotate(180deg)", userSelect:"none" }}>
              ROMBEL
            </span>
          </div>

          {/* Main content */}
          <div style={{ flex:1, background:C.bg, padding:"40px 40px 40px 48px", display:"flex", flexDirection:"column" }}>
            {/* EXPORT button top-right */}
            <div style={{ display:"flex", justifyContent:"flex-end", marginBottom:36 }}>
              <div className="tap-btn" onClick={() => { setExportMsg("Mengekspor..."); setTimeout(()=>{ setExportMsg("Ekspor sukses ke /media/usb0/"); showToast("Ekspor data berhasil!"); setExportMsg(null); }, 1800); }}
                style={{ background:C.dark, borderRadius:14, padding:"12px 36px", color:C.white, fontWeight:900, fontSize:18, letterSpacing:2, boxShadow:"0 4px 14px rgba(0,0,0,0.2)", cursor:"pointer" }}>
                {exportMsg || "EXPORT"}
              </div>
            </div>

            {/* 3×3 grid */}
            <div style={{ display:"grid", gridTemplateColumns:"repeat(3, 1fr)", gap:20, maxWidth:640 }}>
              {ROMBELS.map(r => (
                <div key={r} className="rombel-card tap-btn" onClick={() => pickRombel(r)}
                  style={{ background:C.tan, borderRadius:20, aspectRatio:"1", display:"flex", alignItems:"center", justifyContent:"center", boxShadow:"0 3px 12px rgba(90,62,43,0.2)" }}>
                  <span style={{ color:C.white, fontWeight:900, fontSize:42, letterSpacing:1 }}>{r}</span>
                </div>
              ))}
            </div>

            {/* Back to home */}
            <div style={{ marginTop:"auto", paddingTop:32 }}>
              <div className="tap-btn" onClick={() => setScreen("welcome")}
                style={{ display:"inline-flex", alignItems:"center", gap:8, background:C.dark, borderRadius:40, padding:"10px 28px", color:C.white, fontWeight:700, fontSize:14, cursor:"pointer" }}>
                ← HOME
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ═══════════════════ NIM LIST SCREEN ═══════════════════ */}
      {screen === "nim-list" && selRombel && (
        <div style={{ minHeight:"100vh", display:"flex", flexDirection:"column" }} className="fade-up">
          {/* Header */}
          <div style={{ background:C.dark, padding:"22px 40px" }}>
            <span style={{ color:C.white, fontWeight:900, fontSize:36, letterSpacing:1 }}>
              ROMBEL "{selRombel}"
            </span>
          </div>

          {/* NIM grid */}
          <div style={{ flex:1, padding:"36px 40px" }}>
            <div style={{ display:"grid", gridTemplateColumns:"repeat(3, 1fr)", gap:16 }}>
              {curStudents.map((s, i) => (
                <div key={s.nim} className="nim-card tap-btn" onClick={() => pickNim(i)}
                  style={{ background:C.tan, borderRadius:16, padding:"18px 20px", display:"flex", alignItems:"center", justifyContent:"center", boxShadow:"0 2px 8px rgba(90,62,43,0.18)", minHeight:70 }}>
                  <span style={{ color:C.white, fontWeight:800, fontSize:18, letterSpacing:1 }}>{s.nim}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Nav */}
          <div style={{ padding:"16px 40px 32px", display:"flex", gap:16 }}>
            <div className="nav-btn tap-btn" onClick={() => setScreen("rombel-select")}
              style={{ background:C.dark, borderRadius:40, padding:"12px 32px", color:C.white, fontWeight:800, fontSize:16 }}>
              ‹ BACK
            </div>
            <div className="nav-btn tap-btn" onClick={() => setScreen("welcome")}
              style={{ background:C.dark, borderRadius:40, padding:"12px 32px", color:C.white, fontWeight:800, fontSize:16, marginLeft:"auto", marginRight:"auto" }}>
              HOME
            </div>
          </div>
        </div>
      )}

      {/* ═══════════════════ STUDENT DETAIL SCREEN ═══════════════════ */}
      {screen === "student-detail" && curStudent && (
        <div style={{ minHeight:"100vh", display:"flex", flexDirection:"column", padding:"36px 40px 24px" }} className="fade-up">
          <div style={{ flex:1, display:"flex", flexDirection:"column" }}>
            {/* Title */}
            <div style={{ marginBottom:28 }}>
              <div style={{ fontWeight:900, fontSize:44, color:C.dark, lineHeight:1.1 }}>DATA<br/>MAHASISWA</div>
            </div>

            {/* Two-column layout */}
            <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:32, flex:1, alignItems:"start" }}>
              {/* LEFT — Info card */}
              <div style={{ background:C.tan, borderRadius:20, padding:"28px 28px", boxShadow:"0 3px 14px rgba(90,62,43,0.2)" }}>
                {[["Nama", curStudent.nama], ["NIM", curStudent.nim], ["Kelas", curStudent.kelas]].map(([label, val]) => (
                  <div key={label} style={{ marginBottom:22 }}>
                    <div style={{ fontWeight:800, fontSize:18, color:C.white }}>
                      {label} : <span style={{ fontWeight:700, fontSize:16 }}>{val}</span>
                    </div>
                  </div>
                ))}
                {/* Current status badges */}
                <div style={{ borderTop:`1.5px solid rgba(255,255,255,0.3)`, paddingTop:16, display:"flex", gap:8, flexWrap:"wrap" }}>
                  {curStudent.status && (
                    <span style={{ background:"rgba(255,255,255,0.2)", color:C.white, borderRadius:20, padding:"4px 14px", fontSize:13, fontWeight:700 }}>
                      {curStudent.status.toUpperCase()}
                    </span>
                  )}
                  {curStudent.datang && (
                    <span style={{ background:"rgba(255,255,255,0.2)", color:C.white, borderRadius:20, padding:"4px 14px", fontSize:12, fontWeight:700 }}>
                      DTG: {curStudent.datang}
                    </span>
                  )}
                  {curStudent.pulang && (
                    <span style={{ background:"rgba(255,255,255,0.2)", color:C.white, borderRadius:20, padding:"4px 14px", fontSize:12, fontWeight:700 }}>
                      PLG: {curStudent.pulang}
                    </span>
                  )}
                </div>
              </div>

              {/* RIGHT — Status circles 2×3 */}
              <div>
                <div style={{ fontSize:13, color:C.tanDark, fontWeight:700, marginBottom:14, letterSpacing:0.5 }}>UBAH STATUS</div>
                <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:16 }}>
                  {STATUS_OPTIONS.map(opt => {
                    const isActive = curStudent.status === opt.key || curStudent.datang === opt.key;
                    return (
                      <div key={opt.key} className="status-circle" onClick={() => {
                        if (["hadir","izin","sakit","alfa"].includes(opt.key)) {
                          updateStatus(curStudent.nim, selRombel, "status", opt.key);
                        } else {
                          updateStatus(curStudent.nim, selRombel, "datang", opt.key);
                        }
                      }}
                        style={{
                          width:"100%", aspectRatio:"1", borderRadius:"50%",
                          background: isActive ? opt.bg : C.tan,
                          border: isActive ? `3px solid ${opt.border}` : `3px solid ${C.tanDark}`,
                          display:"flex", flexDirection:"column", alignItems:"center", justifyContent:"center",
                          boxShadow: isActive ? `0 2px 12px ${opt.border}66` : "0 2px 8px rgba(90,62,43,0.15)"
                        }}>
                        <span style={{ fontWeight:900, fontSize:28, color: isActive ? opt.color : C.white }}>
                          {opt.label}
                        </span>
                        <span style={{ fontSize:10, fontWeight:700, color: isActive ? opt.color : "rgba(255,255,255,0.7)", marginTop:2 }}>
                          {opt.full}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>

          {/* Bottom navigation */}
          <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", paddingTop:28 }}>
            <div className="nav-btn tap-btn" onClick={() => { if (selIdx > 0) setSelIdx(i => i-1); else setScreen("nim-list"); }}
              style={{ background:C.dark, borderRadius:40, padding:"14px 36px", color:C.white, fontWeight:900, fontSize:17, minWidth:140, textAlign:"center" }}>
              ‹ BACK
            </div>
            <div className="nav-btn tap-btn" onClick={() => setScreen("welcome")}
              style={{ background:C.dark, borderRadius:40, padding:"14px 36px", color:C.white, fontWeight:900, fontSize:17, minWidth:140, textAlign:"center" }}>
              HOME
            </div>
            <div className="nav-btn tap-btn" onClick={() => { if (selIdx < curStudents.length-1) setSelIdx(i => i+1); }}
              style={{ background: selIdx < curStudents.length-1 ? C.dark : C.tan, borderRadius:40, padding:"14px 36px", color:C.white, fontWeight:900, fontSize:17, minWidth:140, textAlign:"center" }}>
              NEXT ›
            </div>
          </div>
        </div>
      )}
    </div>
  );
}