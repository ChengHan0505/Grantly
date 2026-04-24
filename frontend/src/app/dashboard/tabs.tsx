"use client";
import React from "react";
import s from "./page.module.css";

function MI({name,size=24,color}:{name:string;size?:number;color?:string}){
  return <span className="material-icon" style={{fontSize:size,color}}>{name}</span>;
}

export function HomeTab({onGenerateRoadmap}: {onGenerateRoadmap?: ()=>void}){
  const [selectedGrant, setSelectedGrant] = React.useState<any>(null);

  const grants = [
    {id: 1, source:"FEDERAL", title:"NSF AI Research Grant", amount:"$2.5M", match:98, status:"READY TO SUBMIT", accent:"#006780", 
     desc:"The National Science Foundation (NSF) supports fundamental research in artificial intelligence. This grant targets innovative AI architectures and their applications in critical sectors like manufacturing.",
     link:"https://new.nsf.gov/funding",
     aiAnalysis: [
       {icon:"check_circle", color:"#10B981", text:"Perfect alignment with your predictive maintenance algorithms."},
       {icon:"warning", color:"#F59E0B", text:"Requires an updated data privacy policy document."}
     ]
    },
    {id: 2, source:"STATE", title:"CA Clean Energy Initiative", amount:"$1.2M", match:85, status:"AUDITED", accent:"#494BD6",
     desc:"A state-level initiative focusing on technological solutions that reduce carbon footprints in industrial settings.",
     link:"https://www.energy.ca.gov/funding-opportunities",
     aiAnalysis: [
       {icon:"check_circle", color:"#10B981", text:"Your Industry 4.0 goal directly reduces energy waste."},
       {icon:"warning", color:"#F59E0B", text:"Needs a localized California impact statement."}
     ]
    },
    {id: 3, source:"CORPORATE", title:"Google Tech Impact", amount:"$750k", match:72, status:"DRAFTING DECK", accent:"#904D00",
     desc:"Google's philanthropic arm supports startups leveraging technology for broad industrial impact.",
     link:"https://www.google.org/our-work/",
     aiAnalysis: [
       {icon:"check_circle", color:"#10B981", text:"Cloud-native architecture aligns well with Google Cloud ecosystem."},
       {icon:"error", color:"#BA1A1A", text:"Missing open-source contribution history."}
     ]
    },
    {id: 4, source:"FOUNDATION", title:"Gates Global Health", amount:"$500k", match:65, status:"DISCOVERED", accent:"#6D797E",
     desc:"Supports initiatives that improve global health and infrastructure.",
     link:"https://www.gatesfoundation.org/about/how-we-work/grant-opportunities",
     aiAnalysis: [
       {icon:"warning", color:"#F59E0B", text:"Manufacturing focus is slightly tangential to core health objectives."},
       {icon:"check_circle", color:"#10B981", text:"Strong scalable technology base."}
     ]
    }
  ];

  return <div style={{overflowY:"auto", paddingBottom: 40}}>
    <div style={{display: "flex", flexWrap: "wrap", gap: 24}}>
      
      {/* LEFT COLUMN: Main Focus */}
      <div style={{flex: "1 1 600px", display: "flex", flexDirection: "column", gap: 16}}>
        <MetricCards/>
        
        {/* Vertical Pipeline Feed */}
        <div className={s.panel} style={{padding: 24, borderRadius: 26, background: "rgba(242,244,246,0.78)"}}>
          <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start"}}>
            <div>
              <div style={{fontSize:20,fontWeight:900,letterSpacing:-0.5,color:"#191C1E"}}>Recommended Grants Feed</div>
              <div style={{fontSize:13,color:"#3D494D",marginTop:4}}>AI-curated based on your SME profile</div>
            </div>
            <button className="btn-soft"><MI name="sort" size={15}/>Sort: Match %</button>
          </div>
          <div style={{height: 20}}/>
          <div style={{display: "flex", flexDirection: "column", gap: 12}}>
            {grants.map(g => (
              <FeedCard key={g.id} source={g.source} title={g.title} amount={g.amount} match={g.match} status={g.status} accent={g.accent} onViewDetails={() => setSelectedGrant(g)} />
            ))}
          </div>
        </div>
      </div>

      {/* RIGHT COLUMN: Graphical Views */}
      <div style={{flex: "1 1 300px", display: "flex", flexDirection: "column", gap: 16}}>
        <RadarWidget />
        <PitchDeckWidget />
        <TimelineWidget />
      </div>

    </div>

    {selectedGrant && (
      <GrantModal grant={selectedGrant} onClose={() => setSelectedGrant(null)} onGenerateRoadmap={onGenerateRoadmap} />
    )}
  </div>;
}

function RadarWidget() {
  return (
    <div className={s.panel} style={{padding: 24, borderRadius: 26}}>
      <div style={{fontWeight: 900, fontSize: 16, color: "#191C1E"}}>SME Suitability Analysis</div>
      <div style={{color: "#3D494D", fontSize: 12, marginTop: 4}}>Based on your uploaded documents</div>
      <div style={{height: 20}}/>
      <div style={{position: "relative", width: 180, height: 180, margin: "0 auto"}}>
        <svg viewBox="0 0 100 100" style={{width: "100%", height: "100%", overflow: "visible"}}>
          {/* Background grid */}
          <polygon points="50,10 90,50 50,90 10,50" fill="none" stroke="#E0E7EC" strokeWidth="1"/>
          <polygon points="50,30 70,50 50,70 30,50" fill="none" stroke="#E0E7EC" strokeWidth="1"/>
          <line x1="50" y1="10" x2="50" y2="90" stroke="#E0E7EC" strokeWidth="1"/>
          <line x1="10" y1="50" x2="90" y2="50" stroke="#E0E7EC" strokeWidth="1"/>
          {/* Data shape */}
          <polygon points="50,20 85,50 50,65 20,50" fill="rgba(0,180,216,0.2)" stroke="#00B4D8" strokeWidth="2"/>
          {/* Labels */}
          <text x="50" y="5" fontSize="6" textAnchor="middle" fill="#3D494D" fontWeight="700">Innovation</text>
          <text x="96" y="52" fontSize="6" textAnchor="start" fill="#3D494D" fontWeight="700">Market</text>
          <text x="50" y="99" fontSize="6" textAnchor="middle" fill="#3D494D" fontWeight="700">Impact</text>
          <text x="4" y="52" fontSize="6" textAnchor="end" fill="#3D494D" fontWeight="700">Team</text>
        </svg>
      </div>
      <div style={{height: 16}}/>
      <div style={{display: "flex", justifyContent: "space-between", alignItems: "center"}}>
        <span style={{fontSize: 13, fontWeight: 800, color: "#006780"}}>Overall Match: 88%</span>
        <button className="btn-soft" style={{fontSize: 11, padding: "4px 8px"}}><MI name="tune" size={14}/> Adjust</button>
      </div>
    </div>
  );
}

function PitchDeckWidget() {
  return (
    <div className={s.panel} style={{padding: 24, borderRadius: 26, background: "linear-gradient(135deg, rgba(73,75,214,0.05), rgba(0,180,216,0.05))"}}>
      <div style={{fontWeight: 900, fontSize: 16, color: "#191C1E"}}>AI Pitch Deck Engine</div>
      <div style={{color: "#3D494D", fontSize: 12, marginTop: 4}}>Compiling your narrative</div>
      <div style={{height: 20}}/>
      <div style={{display: "flex", alignItems: "center", gap: 16}}>
        <div style={{position: "relative", width: 56, height: 56}}>
          <svg viewBox="0 0 36 36" style={{width: "100%", height: "100%", transform: "rotate(-90deg)"}}>
            <circle cx="18" cy="18" r="16" fill="none" stroke="#E0E7EC" strokeWidth="3"/>
            <circle cx="18" cy="18" r="16" fill="none" stroke="#494BD6" strokeWidth="3" strokeDasharray="100" strokeDashoffset="25" strokeLinecap="round"/>
          </svg>
          <div style={{position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 800, fontSize: 12, color: "#494BD6"}}>75%</div>
        </div>
        <div style={{flex: 1}}>
          <div style={{fontSize: 13, fontWeight: 700, color: "#191C1E"}}>Drafting 'Financials'</div>
          <div style={{fontSize: 11, color: "#3D494D", marginTop: 4}}>Synthesizing from uploaded Excel models...</div>
        </div>
      </div>
      <div style={{height: 20}}/>
      <button className="btn-primary" style={{width: "100%", justifyContent: "center"}} disabled><MI name="sync" size={16}/> Generating...</button>
    </div>
  );
}

function TimelineWidget() {
  return (
    <div className={s.panel} style={{padding: 24, borderRadius: 26}}>
      <div style={{fontWeight: 900, fontSize: 16, color: "#191C1E"}}>Upcoming Deadlines</div>
      <div style={{height: 16}}/>
      <div style={{display: "flex", flexDirection: "column", gap: 12}}>
        <div style={{display: "flex", gap: 12}}>
          <div style={{width: 3, background: "#BA1A1A", borderRadius: 2}}/>
          <div>
            <div style={{fontSize: 13, fontWeight: 800, color: "#191C1E"}}>NSF AI Research</div>
            <div style={{fontSize: 11, color: "#BA1A1A", fontWeight: 700, marginTop: 2}}>Due in 5 Days (Oct 15)</div>
          </div>
        </div>
        <div style={{display: "flex", gap: 12}}>
          <div style={{width: 3, background: "#904D00", borderRadius: 2}}/>
          <div>
            <div style={{fontSize: 13, fontWeight: 800, color: "#191C1E"}}>Gates Global Health</div>
            <div style={{fontSize: 11, color: "#904D00", fontWeight: 700, marginTop: 2}}>Due Nov 01</div>
          </div>
        </div>
        <div style={{display: "flex", gap: 12}}>
          <div style={{width: 3, background: "#006780", borderRadius: 2}}/>
          <div>
            <div style={{fontSize: 13, fontWeight: 800, color: "#191C1E"}}>CA Clean Energy</div>
            <div style={{fontSize: 11, color: "#3D494D", marginTop: 2}}>Rolling Deadline</div>
          </div>
        </div>
      </div>
    </div>
  );
}

function MetricCards(){
  return <div className={s.metricGrid}>
    <div className={s.metricCard}>
      <div className={s.metricHeader}><span className={s.metricTitle}>READINESS SCORE</span><MI name="speed" size={16} color="#006780"/></div>
      <div className={s.metricValue} style={{fontSize:34,color:"#006780"}}>88.4%</div>
      <div className={s.metricCaption}>+2.1% from last audit</div>
    </div>
    <div className={s.metricCard}>
      <div className={s.metricHeader}><span className={s.metricTitle}>ACTIVE PIPELINE</span><MI name="account_tree" size={16} color="#494BD6"/></div>
      <div className={s.metricValue} style={{fontSize:34,color:"#494BD6"}}>12</div>
      <div className={s.metricCaption}>3 grants requiring attention</div>
      <div style={{height:10}}/>
      <div className={s.stackedProgress}>
        <div style={{flex:40,background:"#006780"}}/>
        <div style={{flex:35,background:"#494BD6"}}/>
        <div style={{flex:25,background:"#904D00"}}/>
      </div>
    </div>
    <div className={s.metricCard}>
      <div className={s.metricHeader}><span className={s.metricTitle}>DOCUMENT HEALTH</span><MI name="health_and_safety" size={16} color="#904D00"/></div>
      <div className={s.metricValue} style={{fontSize:26,color:"#191C1E"}}>Good</div>
      <div className={s.metricCaption}>92% metadata completion</div>
      <div style={{height:10}}/>
      <div style={{display:"flex",alignItems:"center",gap:6}}><MI name="check_circle" size={13} color="#006780"/><span style={{color:"#3D494D",fontSize:12}}>All critical tags present</span></div>
    </div>
  </div>;
}

function FeedCard({source, title, amount, match, status, accent, onViewDetails}:{source:string;title:string;amount:string;match:number;status:string;accent:string;onViewDetails:()=>void}) {
  return (
    <div className={s.panel} style={{padding: 16, borderRadius: 16, display: "flex", alignItems: "center", gap: 16, background: "#fff", boxShadow: "0 4px 12px rgba(0,0,0,0.03)"}}>
      <div style={{width: 54, height: 54, borderRadius: "50%", background: `${accent}1f`, display: "flex", alignItems: "center", justifyContent: "center", flexDirection: "column", flexShrink: 0}}>
        <span style={{fontWeight: 900, fontSize: 15, color: accent, lineHeight: 1}}>{match}%</span>
        <span style={{fontSize: 9, fontWeight: 800, color: accent, marginTop: 2}}>FIT</span>
      </div>
      <div style={{flex: 1}}>
        <div style={{display: "flex", gap: 8, alignItems: "center"}}>
          <span className={s.tag} style={{background: `${accent}1a`, color: accent, fontSize: 10}}>{source}</span>
          <span style={{fontSize: 10, fontWeight: 800, color: "#6D797E", letterSpacing: 0.5}}>{status}</span>
        </div>
        <div style={{fontSize: 15, fontWeight: 900, color: "#191C1E", marginTop: 8}}>{title}</div>
      </div>
      <div style={{textAlign: "right", flexShrink: 0}}>
        <div style={{fontSize: 16, fontWeight: 900, color: "#006780"}}>{amount}</div>
        <button className="btn-outline-sm" onClick={onViewDetails} style={{marginTop: 10, padding: "6px 14px", fontSize: 12}}>View Details</button>
      </div>
    </div>
  );
}

function GrantModal({grant, onClose, onGenerateRoadmap}: {grant:any; onClose:()=>void; onGenerateRoadmap?:()=>void}) {
  return (
    <div style={{position:"fixed", inset:0, zIndex:999, display:"flex", alignItems:"center", justifyContent:"center", background:"rgba(15, 23, 42, 0.4)", backdropFilter:"blur(4px)"}}>
      <div className={s.panel} style={{width: 800, maxWidth:"90vw", maxHeight:"85vh", display:"flex", flexDirection:"column", overflow:"hidden", background:"#fff", borderRadius:24, boxShadow:"0 24px 48px rgba(0,0,0,0.2)", padding:0}}>
        <div style={{padding: 24, borderBottom:"1px solid #E0E7EC", display:"flex", justifyContent:"space-between", alignItems:"center"}}>
          <div style={{display:"flex", gap:12, alignItems:"center"}}>
            <span className={s.tag} style={{background: `${grant.accent}1a`, color: grant.accent, fontSize: 12}}>{grant.source}</span>
            <h2 style={{fontSize: 20, fontWeight: 900, color: "#191C1E", margin:0}}>{grant.title}</h2>
          </div>
          <button onClick={onClose} style={{background:"transparent", border:"none", cursor:"pointer", padding:0, display:"flex"}}><MI name="close" size={24} color="#6D797E"/></button>
        </div>
        
        <div style={{display:"flex", flex:1, overflow:"hidden"}}>
          {/* Main Info */}
          <div style={{flex: 6, padding: 24, overflowY:"auto", borderRight:"1px solid #E0E7EC"}}>
            <div style={{display:"flex", justifyContent:"space-between", marginBottom:24}}>
              <div>
                <div style={{fontSize:12, color:"#6D797E", fontWeight:700, marginBottom:4}}>GRANT AMOUNT</div>
                <div style={{fontSize:28, fontWeight:900, color: grant.accent}}>{grant.amount}</div>
              </div>
              <div style={{textAlign:"right"}}>
                <div style={{fontSize:12, color:"#6D797E", fontWeight:700, marginBottom:4}}>STATUS</div>
                <div style={{fontSize:16, fontWeight:800, color: "#191C1E"}}>{grant.status}</div>
              </div>
            </div>
            
            <div style={{fontSize:14, fontWeight:800, color:"#191C1E", marginBottom:8}}>Description</div>
            <p style={{fontSize:14, color:"#3D494D", lineHeight:1.6, marginBottom:24}}>
              {grant.desc}
            </p>

            <div style={{fontSize:14, fontWeight:800, color:"#191C1E", marginBottom:8}}>Application Requirements</div>
            <ul style={{fontSize:14, color:"#3D494D", lineHeight:1.6, paddingLeft:20, margin:0}}>
              <li style={{marginBottom:8}}>Detailed Business Plan and Project Roadmap</li>
              <li style={{marginBottom:8}}>2 Years of Audited Financials</li>
              <li>Proof of Incorporation and Entity Status</li>
            </ul>

            {grant.link && (
              <div style={{marginTop: 24}}>
                <a href={grant.link} target="_blank" rel="noreferrer" style={{display:"inline-flex", alignItems:"center", gap:6, fontSize:14, fontWeight:700, color:"#006780", textDecoration:"none"}}>
                  <MI name="launch" size={16}/> Official Grant Website
                </a>
              </div>
            )}
          </div>
          
          {/* AI Analysis Sidebar */}
          <div style={{flex: 4, padding: 24, background:"#F8FAFC", overflowY:"auto"}}>
            <div style={{display:"flex", alignItems:"center", gap:8, marginBottom:20}}>
              <MI name="auto_awesome" size={20} color="#0087A5"/>
              <span style={{fontSize:16, fontWeight:900, color:"#0F172A"}}>AI Compatibility Analysis</span>
            </div>
            
            <div style={{display:"flex", alignItems:"center", gap:16, marginBottom:24}}>
              <div style={{width: 60, height: 60, borderRadius: "50%", background: `${grant.accent}1f`, display: "flex", alignItems: "center", justifyContent: "center", flexDirection: "column", flexShrink: 0}}>
                <span style={{fontWeight: 900, fontSize: 18, color: grant.accent, lineHeight: 1}}>{grant.match}%</span>
                <span style={{fontSize: 9, fontWeight: 800, color: grant.accent, marginTop: 2}}>MATCH</span>
              </div>
              <div style={{fontSize:13, color:"#334155", lineHeight:1.5}}>
                Based on your company profile and uploaded documents, this grant is a <strong>strong match</strong>.
              </div>
            </div>

            <div style={{fontSize:12, fontWeight:800, color:"#6D797E", letterSpacing:1, marginBottom:12}}>AI INSIGHTS</div>
            <div style={{display:"flex", flexDirection:"column", gap:12}}>
              {grant.aiAnalysis.map((insight:any, idx:number) => (
                <div key={idx} style={{background:"#fff", padding:12, borderRadius:8, display:"flex", gap:10, boxShadow:"0 2px 4px rgba(0,0,0,0.02)", border:"1px solid #E0E7EC"}}>
                  <div style={{flexShrink:0}}><MI name={insight.icon} size={18} color={insight.color}/></div>
                  <span style={{fontSize:13, color:"#191C1E", lineHeight:1.4}}>{insight.text}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
        
        <div style={{padding: 20, borderTop:"1px solid #E0E7EC", background:"#F8FAFC", display:"flex", justifyContent:"flex-end", gap:12}}>
          <button className="btn-outline-sm" onClick={onClose}>Close</button>
          <button className="btn-primary" onClick={() => {
            if (onGenerateRoadmap) onGenerateRoadmap();
            onClose();
          }}>
            <MI name="rocket_launch" size={16}/> Generate Roadmap
          </button>
        </div>
      </div>
    </div>
  )
}

export function GrantTab({onApply}:{onApply:()=>void}){
  return <div style={{overflowY:"auto"}}>
    <div className={s.pageHeader}>
      <div style={{display:"flex",alignItems:"center",gap:10}}><MI name="analytics" size={18} color="#904D00"/>
        <div className={s.pageTitle} style={{fontSize:28}}>Grant Match Details</div>
      </div>
      <div className={s.pageSub}>We analyzed 42 active funding sources against your profile. Here is why you match with this grant.</div>
    </div>
    <div style={{height:16}}/>
    <div className={s.grantLayout}>
      <div className={s.grantMain}>
        <div className={s.panel} style={{borderRadius:26,padding:18}}>
          <div style={{display:"flex",gap:16}}>
            <div style={{flex:1}}>
              <div style={{display:"flex",flexWrap:"wrap",gap:8}}>
                <span className={s.tag} style={{background:"#F2F4F6",color:"#3D494D"}}>DOE - EERE</span>
                <span className={s.tag} style={{background:"#EDEBFF",color:"#494BD6"}}><MI name="auto_awesome" size={12} color="#494BD6"/>High Confidence</span>
              </div>
              <div style={{height:12}}/>
              <div style={{fontSize:20,fontWeight:900,lineHeight:1.12,letterSpacing:-0.5,color:"#191C1E"}}>Clean Energy Infrastructure Deployment Grant</div>
              <div style={{height:8}}/>
              <div style={{color:"#3D494D",fontSize:13}}>FOA-0002894 - Deadline: Oct 15, 2024</div>
            </div>
            <div style={{width:76,height:76,borderRadius:"50%",background:"#FFDDB6",border:"1px solid rgba(144,77,0,0.14)",display:"flex",flexDirection:"column",alignItems:"center",justifyContent:"center",flexShrink:0}}>
              <div style={{fontSize:24,fontWeight:900,color:"#904D00",letterSpacing:-1}}>94%</div>
              <div style={{fontSize:9,fontWeight:800,color:"#904D00",letterSpacing:2}}>MATCH</div>
            </div>
          </div>
          <div style={{height:20}}/>
          <div style={{display:"flex",gap:20}}>
            <div style={{flex:1}}>
              <div style={{display:"flex",alignItems:"center",gap:8}}><MI name="verified" size={14} color="#904D00"/><span style={{fontWeight:900,letterSpacing:1,fontSize:12,color:"#191C1E"}}>WHY YOU'RE A STRONG FIT</span></div>
              <div style={{height:10}}/>
              <div className={s.evidenceTile}><div className={s.evidenceIcon} style={{background:"rgba(0,103,128,0.12)"}}><MI name="eco" size={14} color="#006780"/></div><div><div style={{fontWeight:700,color:"#191C1E",fontSize:13}}>Aligns with 'Decarbonization'</div><div style={{height:4}}/><div style={{color:"#3D494D",lineHeight:1.4,fontSize:12}}>Your past project "Solar Grid V2" proves you have the required experience.</div></div></div>
              <div className={s.evidenceTile}><div className={s.evidenceIcon} style={{background:"rgba(0,103,128,0.12)"}}><MI name="groups" size={14} color="#006780"/></div><div><div style={{fontWeight:700,color:"#191C1E",fontSize:13}}>Community Benefit Confirmed</div><div style={{height:4}}/><div style={{color:"#3D494D",lineHeight:1.4,fontSize:12}}>You already partner with 3 local workforce development boards.</div></div></div>
            </div>
            <div style={{flex:1}}>
              <div className={s.gapPanel}><MI name="error" size={14} color="#BA1A1A"/><div><div style={{color:"#BA1A1A",fontWeight:900,letterSpacing:1,fontSize:12}}>WHAT'S MISSING</div><div style={{height:8}}/><div style={{color:"#93000A",lineHeight:1.4,fontSize:13}}>Export Compliance Certificate (Form 89-B). We need this before we can submit.</div></div></div>
              <div style={{height:18}}/>
              <div style={{textAlign:"center",color:"#3D494D",fontSize:12,lineHeight:1.4}}>Ready to start? We'll automatically draft your proposal steps.</div>
              <div style={{height:10}}/>
              <button className="btn-amber" onClick={onApply}><MI name="route" size={16} color="#fff"/>Start Application</button>
            </div>
          </div>
        </div>
      </div>
      <div className={s.grantSide}>
        <div style={{display:"flex",justifyContent:"space-between",marginBottom:14}}><span style={{fontWeight:900,letterSpacing:2,fontSize:12,color:"#191C1E"}}>OTHER HIGH MATCHES</span><span style={{color:"#904D00",fontWeight:700,fontSize:12}}>View All</span></div>
        <MatchCard source="NSF - Convergence Accelerator" title="Sustainable Materials Development" score="88%" body="Strong patent overlap detected in polymer synthesis sub-category." onApply={onApply}/>
        <MatchCard source="NIH - R01 Research" title="Advanced Biomarkers for Early Detection" score="82%" body="Gap: Lacking required preliminary in-vivo data subset." hasGap onApply={onApply}/>
        <div className={s.connectCard}>
          <div style={{width:30,height:30,borderRadius:"50%",background:"#F2F4F6",display:"inline-flex",alignItems:"center",justifyContent:"center"}}><MI name="add_link" size={15} color="#3D494D"/></div>
          <div style={{height:10}}/>
          <div style={{fontWeight:900,fontSize:13,color:"#191C1E"}}>Connect New Data Source</div>
          <div style={{height:4}}/>
          <div style={{color:"#3D494D",fontSize:12}}>Expand evaluation context</div>
        </div>
      </div>
    </div>
  </div>;
}

function MatchCard({source,title,score,body,hasGap,onApply}:{source:string;title:string;score:string;body:string;hasGap?:boolean;onApply:()=>void}){
  return <div className={s.matchCard}>
    <div style={{display:"flex",justifyContent:"space-between"}}><span style={{color:"#3D494D",fontWeight:600,fontSize:12}}>{source}</span><span className={s.tag} style={{background:"#F2F4F6",color:"#006780"}}>{score}</span></div>
    <div style={{height:10}}/>
    <div style={{fontSize:14,fontWeight:900,lineHeight:1.15,color:"#191C1E"}}>{title}</div>
    <div style={{height:10}}/>
    <div style={{display:"flex",gap:8,alignItems:"flex-start"}}><div style={{width:5,height:5,borderRadius:"50%",background:hasGap?"#BA1A1A":"#494BD6",marginTop:6,flexShrink:0}}/><span style={{color:hasGap?"#7D1A1A":"#3D494D",lineHeight:1.35,fontSize:12}}>{body}</span></div>
    <div style={{height:10,display:"flex",justifyContent:"flex-end"}}/>
    <div style={{display:"flex",justifyContent:"flex-end"}}><button className="btn-soft" onClick={onApply}><MI name="route" size={14}/>Apply</button></div>
  </div>;
}
