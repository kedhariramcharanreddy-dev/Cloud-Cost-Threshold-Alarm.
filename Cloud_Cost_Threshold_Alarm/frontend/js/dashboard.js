
let chart;
const $ = id => document.getElementById(id);
const money = n => "$" + Number(n || 0).toFixed(2);
function toast(message){const el=$("toast");el.textContent=message;el.classList.add("show");setTimeout(()=>el.classList.remove("show"),2600)}
function setStatus(status){
  const map={NORMAL:["Normal","Spending is within your configured budget.","#18b58e"],WARNING:["Warning","Spending has reached your warning threshold.","#e4a12d"],OVER_BUDGET:["Over budget","Your spending has reached or exceeded the monthly budget.","#e15c57"]};
  const item=map[status]||map.NORMAL;
  $("healthStatus").textContent=item[0].toUpperCase();$("statusText").textContent=item[0].toUpperCase();
  $("healthNote").textContent=item[1];$("statusDot").style.background=item[2];
}
function renderChart(daily){
  const labels=daily.map(x=>new Date(x.date+"T00:00:00").toLocaleDateString(undefined,{day:"numeric",month:"short"}));
  const values=daily.map(x=>x.amount);
  if(chart) chart.destroy();
  chart=new Chart($("spendChart"),{type:"line",data:{labels,datasets:[{label:"Daily spend",data:values,borderColor:"#16b8a6",backgroundColor:"rgba(22,184,166,.10)",fill:true,tension:.38,pointRadius:2.5,pointHoverRadius:5,borderWidth:2}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>money(c.raw)}}},scales:{x:{grid:{display:false},ticks:{color:"#9aa5b4",font:{size:9},maxTicksLimit:8}},y:{beginAtZero:true,grid:{color:"#eef1f5"},ticks:{color:"#9aa5b4",font:{size:9},callback:v=>"$"+v}}}}});
}
async function api(url,options={}){const res=await fetch(url,{headers:{"Content-Type":"application/json"},...options});const data=await res.json();if(!res.ok)throw new Error(data.error||"Request failed");return data}
async function loadDashboard(){
  try{
    const [costs,settings,alerts,device]=await Promise.all([api("/api/costs"),api("/api/settings"),api("/api/alerts"),api("/api/device/status")]);
    $("errorBanner").classList.add("hidden");
    $("dataSource").textContent=costs.is_demo?"DEMO DATA":(costs.error?"AWS ERROR":"AWS LIVE");
    $("spendValue").textContent=money(costs.monthly_spend);$("budgetValue").textContent=money(costs.monthly_budget);
    $("thresholdValue").textContent=money(costs.warning_threshold);$("remainingValue").textContent=money(costs.remaining_budget);
    $("thresholdPercent").textContent=`At ${settings.warning_percent}% of budget`;
    const used=costs.monthly_budget?costs.monthly_spend/costs.monthly_budget*100:0;
    $("usedPercent").textContent=`${Math.round(used)}% used`; $("budgetProgress").style.width=Math.min(used,100)+"%";
    $("budgetProgress").style.background=costs.status==="OVER_BUDGET"?"#e15c57":costs.status==="WARNING"?"#e4a12d":"#16b8a6";
    $("healthPercent").textContent=Math.round(used)+"%";$("healthRing").style.background=`conic-gradient(${costs.status==="OVER_BUDGET"?"#e15c57":costs.status==="WARNING"?"#e4a12d":"#16b8a6"} ${Math.min(used,100)*3.6}deg,#edf2f6 0deg)`;
    $("healthSpent").textContent=money(costs.monthly_spend);$("healthLimit").textContent=money(costs.monthly_budget);setStatus(costs.status);
    $("budgetInput").value=settings.monthly_budget;$("warningInput").value=settings.warning_percent;
    $("deviceBadge").textContent=device.connected?"ONLINE":"OFFLINE";$("deviceBadge").className="connection-badge "+(device.connected?"online":"offline");
    $("deviceConnection").textContent=device.connected?"Connected":"Not connected";
    $("deviceLastSeen").textContent=device.last_seen?new Date(device.last_seen).toLocaleString():"No heartbeat received";
    $("deviceLastStatus").textContent=device.last_status||"UNKNOWN";
    $("alertRows").innerHTML=alerts.length?alerts.map(a=>`<tr><td>${escapeHtml(a.message)}</td><td>${money(a.spend)}</td><td>${money(a.budget)}</td><td>${new Date(a.timestamp).toLocaleString()}</td><td><span class="status-chip ${a.status==="WARNING"?"chip-warning":a.status==="OVER_BUDGET"?"chip-over":"chip-normal"}">${a.status.replace("_"," ")}</span></td></tr>`).join(""):'<tr><td colspan="5" class="empty">No alerts yet. Use “Test alert” to verify the alert centre.</td></tr>';
    renderChart(costs.daily||[]);
    if(costs.error)$("errorBanner").textContent="AWS Cost Explorer could not be reached. Showing an unavailable state rather than live cost data.";
  }catch(e){$("errorBanner").textContent=e.message;$("errorBanner").classList.remove("hidden")}
}
function escapeHtml(s){return String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]))}
$("settingsForm").addEventListener("submit",async e=>{e.preventDefault();try{await api("/api/settings",{method:"POST",body:JSON.stringify({monthly_budget:$("budgetInput").value,warning_percent:$("warningInput").value})});$("settingsMessage").textContent="Settings saved successfully.";toast("Budget settings updated.");await loadDashboard()}catch(err){$("settingsMessage").textContent=err.message;$("settingsMessage").style.color="#d6534e"}});
$("testAlertBtn").addEventListener("click",async()=>{try{const result=await api("/api/test-alert",{method:"POST",body:JSON.stringify({status:"WARNING"})});toast("Test alert created. "+result.sns.message);await loadDashboard()}catch(e){toast(e.message)}});
$("refreshBtn").addEventListener("click",()=>{loadDashboard();toast("Dashboard refreshed")});
loadDashboard();setInterval(loadDashboard,30000);
