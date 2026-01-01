import React, { useState, useMemo, useEffect } from 'react';
import { 
  Trophy, 
  History, 
  PlusCircle, 
  Users, 
  User, 
  Calendar,
  Sword,
  BarChart3,
  UserPlus,
  ChevronDown,
  Medal,
  Info,
  AlertCircle,
  Trash2,
  Edit2,
  X,
  Check,
  UserCheck,
  Users2,
  Settings,
  ShieldCheck,
  ShieldAlert,
  RotateCcw
} from 'lucide-react';

const COLORS = {
  primary: '#E11D48',
  secondary: '#1E40AF',
  background: '#F8FAFC',
};

const INITIAL_MEMBERS = ['嬌', '車長', '牙朗', '勤', '文西', '朱仔', '輝哥', '駱sir', 'BRO', '子謙', '馮善基', '巴士佬'];

const App = () => {
  const [isAdmin, setIsAdmin] = useState(false);
  const [view, setView] = useState('leaderboard'); 
  const [statsType, setStatsType] = useState('Individual');
  const [matchType, setMatchType] = useState('Doubles');
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  
  const [members, setMembers] = useState(() => {
    const saved = localStorage.getItem('scaa_members_v3');
    return saved ? JSON.parse(saved) : INITIAL_MEMBERS;
  });

  const [history, setHistory] = useState(() => {
    const saved = localStorage.getItem('scaa_history_v3');
    return saved ? JSON.parse(saved) : [];
  });

  useEffect(() => {
    localStorage.setItem('scaa_members_v3', JSON.stringify(members));
  }, [members]);

  useEffect(() => {
    localStorage.setItem('scaa_history_v3', JSON.stringify(history));
  }, [history]);

  const [formData, setFormData] = useState({
    id: null, w1: '', w2: '', l1: '', l2: '', sW: 21, sL: 15, gamePoint: 21
  });
  const [isEditing, setIsEditing] = useState(false);

  const formatPoints = (pts, gp) => {
    if (gp === 11) return "+1";
    if (pts === 3) return "3炒";
    if (pts === 2) return "2炒";
    return `+${pts}`;
  };

  const handleAddNewMember = () => {
    const name = prompt("請輸入新球員名稱：");
    if (name && name.trim()) {
      if (members.includes(name.trim())) {
        alert("球員已存在");
        return name.trim();
      }
      setMembers(prev => [...prev, name.trim()]);
      return name.trim();
    }
    return null;
  };

  const validationError = useMemo(() => {
    const selected = [formData.w1, formData.w2, formData.l1, formData.l2].filter(Boolean);
    const unique = new Set(selected);
    if (selected.length !== unique.size) return "同一名球員不能出現在多個位置";
    if (!formData.w1 || !formData.l1) return "請選擇球員";
    if (matchType === 'Doubles' && (!formData.w2 || !formData.l2)) return "雙打需要四名球員";
    return null;
  }, [formData, matchType]);

  const statsAnalysis = useMemo(() => {
    const players = {};
    const pairs = {};

    // 關鍵更改：僅過濾雙打比賽進行統計
    const doublesHistory = history.filter(m => m.type === 'Doubles');

    doublesHistory.forEach(m => {
      const winners = m.winner;
      const losers = m.loser;

      // 組合統計 (僅限雙打)
      const wPair = winners.slice().sort().join(' / ');
      const lPair = losers.slice().sort().join(' / ');
      [wPair, lPair].forEach(p => { if (!pairs[p]) pairs[p] = { pts: 0, wins: 0, played: 0 }; });
      pairs[wPair].pts += m.pts;
      pairs[wPair].wins += 1;
      pairs[wPair].played += 1;
      pairs[lPair].pts -= m.pts;
      pairs[lPair].played += 1;

      // 個人統計 (僅從雙打數據中提取)
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
      const partnerEntries = Object.entries(data.partners);
      const bestPartner = partnerEntries.length > 0 
        ? partnerEntries.map(([pName, r]) => ({ name: pName, rate: r.wins / (r.wins + r.losses), total: r.wins + r.losses }))
            .sort((a, b) => b.rate - a.rate || b.total - a.total)[0]?.name 
        : '-';

      const opponentEntries = Object.entries(data.opponents);
      const opponentStats = opponentEntries.map(([oName, r]) => ({ name: oName, rate: r.wins / (r.wins + r.losses), total: r.wins + r.losses }));
      
      const victim = opponentStats.length > 0 
        ? opponentStats.sort((a, b) => b.rate - a.rate || b.total - a.total)[0]?.name 
        : '-';
      
      const nemesis = opponentStats.length > 0 
        ? opponentStats.sort((a, b) => a.rate - b.rate || b.total - a.total)[0]?.name 
        : '-';

      return { 
        name, 
        pts: data.pts, 
        played: data.played,
        winRate: data.played > 0 ? ((data.wins / data.played) * 100).toFixed(0) + '%' : '0%', 
        bestPartner, 
        victim, 
        nemesis 
      };
    }).sort((a,b) => b.pts - a.pts);

    const pairList = Object.keys(pairs).map(pair => ({ 
      pair, 
      pts: pairs[pair].pts, 
      winRate: ((pairs[pair].wins / pairs[pair].played) * 100).toFixed(0) + '%', 
      played: pairs[pair].played 
    })).sort((a, b) => b.pts - a.pts);

    return { playerList, pairList };
  }, [history]);

  const handleSubmitMatch = () => {
    if (validationError) return;
    
    let calculatedPts = 1;
    if (formData.gamePoint == 21) {
      calculatedPts = (formData.sL < 10 ? 3 : formData.sL < 15 ? 2 : 1);
    } else {
      calculatedPts = 1; // 11分制固定 1 分
    }

    const matchData = {
      id: isEditing ? formData.id : Date.now(), 
      date: selectedDate, type: matchType, gamePoint: formData.gamePoint,
      winner: matchType === 'Doubles' ? [formData.w1, formData.w2] : [formData.w1],
      loser: matchType === 'Doubles' ? [formData.l1, formData.l2] : [formData.l1],
      score: [Number(formData.sW), Number(formData.sL)], pts: calculatedPts
    };

    if (isEditing) setHistory(history.map(m => m.id === formData.id ? matchData : m));
    else setHistory([matchData, ...history]);
    
    setFormData({ id: null, w1: '', w2: '', l1: '', l2: '', sW: 21, sL: 15, gamePoint: 21 });
    setView('history');
    setIsEditing(false);
  };

  const handleEditHistory = (match) => {
    setIsEditing(true);
    setMatchType(match.type);
    setSelectedDate(match.date);
    setFormData({
      id: match.id,
      w1: match.winner[0] || '',
      w2: match.winner[1] || '',
      l1: match.loser[0] || '',
      l2: match.loser[1] || '',
      sW: match.score[0],
      sL: match.score[1],
      gamePoint: match.gamePoint || 21
    });
    setView('input');
  };

  const handleDeleteHistory = (id) => {
    if (window.confirm("確定要刪除這場紀錄嗎？")) {
      setHistory(history.filter(m => m.id !== id));
    }
  };

  const handleEditMember = (oldName) => {
    const newName = prompt("球員新名字：", oldName);
    if (newName && newName !== oldName) {
      setMembers(members.map(m => m === oldName ? newName : m));
      setHistory(history.map(m => ({
        ...m,
        winner: m.winner.map(w => w === oldName ? newName : w),
        loser: m.loser.map(l => l === oldName ? newName : l)
      })));
    }
  };

  const PlayerSelect = ({ value, onChange, label, colorClass }) => (
    <div className={`p-4 rounded-xl border ${colorClass}`}>
      <label className="text-xs font-black uppercase mb-2 block text-center opacity-70">{label}</label>
      <select 
        value={value} 
        onChange={(e) => {
          if (e.target.value === "ADD_NEW") {
            const newName = handleAddNewMember();
            if (newName) onChange(newName);
          } else {
            onChange(e.target.value);
          }
        }} 
        className="w-full p-3 rounded-lg border font-bold text-sm bg-white"
      >
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
             <div className="flex flex-col -gap-1">
                <h1 className="text-xl font-black tracking-tight text-blue-900 leading-none">南華體育會</h1>
                <span className="text-[10px] font-bold text-slate-400 tracking-widest uppercase">SCAA Badminton</span>
             </div>
          </div>
          <div className="flex items-center gap-2">
            <span className={`text-[10px] font-bold bg-red-50 text-red-600 px-2 py-0.5 rounded-full uppercase`}>
              2026 Season
            </span>
          </div>
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
            <h2 className="text-xl font-bold text-slate-800">2026 年度積分榜 (雙打限定)</h2>
            {statsAnalysis.playerList.length > 0 ? (
              statsAnalysis.playerList.map((p, idx) => (
                <div key={p.name} className="bg-white rounded-xl p-4 shadow-sm border flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <span className={`text-xl font-black ${idx < 3 ? 'text-red-600' : 'text-slate-200'}`}>#{idx + 1}</span>
                    <div><p className="font-bold text-slate-800">{p.name}</p><p className="text-[10px] text-slate-500 font-bold uppercase tracking-tight">{p.winRate} 勝率 • {p.played} 場</p></div>
                  </div>
                  <div className="text-right"><p className={`text-2xl font-black ${idx < 3 ? 'text-blue-900' : 'text-slate-700'}`}>{p.pts}</p></div>
                </div>
              ))
            ) : (
              <div className="text-center py-20 text-slate-400 font-bold italic">尚無雙打比賽數據</div>
            )}
          </div>
        )}

        {view === 'stats' && (
          <div className="space-y-4 animate-in fade-in pb-10">
            <div className="flex justify-between items-center mb-2">
              <h2 className="text-xl font-bold text-slate-800">球員深度統計 (雙打)</h2>
              <div className="flex bg-slate-200 p-1 rounded-lg">
                {['Individual', 'Pairs'].map(t => (
                  <button key={t} onClick={() => setStatsType(t)} className={`px-3 py-1 text-[10px] font-black rounded-md ${statsType === t ? 'bg-white text-blue-900 shadow-sm' : 'text-slate-500'}`}>{t === 'Individual' ? '個人' : '組合'}</button>
                ))}
              </div>
            </div>

            {statsType === 'Individual' ? (
              <div className="bg-white rounded-2xl shadow-sm border overflow-x-auto">
                <table className="w-full text-left min-w-[600px]">
                  <thead className="bg-slate-50 border-b">
                    <tr>
                      <th className="px-4 py-3 text-[10px] font-black text-slate-400 uppercase">球員</th>
                      <th className="px-2 py-3 text-[10px] font-black text-slate-400 uppercase text-center">積分</th>
                      <th className="px-2 py-3 text-[10px] font-black text-slate-400 uppercase text-center">勝率</th>
                      <th className="px-2 py-3 text-[10px] font-black text-slate-400 uppercase text-center">場數</th>
                      <th className="px-4 py-3 text-[10px] font-black text-blue-500 uppercase text-center">最佳拍檔</th>
                      <th className="px-4 py-3 text-[10px] font-black text-emerald-500 uppercase text-center">苦主</th>
                      <th className="px-4 py-3 text-[10px] font-black text-red-500 uppercase text-center">死敵</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y text-sm">
                    {statsAnalysis.playerList.map((p, idx) => (
                      <tr key={idx}>
                        <td className="px-4 py-4 font-bold text-slate-800">{p.name}</td>
                        <td className={`px-2 py-4 font-black text-center ${p.pts > 0 ? 'text-blue-600' : 'text-red-600'}`}>{p.pts}</td>
                        <td className="px-2 py-4 text-center text-[11px] font-bold text-slate-600">{p.winRate}</td>
                        <td className="px-2 py-4 text-center text-[11px] text-slate-400">{p.played}</td>
                        <td className="px-4 py-4 text-center font-bold text-blue-500 text-[10px] bg-blue-50/30">{p.bestPartner}</td>
                        <td className="px-4 py-4 text-center font-bold text-emerald-500 text-[10px] bg-emerald-50/30">{p.victim}</td>
                        <td className="px-4 py-4 text-center font-bold text-red-500 text-[10px] bg-red-50/30">{p.nemesis}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="bg-white rounded-2xl shadow-sm border overflow-hidden">
                <table className="w-full text-left">
                  <thead className="bg-slate-50 border-b">
                    <tr><th className="px-4 py-3 text-[10px] font-black text-slate-400 uppercase">組合名稱</th><th className="px-2 py-3 text-[10px] font-black text-slate-400 uppercase text-center">總積分</th><th className="px-4 py-3 text-[10px] font-black text-slate-400 uppercase text-center">勝率</th></tr>
                  </thead>
                  <tbody className="divide-y text-sm">
                    {statsAnalysis.pairList.map((p, idx) => (
                      <tr key={idx}><td className="px-4 py-4 font-bold text-slate-800 text-[11px] leading-tight">{p.pair}</td><td className={`px-2 py-4 font-black text-center ${p.pts > 0 ? 'text-blue-600' : 'text-red-600'}`}>{p.pts}</td><td className="px-4 py-4 text-center font-black text-slate-700 text-[11px]">{p.winRate}</td></tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {view === 'members' && (
          <div className="space-y-6 animate-in fade-in pb-10">
            <div className="flex justify-between items-center">
               <h2 className="text-xl font-bold text-slate-800">成員名單</h2>
               <button onClick={handleAddNewMember} className="flex items-center gap-1 text-xs font-bold text-blue-600 bg-blue-50 px-3 py-1.5 rounded-full"><UserPlus size={14} /> 新增</button>
            </div>
            <div className="grid grid-cols-2 gap-2">
              {members.map(m => (
                <div key={m} className="p-3 bg-white border rounded-xl flex justify-between items-center shadow-sm">
                  <span className="font-bold text-slate-700">{m}</span>
                  <button onClick={() => handleEditMember(m)} className="p-1.5 text-blue-500 hover:bg-blue-50 rounded">
                    <Edit2 size={14}/>
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {view === 'history' && (
          <div className="space-y-4 animate-in fade-in">
            <h2 className="text-xl font-bold text-slate-800">對賽紀錄 (全)</h2>
            <div className="space-y-3">
              {history.length > 0 ? (
                history.map(item => (
                  <div key={item.id} className="bg-white rounded-xl p-4 shadow-sm border group relative">
                    <div className="flex justify-between items-start mb-2">
                      <span className="text-[10px] text-slate-400 font-black uppercase tracking-tight">{item.date} • {item.type === 'Doubles' ? '雙打' : '單打'} ({item.gamePoint}分制)</span>
                      <div className="flex gap-2 items-center">
                         <span className={`text-[10px] font-black px-2 py-0.5 rounded ${item.pts > 1 ? 'bg-amber-100 text-amber-700' : 'bg-blue-50 text-blue-600'}`}>{formatPoints(item.pts, item.gamePoint)}</span>
                         <button onClick={() => handleEditHistory(item)} className="p-1 text-slate-400 hover:text-blue-600 transition-colors"><Edit2 size={14}/></button>
                         <button onClick={() => handleDeleteHistory(item.id)} className="p-1 text-slate-400 hover:text-red-600 transition-colors"><Trash2 size={14}/></button>
                      </div>
                    </div>
                    <div className="flex justify-between items-center text-sm font-bold">
                      <div className="flex-1 text-blue-800 truncate">{item.winner.join(' / ')}</div>
                      <div className="px-3 py-1 bg-slate-50 border rounded-full text-xs font-black shadow-inner mx-2 shrink-0">
                        <span className="text-blue-600">{item.score[0]}</span>:<span className="text-red-500">{item.score[1]}</span>
                      </div>
                      <div className="flex-1 text-right text-slate-400 truncate">{item.loser.join(' / ')}</div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-20 text-slate-400 font-bold italic">尚無比賽紀錄</div>
              )}
            </div>
          </div>
        )}

        {view === 'input' && (
          <div className="space-y-6 animate-in slide-in-from-bottom-4">
            <div className="flex justify-between items-center">
               <h2 className="text-xl font-bold text-slate-800">{isEditing ? '修改紀錄' : '錄入新賽果'}</h2>
               {isEditing && <button onClick={() => { setIsEditing(false); setView('history'); }} className="text-xs font-bold text-slate-400">取消</button>}
            </div>
            
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1"><label className="text-[10px] font-bold text-slate-400 uppercase">項目</label>
                  <div className="flex p-1 bg-slate-200 rounded-lg">
                    {['Singles', 'Doubles'].map(m => (
                      <button key={m} onClick={() => setMatchType(m)} className={`flex-1 py-1.5 text-xs font-bold rounded-md ${matchType === m ? 'bg-white shadow text-blue-800' : 'text-slate-600'}`}>{m === 'Singles' ? '單打' : '雙打'}</button>
                    ))}
                  </div>
                </div>
                <div className="space-y-1"><label className="text-[10px] font-bold text-slate-400 uppercase">比賽分數</label>
                  <div className="flex p-1 bg-slate-200 rounded-lg">
                    {[21, 11].map(gp => (
                      <button key={gp} onClick={() => setFormData({...formData, gamePoint: gp, sW: gp})} className={`flex-1 py-1.5 text-xs font-bold rounded-md ${formData.gamePoint === gp ? 'bg-white shadow text-blue-800' : 'text-slate-600'}`}>{gp}分制</button>
                    ))}
                  </div>
                </div>
              </div>

              <div className="space-y-1"><label className="text-[10px] font-bold text-slate-400 uppercase">日期</label>
                <input type="date" value={selectedDate} onChange={e => setSelectedDate(e.target.value)} className="w-full p-2 border rounded-lg text-xs font-bold h-[40px]" />
              </div>

              <div className="space-y-3">
                <PlayerSelect label="勝方 Winner" colorClass="bg-blue-50 border-blue-100 text-blue-700" value={formData.w1} onChange={val => setFormData({...formData, w1: val})} />
                {matchType === 'Doubles' && <PlayerSelect label="勝方 Partner" colorClass="bg-blue-50 border-blue-100 text-blue-700" value={formData.w2} onChange={val => setFormData({...formData, w2: val})} />}
                
                <div className="py-2 flex items-center justify-center"><Sword className="text-slate-200" size={24}/></div>

                <PlayerSelect label="負方 Loser" colorClass="bg-red-50 border-red-100 text-red-700" value={formData.l1} onChange={val => setFormData({...formData, l1: val})} />
                {matchType === 'Doubles' && <PlayerSelect label="負方 Partner" colorClass="bg-red-50 border-red-100 text-red-700" value={formData.l2} onChange={val => setFormData({...formData, l2: val})} />}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1 text-center"><label className="text-[10px] font-bold text-slate-400 uppercase">勝方得分</label><input type="number" value={formData.sW} onChange={e => setFormData({...formData, sW: e.target.value})} className="w-full p-3 border rounded-lg font-black text-center text-xl text-blue-700" /></div>
                <div className="space-y-1 text-center"><label className="text-[10px] font-bold text-slate-400 uppercase">負方得分</label><input type="number" value={formData.sL} onChange={e => setFormData({...formData, sL: e.target.value})} className="w-full p-3 border rounded-lg font-black text-center text-xl text-red-700" /></div>
              </div>

              <button onClick={handleSubmitMatch} disabled={!!validationError} className={`w-full py-4 text-white font-black rounded-xl shadow-lg uppercase transition-all ${validationError ? 'bg-slate-300' : 'bg-red-600'}`}>
                {isEditing ? '更新成績' : '提交成績'}
              </button>
            </div>
          </div>
        )}

        {view === 'daily' && (
          <div className="space-y-4 animate-in fade-in">
            <div className="flex justify-between items-center"><h2 className="text-xl font-bold text-slate-800">今日成績表</h2><input type="date" value={selectedDate} onChange={e => setSelectedDate(e.target.value)} className="p-2 border rounded-lg text-xs font-bold" /></div>
            <div className="bg-white rounded-xl shadow-sm border overflow-hidden">
              <table className="w-full text-left">
                <thead className="bg-slate-50 border-b"><tr><th className="px-4 py-3 text-[10px] font-black text-slate-400 uppercase">球員</th><th className="text-center px-4 py-3 text-[10px] font-black text-slate-400 uppercase">單日積分</th><th className="text-right px-4 py-3 text-[10px] font-black text-slate-400 uppercase">勝率</th></tr></thead>
                <tbody className="divide-y">
                  {Object.keys(history.reduce((acc, m) => { if(m.date === selectedDate) { [...m.winner, ...m.loser].forEach(p => acc[p] = true); } return acc; }, {})).length > 0 ? (
                    (() => {
                        const daily = history.filter(m => m.date === selectedDate);
                        const players = {};
                        daily.forEach(m => {
                          m.winner.forEach(n => { if(!players[n]) players[n] = {pts:0, wins:0, games:0}; players[n].pts += m.pts; players[n].wins += 1; players[n].games += 1; });
                          m.loser.forEach(n => { if(!players[n]) players[n] = {pts:0, wins:0, games:0}; players[n].pts -= m.pts; players[n].games += 1; });
                        });
                        return Object.keys(players).map(n => ({ name: n, ...players[n], rate: ((players[n].wins / players[n].games) * 100).toFixed(0) + '%' }))
                          .sort((a,b) => b.pts - a.pts)
                          .map((p, i) => (
                            <tr key={i}><td className="px-4 py-4 font-bold text-sm">{p.name}</td><td className={`text-center font-black ${p.pts > 0 ? 'text-blue-600' : 'text-red-600'}`}>{p.pts > 0 ? `+${p.pts}` : p.pts}</td><td className="px-4 py-4 text-right"><span className="text-xs font-black bg-slate-100 px-2 py-1 rounded">{p.rate}</span></td></tr>
                          ));
                    })()
                  ) : (
                    <tr><td colSpan="3" className="p-8 text-center text-slate-400 text-xs font-bold uppercase italic">此日暫無比賽紀錄</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>

      <button onClick={() => { setView('input'); setIsEditing(false); }} className={`fixed bottom-6 right-6 w-14 h-14 bg-red-600 rounded-full flex items-center justify-center text-white shadow-2xl z-40 active:scale-95 transition-all ${view === 'input' ? 'hidden' : ''}`}><PlusCircle size={32} /></button>
    </div>
  );
};

export default App;