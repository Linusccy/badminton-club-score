import React, { useState, useMemo, useEffect } from 'react';
import { 
  Trophy, History, PlusCircle, Users, Calendar, Sword, BarChart3, UserPlus, Trash2, Edit2, Loader2, Cloud
} from 'lucide-react';

const COLORS = {
  primary: '#E11D48',
  secondary: '#1E40AF',
  background: '#F8FAFC'
};

// !!! 請將此處替換為你的 Google Apps Script URL !!!
const GAS_URL = "YOUR_GAS_URL";

const INITIAL_MEMBERS = ['嬌', '車長', '牙朗', '勤', '文西', '朱仔', '輝哥', '駱sir', 'BRO', '子謙', '馮善基', '巴士佬'];

const App = () => {
  const [view, setView] = useState('leaderboard'); 
  const [statsType, setStatsType] = useState('Individual');
  const [matchType, setMatchType] = useState('Doubles');
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [isLoading, setIsLoading] = useState(false);
  
  const [members, setMembers] = useState(() => {
    const saved = localStorage.getItem('scaa_members_2026');
    return saved ? JSON.parse(saved) : INITIAL_MEMBERS;
  });

  const [history, setHistory] = useState([]);

  const [formData, setFormData] = useState({
    id: null, w1: '', w2: '', l1: '', l2: '', sW: 21, sL: 15, gamePoint: 21
  });

  const [isEditing, setIsEditing] = useState(false);

  // 從 Google Sheets 獲取數據
  const fetchData = async () => {
    if (GAS_URL === "YOUR_GAS_URL") return;
    setIsLoading(true);
    try {
      const response = await fetch(GAS_URL, { method: 'POST', body: JSON.stringify({ action: 'get' }) });
      const data = await response.json();
      setHistory(data.sort((a, b) => b.id - a.id));
    } catch (error) {
      console.error("Fetch error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    localStorage.setItem('scaa_members_2026', JSON.stringify(members));
  }, [members]);

  const statsAnalysis = useMemo(() => {
    const players = {};
    const pairs = {};
    const doublesHistory = history.filter(m => m.type === 'Doubles');

    doublesHistory.forEach(m => {
      const winners = m.winner;
      const losers = m.loser;
      const wPair = winners.slice().sort().join(' / ');
      const lPair = losers.slice().sort().join(' / ');
      
      if (!pairs[wPair]) pairs[wPair] = { pts: 0, wins: 0, played: 0 };
      if (!pairs[lPair]) pairs[lPair] = { pts: 0, wins: 0, played: 0 };
      pairs[wPair].pts += m.pts;
      pairs[wPair].wins += 1;
      pairs[wPair].played += 1;
      pairs[lPair].pts -= m.pts;
      pairs[lPair].played += 1;

      [...winners, ...losers].forEach(p => {
        if (!players[p]) players[p] = { pts: 0, wins: 0, played: 0, opponents: {}, partners: {} };
      });

      winners.forEach(w => {
        players[w].pts += m.pts;
        players[w].wins += 1;
        players[w].played += 1;
        winners.filter(o => o !== w).forEach(partner => {
          if (!players[w].partners[partner]) players[w].partners[partner] = { wins: 0, losses: 0 };
          players[w].partners[partner].wins += 1;
        });
        losers.forEach(loser => {
          if (!players[w].opponents[loser]) players[w].opponents[loser] = { wins: 0, losses: 0 };
          players[w].opponents[loser].wins += 1;
        });
      });

      losers.forEach(l => {
        players[l].pts -= m.pts;
        players[l].played += 1;
        losers.filter(o => o !== l).forEach(partner => {
          if (!players[l].partners[partner]) players[l].partners[partner] = { wins: 0, losses: 0 };
          players[l].partners[partner].losses += 1;
        });
        winners.forEach(winner => {
          if (!players[l].opponents[winner]) players[l].opponents[winner] = { wins: 0, losses: 0 };
          players[l].opponents[winner].losses += 1;
        });
      });
    });

    const playerList = Object.keys(players).map(name => {
      const data = players[name];
      const pEnt = Object.entries(data.partners);
      const bestPartner = pEnt.length > 0 ? pEnt.map(([n, r]) => ({ n, rate: r.wins/(r.wins+r.losses), t: r.wins+r.losses })).sort((a,b)=>b.rate-a.rate||b.t-a.t)[0]?.n : '-';
      const oEnt = Object.entries(data.opponents);
      const oStats = oEnt.map(([n, r]) => ({ n, rate: r.wins/(r.wins+r.losses), t: r.wins+r.losses }));
      const victim = oStats.length > 0 ? oStats.sort((a,b)=>b.rate-a.rate||b.t-a.t)[0]?.n : '-';
      return { name, pts: data.pts, played: data.played, winRate: data.played > 0 ? ((data.wins/data.played)*100).toFixed(0)+'%' : '0%', bestPartner, victim };
    }).sort((a,b) => b.pts - a.pts);

    const pairList = Object.keys(pairs).map(pair => ({ pair, pts: pairs[pair].pts, winRate: ((pairs[pair].wins/pairs[pair].played)*100).toFixed(0)+'%', played: pairs[pair].played })).sort((a,b)=>b.pts-a.pts);
    return { playerList, pairList };
  }, [history]);

  const handleSubmitMatch = async () => {
    setIsLoading(true);
    let calculatedPts = formData.gamePoint == 21 ? (formData.sL < 10 ? 3 : formData.sL < 15 ? 2 : 1) : 1;
    const newMatch = {
      id: isEditing ? formData.id : Date.now(),
      date: selectedDate,
      type: matchType,
      gamePoint: formData.gamePoint,
      winner: matchType === 'Doubles' ? [formData.w1, formData.w2] : [formData.w1],
      loser: matchType === 'Doubles' ? [formData.l1, formData.l2] : [formData.l1],
      score: [Number(formData.sW), Number(formData.sL)],
      pts: calculatedPts
    };

    try {
      // 發送到 Google Sheets
      await fetch(GAS_URL, {
        method: 'POST',
        mode: 'no-cors', // GAS Web App 通常需要此模式
        body: JSON.stringify({ action: 'add', match: newMatch })
      });
      
      // 更新本地狀態
      setHistory(prev => [newMatch, ...prev]);
      setFormData({ id: null, w1: '', w2: '', l1: '', l2: '', sW: 21, sL: 15, gamePoint: 21 });
      setView('history');
      setIsEditing(false);
    } catch (error) {
      console.error("Save error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddNewMember = () => {
    const name = prompt("請輸入新球員名稱：")?.trim();
    if (name && !members.includes(name)) {
      setMembers(prev => [...prev, name]);
    }
  };

  const PlayerSelect = ({ value, onChange, label, colorClass }) => (
    <div className={`p-4 rounded-xl border ${colorClass}`}>
      <label className="text-xs font-black uppercase mb-2 block text-center opacity-70">{label}</label>
      <select value={value} onChange={(e) => e.target.value === "ADD_NEW" ? handleAddNewMember() : onChange(e.target.value)} className="w-full p-3 rounded-lg border font-bold text-sm bg-white">
        <option value="">選擇球員...</option>
        {members.map(m => <option key={m} value={m}>{m}</option>)}
        <option value="ADD_NEW" className="text-blue-600 font-bold">+ 新增球員...</option>
      </select>
    </div>
  );

  return (
    <div className="min-h-screen flex flex-col font-sans pb-20" style={{ backgroundColor: COLORS.background }}>
      <header className="bg-white shadow-sm border-b-2 sticky top-0 z-30" style={{ borderColor: COLORS.primary }}>
        <div className="max-w-md mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
             <div className="w-10 h-10 bg-red-600 rounded-full flex items-center justify-center text-white font-black text-xl italic shadow-inner">南</div>
             <div className="flex flex-col">
                <h1 className="text-xl font-black tracking-tight text-blue-900 leading-none">南華體育會</h1>
                <span className="text-[10px] font-bold text-slate-400 tracking-widest uppercase italic flex items-center gap-1">
                  <Cloud size={10} /> Google Sheet Syncing
                </span>
             </div>
          </div>
          {isLoading && <Loader2 className="animate-spin text-red-600" size={20} />}
        </div>
      </header>

      <nav className="bg-white border-b sticky top-[72px] z-20">
        <div className="max-w-md mx-auto flex overflow-x-auto no-scrollbar px-4 py-2 gap-2">
          {[{ id: 'leaderboard', label: '排名', icon: Trophy }, { id: 'daily', label: '今日', icon: Calendar }, { id: 'stats', label: '統計', icon: BarChart3 }, { id: 'members', label: '成員', icon: Users }, { id: 'history', label: '歷史', icon: History }].map(tab => (
            <button key={tab.id} onClick={() => { setView(tab.id); setIsEditing(false); }} className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold transition-all flex-shrink-0 ${view === tab.id ? 'bg-blue-900 text-white shadow-md' : 'bg-slate-100 text-slate-500'}`}>
              <tab.icon size={14} />{tab.label}
            </button>
          ))}
        </div>
      </nav>

      <main className="flex-1 max-w-md mx-auto w-full p-4">
        {view === 'leaderboard' && (
          <div className="space-y-4 animate-in fade-in">
            <h2 className="text-xl font-bold text-slate-800 italic">年度積分榜 (雙打)</h2>
            {statsAnalysis.playerList.map((p, idx) => (
              <div key={p.name} className="bg-white rounded-xl p-4 shadow-sm border flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <span className={`text-xl font-black ${idx < 3 ? 'text-red-600' : 'text-slate-200'}`}>#{idx + 1}</span>
                  <div><p className="font-bold text-slate-800">{p.name}</p><p className="text-[10px] text-slate-500 font-bold uppercase">{p.winRate} 勝率 • {p.played} 場</p></div>
                </div>
                <p className={`text-2xl font-black ${idx < 3 ? 'text-blue-900' : 'text-slate-700'}`}>{p.pts}</p>
              </div>
            ))}
          </div>
        )}

        {view === 'stats' && (
          <div className="space-y-4 animate-in fade-in pb-10">
            <div className="flex justify-between items-center mb-2">
              <h2 className="text-xl font-bold text-slate-800">數據深挖</h2>
              <div className="flex bg-slate-200 p-1 rounded-lg">
                {['Individual', 'Pairs'].map(t => (
                  <button key={t} onClick={() => setStatsType(t)} className={`px-3 py-1 text-[10px] font-black rounded-md ${statsType === t ? 'bg-white text-blue-900 shadow-sm' : 'text-slate-500'}`}>{t === 'Individual' ? '個人' : '組合'}</button>
                ))}
              </div>
            </div>
            <div className="bg-white rounded-xl shadow-sm border overflow-x-auto">
              <table className="w-full text-left min-w-[500px]">
                <thead className="bg-slate-50 border-b">
                  <tr className="text-[10px] font-black text-slate-400 uppercase">
                    <th className="px-4 py-3">{statsType === 'Individual' ? '球員' : '組合'}</th>
                    <th className="text-center px-2 py-3">積分</th>
                    <th className="text-center px-2 py-3">勝率</th>
                    {statsType === 'Individual' && <th className="px-4 py-3 text-blue-600">最佳拍檔</th>}
                    {statsType === 'Individual' && <th className="px-4 py-3 text-emerald-600">苦主</th>}
                  </tr>
                </thead>
                <tbody className="divide-y text-sm">
                  {(statsType === 'Individual' ? statsAnalysis.playerList : statsAnalysis.pairList).map((p, i) => (
                    <tr key={i}>
                      <td className="px-4 py-4 font-bold">{p.name || p.pair}</td>
                      <td className={`text-center font-black ${p.pts > 0 ? 'text-blue-600' : 'text-red-600'}`}>{p.pts}</td>
                      <td className="text-center font-bold text-slate-500">{p.winRate}</td>
                      {statsType === 'Individual' && <td className="px-4 py-4 text-xs font-bold text-blue-500">{p.bestPartner}</td>}
                      {statsType === 'Individual' && <td className="px-4 py-4 text-xs font-bold text-emerald-500">{p.victim}</td>}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {view === 'history' && (
          <div className="space-y-4 animate-in fade-in">
            <div className="flex justify-between items-center">
               <h2 className="text-xl font-bold text-slate-800 italic">歷史紀錄</h2>
               <button onClick={fetchData} className="text-[10px] font-bold text-blue-600 underline">重新整理</button>
            </div>
            {history.length === 0 && !isLoading && <p className="text-center py-10 text-slate-400 font-bold">尚無雲端紀錄</p>}
            {history.map(item => (
              <div key={item.id} className="bg-white rounded-xl p-4 shadow-sm border group">
                <div className="flex justify-between items-start mb-2 text-[10px] text-slate-400 font-black uppercase">
                  <span>{item.date} • {item.gamePoint}分制</span>
                  <div className="flex gap-2">
                    <button onClick={() => { setIsEditing(true); setFormData({...item, w1: item.winner[0], w2: item.winner[1], l1: item.loser[0], l2: item.loser[1], sW: item.score[0], sL: item.score[1]}); setView('input'); }} className="p-1 hover:text-blue-600"><Edit2 size={14}/></button>
                  </div>
                </div>
                <div className="flex justify-between items-center text-sm font-bold">
                  <div className="flex-1 text-blue-800 truncate">{item.winner.join(' / ')}</div>
                  <div className="px-3 py-1 bg-slate-50 border rounded-full text-[10px] mx-2 shrink-0">{item.score[0]}:{item.score[1]}</div>
                  <div className="flex-1 text-right text-slate-400 truncate">{item.loser.join(' / ')}</div>
                </div>
              </div>
            ))}
          </div>
        )}

        {view === 'input' && (
           <div className="space-y-6 animate-in slide-in-from-bottom-4">
             <div className="flex justify-between items-center"><h2 className="text-xl font-bold text-slate-800">{isEditing ? '修改紀錄' : '錄入賽果'}</h2></div>
             <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1"><label className="text-[10px] font-bold text-slate-400 uppercase">項目</label>
                    <div className="flex p-1 bg-slate-200 rounded-lg">
                      {['Singles', 'Doubles'].map(m => (
                        <button key={m} onClick={() => setMatchType(m)} className={`flex-1 py-1.5 text-xs font-bold rounded-md ${matchType === m ? 'bg-white shadow text-blue-800' : 'text-slate-600'}`}>{m === 'Singles' ? '單打' : '雙打'}</button>
                      ))}
                    </div>
                  </div>
                  <div className="space-y-1"><label className="text-[10px] font-bold text-slate-400 uppercase">日期</label>
                    <input type="date" value={selectedDate} onChange={e => setSelectedDate(e.target.value)} className="w-full p-2 border rounded-lg text-xs font-bold bg-white" />
                  </div>
                </div>
                <div className="space-y-3">
                  <PlayerSelect label="勝方 Winner" colorClass="bg-blue-50 border-blue-100 text-blue-700" value={formData.w1} onChange={val => setFormData({...formData, w1: val})} />
                  {matchType === 'Doubles' && <PlayerSelect label="勝方 Partner" colorClass="bg-blue-50 border-blue-100 text-blue-700" value={formData.w2} onChange={val => setFormData({...formData, w2: val})} />}
                  <div className="py-2 flex items-center justify-center"><Sword className="text-slate-200" size={24}/></div>
                  <PlayerSelect label="負方 Loser" colorClass="bg-red-50 border-red-100 text-red-700" value={formData.l1} onChange={val => setFormData({...formData, l1: val})} />
                  {matchType === 'Doubles' && <PlayerSelect label="負方 Partner" colorClass="bg-red-50 border-red-100 text-red-700" value={formData.l2} onChange={val => setFormData({...formData, l2: val})} />}
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center"><label className="text-[10px] font-bold text-slate-400">勝方得分</label><input type="number" value={formData.sW} onChange={e=>setFormData({...formData, sW: e.target.value})} className="w-full p-3 border rounded-lg font-black text-center text-xl text-blue-700" /></div>
                  <div className="text-center"><label className="text-[10px] font-bold text-slate-400">負方得分</label><input type="number" value={formData.sL} onChange={e=>setFormData({...formData, sL: e.target.value})} className="w-full p-3 border rounded-lg font-black text-center text-xl text-red-700" /></div>
                </div>
                <button 
                  disabled={isLoading}
                  onClick={handleSubmitMatch} 
                  className="w-full py-4 bg-red-600 text-white font-black rounded-xl shadow-lg uppercase active:scale-95 transition-all disabled:bg-slate-300"
                >
                  {isLoading ? '正在同步...' : '保存至雲端 Google Sheets'}
                </button>
             </div>
           </div>
        )}

        {view === 'daily' && (
          <div className="space-y-4 animate-in fade-in">
            <div className="flex justify-between items-center"><h2 className="text-xl font-bold text-slate-800">今日戰績</h2><input type="date" value={selectedDate} onChange={e=>setSelectedDate(e.target.value)} className="p-1 border rounded text-[10px] font-bold" /></div>
            <div className="bg-white rounded-xl shadow-sm border p-4 text-center">
              {(() => {
                const daily = history.filter(m => m.date === selectedDate);
                const pMap = {};
                daily.forEach(m => {
                  m.winner.forEach(n => { if(!pMap[n]) pMap[n]={p:0,w:0,g:0}; pMap[n].p+=m.pts; pMap[n].w++; pMap[n].g++; });
                  m.loser.forEach(n => { if(!pMap[n]) pMap[n]={p:0,w:0,g:0}; pMap[n].p-=m.pts; pMap[n].g++; });
                });
                const sorted = Object.keys(pMap).map(n=>({n, ...pMap[n]})).sort((a,b)=>b.p-a.p);
                return sorted.length > 0 ? sorted.map(p=>(
                  <div key={p.n} className="flex justify-between py-2 border-b last:border-0 items-center">
                    <span className="font-bold">{p.n}</span>
                    <div className="flex gap-4">
                      <span className="text-[10px] font-black text-slate-400">{p.w}W - {p.g-p.w}L</span>
                      <span className={`font-black ${p.p > 0 ? 'text-blue-600' : 'text-red-500'}`}>{p.p > 0 ? `+${p.p}` : p.p}</span>
                    </div>
                  </div>
                )) : <div className="py-10 text-slate-300 italic text-sm">今日尚無紀錄</div>;
              })()}
            </div>
          </div>
        )}

        {view === 'members' && (
          <div className="space-y-4 animate-in fade-in">
            <div className="flex justify-between items-center"><h2 className="text-xl font-bold text-slate-800">成員管理</h2><button onClick={handleAddNewMember} className="bg-blue-50 text-blue-600 px-3 py-1.5 rounded-full text-xs font-bold flex items-center gap-1"><UserPlus size={14}/>新增</button></div>
            <div className="grid grid-cols-2 gap-2">
              {members.map(m => (
                <div key={m} className="p-3 bg-white border rounded-xl flex justify-between items-center shadow-sm">
                  <span className="font-bold text-slate-700">{m}</span>
                  <button onClick={() => setMembers(prev => prev.filter(x => x !== m))} className="text-slate-300 hover:text-red-500"><Trash2 size={14}/></button>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      <button onClick={() => { setIsEditing(false); setView('input'); }} className={`fixed bottom-6 right-6 w-14 h-14 bg-red-600 rounded-full flex items-center justify-center text-white shadow-2xl z-40 active:scale-95 transition-all ${view === 'input' ? 'hidden' : ''}`}><PlusCircle size={32} /></button>
    </div>
  );
};

export default App;