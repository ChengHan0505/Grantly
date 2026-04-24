"use client";
import React from "react";
import s from "./page.module.css";

function MI({name,size=24,color}:{name:string;size?:number;color?:string}){
  return <span className="material-icon" style={{fontSize:size,color}}>{name}</span>;
}

export function CompanyTab(){
  const [isEditing, setIsEditing] = React.useState(false);
  const [name, setName] = React.useState("Nexus Dynamics Sdn Bhd");
  const [vertical, setVertical] = React.useState("Information & Communication Tech (ICT)");
  const [stage, setStage] = React.useState("Early Stage / MVP");
  const [desc, setDesc] = React.useState("Nexus Dynamics develops AI-driven predictive maintenance software for the manufacturing sector. Our core platform utilizes machine learning algorithms to analyze sensor data from industrial machinery, predicting failures before they occur and minimizing costly downtime.");
  const [prob, setProb] = React.useState("Unplanned equipment downtime costs the global manufacturing industry an estimated $50 billion annually. Current preventative maintenance schedules are often inefficient, replacing parts prematurely or failing to catch irregular faults.");
  const [aiModalOpen, setAiModalOpen] = React.useState(false);

  return <div style={{overflowY:"auto"}}>
    <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-end",marginBottom:12}}>
      <div className={s.pageHeader} style={{marginBottom:0}}>
        <div className={s.pageTitle} style={{fontSize:24}}>Company Profile</div>
        <div className={s.pageSub} style={{marginTop:4,fontSize:13}}>Consolidated view of your registration, onboarding, and organizational narrative.</div>
      </div>
      {isEditing ? (
        <div style={{display:"flex",gap:8}}>
          <button className="btn-outline-sm" onClick={() => setIsEditing(false)}>Cancel</button>
          <button className="btn-primary" onClick={() => setIsEditing(false)}>Save</button>
        </div>
      ) : (
        <button className="btn-soft" style={{padding:"6px 12px",fontSize:13}} onClick={() => setIsEditing(true)}><MI name="edit" size={15}/>Edit</button>
      )}
    </div>

    {/* AI Analysis Top Section */}
    <div className={s.panel} onClick={() => setAiModalOpen(true)} style={{borderRadius:20,padding:"14px 20px",marginBottom:16,background:"linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)",border:"1px solid #bae6fd",cursor:"pointer",transition:"all 0.2s"}}>
      <div style={{display:"flex",gap:20,alignItems:"center"}}>
        <div style={{position:"relative",width:54,height:54,flexShrink:0}}>
          <svg viewBox="0 0 36 36" style={{width:"100%",height:"100%",transform:"rotate(-90deg)"}}>
            <circle cx="18" cy="18" r="16" fill="transparent" stroke="rgba(0,180,216,0.2)" strokeWidth="4"/>
            <circle cx="18" cy="18" r="16" fill="transparent" stroke="#00B4D8" strokeWidth="4" strokeDasharray="85 100" strokeDashoffset="0"/>
          </svg>
          <div style={{position:"absolute",inset:0,display:"flex",alignItems:"center",justifyContent:"center",flexDirection:"column"}}>
            <span style={{fontSize:16,fontWeight:900,color:"#006780",lineHeight:1}}>85</span>
          </div>
        </div>
        <div style={{flex:1}}>
          <div style={{display:"flex",alignItems:"center",gap:6}}>
            <MI name="auto_awesome" size={16} color="#0087A5"/>
            <span style={{fontSize:15,fontWeight:800,color:"#0F172A"}}>AI Grant Readiness Analysis</span>
          </div>
          <p style={{fontSize:13,color:"#334155",lineHeight:1.4,marginTop:4,marginBottom:0}}>
            Profile is optimized. To reach a 95+ score, upload <strong>Export Compliance Certificates</strong> and detail your <strong>Community Benefit Plan</strong>.
          </p>
        </div>
        <div style={{flexShrink:0,display:"flex",gap:8}}>
          <div style={{background:"#fff",padding:"6px 10px",borderRadius:6,display:"flex",alignItems:"center",gap:6,boxShadow:"0 2px 4px rgba(0,0,0,0.05)"}}>
            <MI name="check_circle" size={14} color="#10B981"/>
            <span style={{fontSize:12,fontWeight:700,color:"#0F172A"}}>Strong Traction</span>
          </div>
          <div style={{background:"#fff",padding:"6px 10px",borderRadius:6,display:"flex",alignItems:"center",gap:6,boxShadow:"0 2px 4px rgba(0,0,0,0.05)"}}>
            <MI name="warning" size={14} color="#F59E0B"/>
            <span style={{fontSize:12,fontWeight:700,color:"#0F172A"}}>Missing Docs</span>
          </div>
        </div>
      </div>
    </div>

    <div className={s.profileLayout}>
      <div className={s.profileMain} style={{gap:16}}>
        {/* Business Fundamentals */}
        <div className={s.panel} style={{borderRadius:20,padding:24}}>
          <CardTitle icon="corporate_fare" title="Business Fundamentals" color="#006780" small/>
          {isEditing ? (
            <div style={{display:"flex",flexDirection:"column",gap:12,marginTop:16}}>
              <div style={{display:"flex",gap:16}}>
                <div style={{flex:1}}><input style={{width:"100%",padding:"8px 12px",border:"1px solid #E0E7EC",borderRadius:6,fontSize:13}} placeholder="Legal Entity Name" value={name} onChange={e=>setName(e.target.value)} /></div>
                <div style={{flex:1}}><input style={{width:"100%",padding:"8px 12px",border:"1px solid #E0E7EC",borderRadius:6,fontSize:13}} placeholder="Industry" value={vertical} onChange={e=>setVertical(e.target.value)} /></div>
              </div>
              <textarea style={{width:"100%",padding:"8px 12px",border:"1px solid #E0E7EC",borderRadius:6,fontSize:13,minHeight:60,fontFamily:"inherit"}} placeholder="Description" value={desc} onChange={e=>setDesc(e.target.value)} />
              <textarea style={{width:"100%",padding:"8px 12px",border:"1px solid #E0E7EC",borderRadius:6,fontSize:13,minHeight:60,fontFamily:"inherit"}} placeholder="Problem Solved" value={prob} onChange={e=>setProb(e.target.value)} />
            </div>
          ) : (
            <div style={{marginTop:16}}>
              <div style={{display:"flex",gap:12,alignItems:"center",marginBottom:12}}>
                <span style={{fontSize:16,fontWeight:800,color:"#191C1E"}}>{name}</span>
                <span style={{fontSize:12,background:"#F2F4F6",padding:"4px 10px",borderRadius:999,fontWeight:600}}>{vertical}</span>
                <span style={{fontSize:12,background:"rgba(0,180,216,0.15)",color:"#006780",padding:"4px 10px",borderRadius:999,fontWeight:600}}>{stage}</span>
              </div>
              <div style={{fontSize:13,color:"#3D494D",lineHeight:1.5,marginBottom:10}}><strong>Desc:</strong> {desc}</div>
              <div style={{fontSize:13,color:"#3D494D",lineHeight:1.5}}><strong>Problem:</strong> {prob}</div>
            </div>
          )}
        </div>
        {/* Document Repository */}
        <div className={s.panel} style={{borderRadius:20,padding:16}}>
          <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:12}}>
            <CardTitle icon="folder" title="Document Repository" color="#904D00" small/>
            <span style={{color:"#006780",fontWeight:700,fontSize:11}}>View All →</span>
          </div>
          <div className={s.docGrid} style={{gap:12}}>
            <div style={{flex:1,padding:12,borderRadius:12,border:"1px solid #E0E7EC",display:"flex",alignItems:"center",gap:8}}><MI name="picture_as_pdf" size={16} color="#BA1A1A"/><span style={{fontSize:11,fontWeight:600,overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>SSM_2023.pdf</span></div>
            <div style={{flex:1,padding:12,borderRadius:12,border:"1px solid #E0E7EC",display:"flex",alignItems:"center",gap:8}}><MI name="slideshow" size={16} color="#494BD6"/><span style={{fontSize:11,fontWeight:600,overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>InvestorDeck.pptx</span></div>
            <div style={{flex:1,padding:12,borderRadius:12,border:"1px solid #E0E7EC",display:"flex",alignItems:"center",gap:8}}><MI name="table_chart" size={16} color="#904D00"/><span style={{fontSize:11,fontWeight:600,overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>Financials.xlsx</span></div>
          </div>
        </div>
      </div>
      <div className={s.profileSide} style={{gap:16}}>
        {/* Funding Needs */}
        <div className={s.panel} style={{borderRadius:20,padding:16}}>
          <CardTitle icon="payments" title="Funding Allocation" color="#904D00" small/>
          <div style={{height:12}}/>
          <div style={{position:"relative",width:100,height:100,margin:"0 auto"}}>
            <svg viewBox="0 0 36 36" style={{width:"100%",height:"100%",transform:"rotate(-90deg)"}}>
              <circle cx="18" cy="18" r="16" fill="transparent" stroke="#006780" strokeWidth="4" strokeDasharray="40 100" strokeDashoffset="0"/>
              <circle cx="18" cy="18" r="16" fill="transparent" stroke="#904D00" strokeWidth="4" strokeDasharray="35 100" strokeDashoffset="-40"/>
              <circle cx="18" cy="18" r="16" fill="transparent" stroke="#494BD6" strokeWidth="4" strokeDasharray="25 100" strokeDashoffset="-75"/>
            </svg>
            <div style={{position:"absolute",inset:0,display:"flex",alignItems:"center",justifyContent:"center",flexDirection:"column"}}>
              <span style={{fontSize:9,color:"#3D494D",fontWeight:700}}>TOTAL</span>
              <span style={{fontSize:14,fontWeight:900,color:"#191C1E"}}>RM 500k</span>
            </div>
          </div>
          <div style={{height:12}}/>
          <div style={{fontSize:11,display:"flex",justifyContent:"space-between",marginBottom:4}}><span style={{color:"#006780",fontWeight:700}}>Product (40%)</span></div>
          <div style={{fontSize:11,display:"flex",justifyContent:"space-between",marginBottom:4}}><span style={{color:"#904D00",fontWeight:700}}>Talent (35%)</span></div>
          <div style={{fontSize:11,display:"flex",justifyContent:"space-between"}}><span style={{color:"#494BD6",fontWeight:700}}>Marketing (25%)</span></div>
        </div>
        
        {/* Traction */}
        <div className={s.panel} style={{borderRadius:20,padding:16}}>
          <CardTitle icon="trending_up" title="Traction Growth" color="#494BD6" small/>
          <div style={{height:12}}/>
          <div style={{display:"flex",alignItems:"flex-end",justifyContent:"space-between",height:80,paddingTop:12,gap:8,borderBottom:"1px solid #E0E7EC"}}>
            <div style={{flex:1,background:"#F2F4F6",height:"30%",borderRadius:"4px 4px 0 0",position:"relative"}}><span style={{position:"absolute",top:-18,left:"50%",transform:"translateX(-50%)",fontSize:10,color:"#6D797E",fontWeight:700}}>Q1</span></div>
            <div style={{flex:1,background:"rgba(73,75,214,0.3)",height:"50%",borderRadius:"4px 4px 0 0",position:"relative"}}><span style={{position:"absolute",top:-18,left:"50%",transform:"translateX(-50%)",fontSize:10,color:"#494BD6",fontWeight:700}}>Q2</span></div>
            <div style={{flex:1,background:"rgba(73,75,214,0.6)",height:"70%",borderRadius:"4px 4px 0 0",position:"relative"}}><span style={{position:"absolute",top:-18,left:"50%",transform:"translateX(-50%)",fontSize:10,color:"#494BD6",fontWeight:700}}>Q3</span></div>
            <div style={{flex:1,background:"#494BD6",height:"100%",borderRadius:"4px 4px 0 0",position:"relative"}}><span style={{position:"absolute",top:-18,left:"50%",transform:"translateX(-50%)",fontSize:10,fontWeight:900,color:"#494BD6"}}>Q4</span></div>
          </div>
          <div style={{height:12}}/>
          <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:4}}>
            <span style={{color:"#3D494D",fontSize:12,fontWeight:600}}>MRR</span>
            <span style={{fontSize:14,fontWeight:900,color:"#191C1E"}}>RM 15,000</span>
          </div>
          <div style={{display:"flex",justifyContent:"space-between",alignItems:"center"}}>
            <span style={{color:"#3D494D",fontSize:12,fontWeight:600}}>Pilots</span>
            <span style={{fontSize:13,fontWeight:800,color:"#006780"}}>4 Factories</span>
          </div>
        </div>
      </div>
    </div>

    {aiModalOpen && <AiAnalysisModal onClose={() => setAiModalOpen(false)} />}
  </div>;
}

function AiAnalysisModal({onClose}: {onClose:()=>void}) {
  const [chat, setChat] = React.useState([
    {role:"assistant", text:"Hi there! I'm your Grantly AI assistant. I've analyzed your profile and identified a few missing elements that are preventing a 95+ readiness score. How can I help you complete them?"}
  ]);
  const [input, setInput] = React.useState("");

  const handleSend = () => {
    if(!input.trim()) return;
    setChat(prev => [...prev, {role:"user", text:input}, {role:"assistant", text:"I can certainly help with that. Uploading your compliance certificate takes about 2 minutes via the Document Vault."}]);
    setInput("");
  };

  return (
    <div style={{position:"fixed", inset:0, zIndex:999, display:"flex", alignItems:"center", justifyContent:"center", background:"rgba(15, 23, 42, 0.4)", backdropFilter:"blur(4px)"}}>
      <div className={s.panel} style={{width: 900, maxWidth:"95vw", height: 600, maxHeight:"90vh", display:"flex", flexDirection:"column", overflow:"hidden", background:"#fff", borderRadius:24, boxShadow:"0 24px 48px rgba(0,0,0,0.2)", padding:0}}>
        
        {/* Header */}
        <div style={{padding: "16px 24px", borderBottom:"1px solid #E0E7EC", display:"flex", justifyContent:"space-between", alignItems:"center", background:"linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)"}}>
          <div style={{display:"flex", gap:12, alignItems:"center"}}>
            <MI name="auto_awesome" size={24} color="#0087A5"/>
            <h2 style={{fontSize: 20, fontWeight: 900, color: "#0F172A", margin:0}}>Profile Readiness Analysis</h2>
          </div>
          <button onClick={onClose} style={{background:"transparent", border:"none", cursor:"pointer", padding:0, display:"flex"}}><MI name="close" size={24} color="#6D797E"/></button>
        </div>

        <div style={{display:"flex", flex:1, overflow:"hidden"}}>
          
          {/* Left Side: Action Plan */}
          <div style={{flex: 1.2, padding: 24, overflowY:"auto", borderRight:"1px solid #E0E7EC"}}>
            
            {/* Score Banner */}
            <div style={{display:"flex", alignItems:"center", gap:20, marginBottom:24, background:"#F8FAFC", padding:16, borderRadius:16, border:"1px solid #E0E7EC"}}>
              <div style={{position:"relative",width:64,height:64,flexShrink:0}}>
                <svg viewBox="0 0 36 36" style={{width:"100%",height:"100%",transform:"rotate(-90deg)"}}>
                  <circle cx="18" cy="18" r="16" fill="transparent" stroke="#E0E7EC" strokeWidth="4"/>
                  <circle cx="18" cy="18" r="16" fill="transparent" stroke="#00B4D8" strokeWidth="4" strokeDasharray="85 100" strokeDashoffset="0"/>
                </svg>
                <div style={{position:"absolute",inset:0,display:"flex",alignItems:"center",justifyContent:"center"}}>
                  <span style={{fontSize:18,fontWeight:900,color:"#006780"}}>85</span>
                </div>
              </div>
              <div>
                <div style={{fontSize:16, fontWeight:800, color:"#191C1E"}}>Current Score: 85 / 100</div>
                <div style={{fontSize:13, color:"#3D494D", marginTop:4}}>Your profile is in the top 15% of peers.</div>
              </div>
            </div>

            <div style={{fontSize:14, fontWeight:800, color:"#191C1E", marginBottom:12}}>Suggested Action Plan</div>
            <div style={{display:"flex", flexDirection:"column", gap:12}}>
              
              <div style={{padding:16, borderRadius:12, border:"1px solid #bae6fd", background:"#f0f9ff"}}>
                <div style={{display:"flex", justifyContent:"space-between", alignItems:"flex-start", marginBottom:8}}>
                  <div style={{display:"flex", gap:8, alignItems:"center"}}>
                    <div style={{width:20, height:20, borderRadius:"50%", background:"#0ea5e9", color:"#fff", display:"flex", alignItems:"center", justifyContent:"center", fontSize:11, fontWeight:800}}>1</div>
                    <span style={{fontSize:14, fontWeight:700, color:"#0369a1"}}>Upload Compliance Certificate</span>
                  </div>
                  <span style={{fontSize:11, fontWeight:700, color:"#0369a1", background:"#e0f2fe", padding:"2px 8px", borderRadius:999}}>+5 Pts</span>
                </div>
                <div style={{fontSize:13, color:"#075985", lineHeight:1.4}}>Many federal grants require Form 89-B. Missing this document automatically disqualifies you from 40% of DoD funding.</div>
                <button className="btn-primary" style={{marginTop:12, padding:"6px 12px", fontSize:12}}><MI name="upload" size={14}/> Upload Now</button>
              </div>

              <div style={{padding:16, borderRadius:12, border:"1px solid #E0E7EC"}}>
                <div style={{display:"flex", justifyContent:"space-between", alignItems:"flex-start", marginBottom:8}}>
                  <div style={{display:"flex", gap:8, alignItems:"center"}}>
                    <div style={{width:20, height:20, borderRadius:"50%", background:"#91A0B6", color:"#fff", display:"flex", alignItems:"center", justifyContent:"center", fontSize:11, fontWeight:800}}>2</div>
                    <span style={{fontSize:14, fontWeight:700, color:"#191C1E"}}>Detail Community Benefit</span>
                  </div>
                  <span style={{fontSize:11, fontWeight:700, color:"#6D797E", background:"#F2F4F6", padding:"2px 8px", borderRadius:999}}>+5 Pts</span>
                </div>
                <div style={{fontSize:13, color:"#3D494D", lineHeight:1.4}}>Add metrics on local job creation to your 'Problem Solved' narrative to align with recent DOE FOA trends.</div>
              </div>

            </div>

            <div style={{fontSize:14, fontWeight:800, color:"#191C1E", marginTop:24, marginBottom:12}}>Profile Strengths</div>
            <div style={{display:"flex", flexWrap:"wrap", gap:8}}>
              <span className={s.tag} style={{background:"#ecfdf5", color:"#059669", border:"1px solid #a7f3d0"}}><MI name="check_circle" size={14}/> Verified Traction</span>
              <span className={s.tag} style={{background:"#ecfdf5", color:"#059669", border:"1px solid #a7f3d0"}}><MI name="check_circle" size={14}/> Patent Portfolio</span>
              <span className={s.tag} style={{background:"#ecfdf5", color:"#059669", border:"1px solid #a7f3d0"}}><MI name="check_circle" size={14}/> Pitch Deck Ready</span>
            </div>

          </div>

          {/* Right Side: AI Chat */}
          <div style={{flex: 1, display:"flex", flexDirection:"column", background:"#F8FAFC"}}>
            <div style={{padding:"12px 20px", borderBottom:"1px solid #E0E7EC", background:"#fff", display:"flex", alignItems:"center", gap:8}}>
              <MI name="forum" size={18} color="#0087A5"/>
              <span style={{fontSize:14, fontWeight:800, color:"#0F172A"}}>Ask AI Assistant</span>
            </div>
            
            {/* Chat History */}
            <div style={{flex:1, overflowY:"auto", padding:20, display:"flex", flexDirection:"column", gap:16}}>
              {chat.map((msg, i) => (
                <div key={i} style={{display:"flex", flexDirection: msg.role === "user" ? "row-reverse" : "row", gap:12}}>
                  <div style={{width:28, height:28, borderRadius:"50%", background: msg.role === "user" ? "#191C1E" : "#00B4D8", flexShrink:0, display:"flex", alignItems:"center", justifyContent:"center"}}>
                    <MI name={msg.role === "user" ? "person" : "auto_awesome"} size={16} color="#fff"/>
                  </div>
                  <div style={{
                    background: msg.role === "user" ? "#191C1E" : "#fff",
                    color: msg.role === "user" ? "#fff" : "#191C1E",
                    padding:"10px 14px",
                    borderRadius: msg.role === "user" ? "12px 12px 0 12px" : "12px 12px 12px 0",
                    fontSize:13,
                    lineHeight:1.5,
                    border: msg.role === "user" ? "none" : "1px solid #E0E7EC",
                    boxShadow: "0 2px 4px rgba(0,0,0,0.02)",
                    maxWidth: "85%"
                  }}>
                    {msg.text}
                  </div>
                </div>
              ))}
            </div>

            {/* Chat Input */}
            <div style={{padding:16, borderTop:"1px solid #E0E7EC", background:"#fff"}}>
              <div style={{display:"flex", gap:8}}>
                <input 
                  type="text" 
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSend()}
                  placeholder="Ask how to improve your score..." 
                  style={{flex:1, padding:"10px 14px", border:"1px solid #E0E7EC", borderRadius:100, fontSize:13, outline:"none"}}
                />
                <button onClick={handleSend} style={{width:38, height:38, borderRadius:"50%", background:"#006780", border:"none", color:"#fff", display:"flex", alignItems:"center", justifyContent:"center", cursor:"pointer"}}>
                  <MI name="send" size={16}/>
                </button>
              </div>
            </div>

          </div>

        </div>
      </div>
    </div>
  );
}

export function DraftsTab(){
  const [activeTag, setActiveTag] = React.useState("ALL");

  const roadmaps = [
    { id: 1, title: "DOE_EERE_CleanEnergy_Roadmap", tag: "READY", progress: 0.72, grant: "Clean Energy Infrastructure Deployment Grant", generated: "Generated just now", accent: "#006780" },
    { id: 2, title: "NSF_Convergence_Materials_Roadmap", tag: "GENERATED", progress: 0.56, grant: "Sustainable Materials Development", generated: "Generated yesterday", accent: "#494BD6" },
    { id: 3, title: "NIH_R01_Biomarkers_Readiness_Map", tag: "DRAFT", progress: 0.38, grant: "Advanced Biomarkers for Early Detection", generated: "Generated Oct 2, 2024", accent: "#6D797E" }
  ];

  const filtered = activeTag === "ALL" ? roadmaps : roadmaps.filter(r => r.tag === activeTag);

  return <div style={{overflowY:"auto"}}>
    <div className={s.pageHeader}>
      <div style={{display:"flex",alignItems:"center",gap:10}}><MI name="history_edu" size={18} color="#904D00"/><div className={s.pageTitle} style={{fontSize:28}}>Roadmaps &amp; Outputs</div></div>
      <div className={s.pageSub}>View generated grant application roadmaps, check milestones, and download the roadmap package after applying from the Grants tab.</div>
    </div>
    <div style={{height:16}}/>
    <div className={s.roadmapLayout}>
      <div className={s.roadmapMain}>
        <div style={{display:"flex",gap:8,marginBottom:20}}>
          {["ALL", "READY", "GENERATED", "DRAFT"].map(tag => (
            <button key={tag} onClick={() => setActiveTag(tag)} className={activeTag === tag ? s.tagActive : s.tagFilter} style={{
              background: activeTag === tag ? "#00B4D8" : "#fff",
              color: activeTag === tag ? "#fff" : "#3D494D",
              border: activeTag === tag ? "1px solid #00B4D8" : "1px solid #E0E7EC",
              padding: "6px 14px", borderRadius: 999, fontSize: 12, fontWeight: 700, cursor: "pointer", transition: "all 0.2s"
            }}>
              {tag}
            </button>
          ))}
        </div>
        {filtered.length === 0 ? (
          <div style={{padding: 40, textAlign: "center", color: "#6D797E", fontSize: 14}}>No roadmaps found with this status.</div>
        ) : (
          filtered.map(r => (
            <RoadmapCard key={r.id} title={r.title} tag={r.tag} progress={r.progress} grant={r.grant} generated={r.generated} accent={r.accent}/>
          ))
        )}
      </div>
      <div className={s.roadmapSide}>
        <div className={s.panel} style={{borderRadius:26,padding:18}}>
          <div style={{fontWeight:900,letterSpacing:2,fontSize:12,color:"#191C1E"}}>FILTER BY</div>
          <div style={{height:14}}/>
          <CheckRow label="All Roadmaps" checked={activeTag === "ALL"} onClick={() => setActiveTag("ALL")}/>
          <CheckRow label="Ready to Execute" checked={activeTag === "READY"} onClick={() => setActiveTag("READY")}/>
          <CheckRow label="In Progress" checked={activeTag === "GENERATED" || activeTag === "DRAFT"} onClick={() => setActiveTag("DRAFT")}/>
          <div style={{height:16}}/>
          <div style={{height:1,background:"#E0E7EC"}}/>
          <div style={{height:16}}/>
          <div style={{fontWeight:900,letterSpacing:2,fontSize:12,color:"#191C1E"}}>RECENT ACTIVITY</div>
          <div style={{height:12}}/>
          <ActivityRow color="#904D00" title="Generated Roadmap" detail="DOE_EERE_CleanEnergy - just now"/>
          <ActivityRow color="#006780" title="Applied to Grant" detail="NSF_Convergence - 1d ago"/>
        </div>
      </div>
    </div>
  </div>;
}

function CardTitle({icon,title,color,small}:{icon:string;title:string;color:string;small?:boolean}){
  return <div className={s.cardTitleRow}><div className={s.cardTitleIcon} style={{background:`${color}1f`}}><MI name={icon} size={16} color={color}/></div><span className={s.cardTitleText} style={{fontSize:small?16:18}}>{title}</span></div>;
}

function Field({label,value,prominent,pill,teal,boxed}:{label:string;value:string;prominent?:boolean;pill?:boolean;teal?:boolean;boxed?:boolean}){
  const inner = pill
    ? <span className={s.tag} style={{background:teal?"rgba(0,103,128,0.1)":"#F2F4F6",color:teal?"#006780":"#191C1E"}}>{value}</span>
    : <div className={s.fieldValue} style={{fontSize:prominent?15:13,fontWeight:prominent?800:500}}>{value}</div>;
  return <div><div className={s.fieldLabel}>{label}</div>{boxed?<div className={s.fieldBox}>{inner}</div>:inner}</div>;
}

function DocCard({icon,tag,title,color}:{icon:string;tag:string;title:string;color:string}){
  return <div className={s.docCard}>
    <div className={s.docCardHeader}><div className={s.docCardIcon} style={{background:`${color}1f`}}><MI name={icon} size={20} color={color}/></div><span className={s.tag} style={{background:"#F2F4F6",color:"#3D494D"}}>{tag}</span></div>
    <div className={s.docCardTitle}>{title}</div>
    <div style={{fontSize:12,color:"#3D494D",marginTop:8}}>Uploaded recently - 2.4 MB</div>
    <div className={s.docBtnRow}><button className="btn-outline-sm" style={{flex:1,color:"#191C1E"}}>View</button><button className="btn-outline-sm" style={{flex:1,color:"#006780"}}>Update</button></div>
  </div>;
}

function FundRow({color,title,sub}:{color:string;title:string;sub:string}){
  return <div className={s.fundRow}><div className={s.fundDotOuter}><div className={s.fundDotInner} style={{background:color}}/></div><div><div style={{fontWeight:800,color:"#191C1E"}}>{title}</div><div style={{fontSize:12,color:"#3D494D"}}>{sub}</div></div></div>;
}

function MetricProgress({label,value,progress,color}:{label:string;value:string;progress:number;color:string}){
  return <div><div className={s.metricProgressRow}><span style={{color:"#3D494D",fontSize:12}}>{label}</span><span style={{fontSize:13,fontWeight:900,color:"#191C1E"}}>{value}</span></div><div className={s.progressTrack}><div className={s.progressFill} style={{width:`${progress*100}%`,background:color}}/></div></div>;
}

function RoadmapCard({title,tag,progress,grant,generated,accent}:{title:string;tag:string;progress:number;grant:string;generated:string;accent:string}){
  const steps=["Profile Fit","Gap Closure","Submission Pack","Final Review"];
  const thresholds=[0.25,0.50,0.75,0.95];
  return <div className={s.panel} style={{borderRadius:26,padding:18,marginBottom:16}}>
    <div style={{display:"flex",gap:14}}>
      <div style={{width:38,height:38,borderRadius:"50%",background:`${accent}1f`,display:"flex",alignItems:"center",justifyContent:"center",flexShrink:0}}><MI name="route" size={18} color={accent}/></div>
      <div style={{flex:1}}>
        <div style={{display:"flex",justifyContent:"space-between",gap:8}}><div style={{fontSize:14,fontWeight:900,letterSpacing:-0.3,color:"#191C1E"}}>{title}</div><span className={s.tag} style={{background:`${accent}1a`,color:accent}}>{tag}</span></div>
        <div style={{color:"#3D494D",fontSize:12,marginTop:4}}>{grant}</div>
        <div style={{color:"#768190",marginTop:2,fontSize:12}}>{generated}</div>
      </div>
    </div>
    <div className={s.roadmapSteps}>
      {steps.map((st,i)=>{
        const done=progress>=thresholds[i];
        return <div key={st} className={s.roadmapStep}>
          <div style={{display:"flex",alignItems:"center"}}>
            <div className={s.stepDot} style={{background:done?accent:"#F2F4F6"}}><MI name={done?"check":"more_horiz"} size={12} color={done?"#fff":"#3D494D"}/></div>
            <div className={s.stepLine} style={{background:done?`${accent}73`:"#F2F4F6"}}/>
          </div>
          <div className={s.stepLabel} style={{color:done?"#191C1E":"#3D494D"}}>{st}</div>
        </div>;
      })}
    </div>
    <div style={{display:"flex",flexWrap:"wrap",gap:10}}>
      <button className="btn-soft"><MI name="visibility" size={14}/>View Roadmap</button>
      <button className="btn-primary"><MI name="download" size={14}/>Download</button>
    </div>
  </div>;
}

function CheckRow({label,checked,onClick}:{label:string;checked?:boolean;onClick?:()=>void}){
  return <div className={s.checkRow} onClick={onClick} style={{cursor:"pointer"}}><div className={s.checkDot} style={{background:checked?"#006780":"transparent",border:checked?"none":"1px solid #3D494D"}}>{checked&&<MI name="check" size={12} color="#fff"/>}</div><span style={{color:"#191C1E",fontSize:13}}>{label}</span></div>;
}

function ActivityRow({color,title,detail}:{color:string;title:string;detail:string}){
  return <div className={s.activityRow}><div className={s.activityDot} style={{background:color}}/><div><div style={{color:"#191C1E",fontSize:15}}>{title}</div><div style={{color:"#3D494D",fontSize:13}}>{detail}</div></div></div>;
}
