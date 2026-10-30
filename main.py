"""LaLiga Insight — an editorial-style football analytics desktop app.
Run with: python main.py
All interface and application code is Python/Tkinter. Match data remains CSV.
"""
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from models import Match, MatchManager
from calculations import team_summary, last_results, league_table, head_to_head
from validation import validate_match_form

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "laliga_matches.csv")
# A fresh visual system: midnight ink, warm paper, electric coral and mint.
C = {"bg":"#10131D", "side":"#171B28", "panel":"#1D2232", "panel2":"#242B3E",
     "line":"#343B50", "paper":"#F3F0E8", "muted":"#9BA4B8", "coral":"#FF7058",
     "mint":"#9AF0C4", "blue":"#8EA7FF", "yellow":"#F4D77B", "red":"#FF817C",
     "white":"#FFFFFF", "ink":"#141824"}
FONT = "Segoe UI"

class LaLigaApp:
    def __init__(self, root):
        self.root=root; self.root.title("LaLiga Insight | Football Intelligence")
        self.root.geometry("1380x860"); self.root.minsize(1120,720); self.root.configure(bg=C["bg"])
        self.manager=MatchManager(); self.active_page="Overview"; self.selected_team=tk.StringVar()
        self.selected_season=tk.StringVar(); self.search_var=tk.StringVar(); self.status=tk.StringVar(value="READY · Local dataset")
        self._styles(); self._shell(); self.load_data(); self.show_page("Overview")

    def _styles(self):
        s=ttk.Style(); s.theme_use("clam")
        s.configure("TCombobox", fieldbackground=C["panel2"], background=C["panel2"], foreground=C["paper"], arrowcolor=C["mint"], padding=7)
        s.map("TCombobox", fieldbackground=[("readonly",C["panel2"])], foreground=[("readonly",C["paper"])])
        s.configure("Treeview", background=C["panel"], fieldbackground=C["panel"], foreground=C["paper"], rowheight=32, borderwidth=0, font=(FONT,10))
        s.configure("Treeview.Heading", background=C["panel2"], foreground=C["mint"], relief="flat", font=(FONT,9,"bold"), padding=9)
        s.map("Treeview", background=[("selected",C["coral"])], foreground=[("selected",C["ink"])])
        s.configure("TScrollbar", background=C["panel2"], troughcolor=C["bg"], bordercolor=C["bg"], arrowcolor=C["paper"])

    def _shell(self):
        self.sidebar=tk.Frame(self.root,bg=C["side"],width=230); self.sidebar.pack(side="left",fill="y"); self.sidebar.pack_propagate(False)
        brand=tk.Frame(self.sidebar,bg=C["side"]); brand.pack(fill="x",padx=22,pady=(27,35))
        mark=tk.Canvas(brand,width=42,height=42,bg=C["side"],highlightthickness=0); mark.pack(side="left")
        mark.create_oval(3,3,39,39,outline=C["coral"],width=2); mark.create_line(12,13,30,13,21,30,12,13,fill=C["mint"],width=2); mark.create_line(12,13,12,26,21,30,30,26,30,13,fill=C["mint"],width=2)
        tk.Label(brand,text="LALIGA\nINSIGHT",bg=C["side"],fg=C["paper"],font=(FONT,13,"bold"),justify="left").pack(side="left",padx=10)
        tk.Label(self.sidebar,text="MATCH INTELLIGENCE",bg=C["side"],fg=C["muted"],font=(FONT,8,"bold")).pack(anchor="w",padx=23,pady=(0,10))
        self.nav={}
        for name,icon in [("Overview","◈"),("Team Lab","◎"),("Standings","▤"),("Head to Head","⇄"),("Match Vault","▦")]:
            b=tk.Button(self.sidebar,text=f"  {icon}    {name}",command=lambda n=name:self.show_page(n),anchor="w",bd=0,relief="flat",cursor="hand2",font=(FONT,11,"bold"),padx=17,pady=13,bg=C["side"],fg=C["muted"],activebackground=C["panel2"],activeforeground=C["paper"])
            b.pack(fill="x",padx=12,pady=2); self.nav[name]=b
        tk.Frame(self.sidebar,bg=C["line"],height=1).pack(fill="x",padx=20,pady=(28,14))
        tk.Label(self.sidebar,text="DATASET",bg=C["side"],fg=C["muted"],font=(FONT,8,"bold")).pack(anchor="w",padx=23)
        self.side_count=tk.Label(self.sidebar,text="Loading matches…",bg=C["side"],fg=C["mint"],font=(FONT,10)); self.side_count.pack(anchor="w",padx=23,pady=7)
        tk.Label(self.sidebar,text="LOCAL MODE  •  CSV STORAGE",bg=C["side"],fg=C["muted"],font=(FONT,8)).pack(side="bottom",anchor="w",padx=20,pady=20)
        self.main=tk.Frame(self.root,bg=C["bg"]); self.main.pack(side="left",fill="both",expand=True)
        top=tk.Frame(self.main,bg=C["bg"]); top.pack(fill="x",padx=32,pady=(24,14))
        self.eyebrow=tk.Label(top,text="THE NUMBERS BEHIND THE GAME",bg=C["bg"],fg=C["coral"],font=(FONT,9,"bold")); self.eyebrow.pack(anchor="w")
        line=tk.Frame(top,bg=C["bg"]); line.pack(fill="x",pady=(4,0))
        self.page_title=tk.Label(line,text="Overview",bg=C["bg"],fg=C["paper"],font=(FONT,27,"bold")); self.page_title.pack(side="left")
        self.top_badge=tk.Label(line,text="●  DATA LOADED",bg=C["panel"],fg=C["mint"],font=(FONT,9,"bold"),padx=12,pady=7); self.top_badge.pack(side="right",anchor="s")
        self.content=tk.Frame(self.main,bg=C["bg"]); self.content.pack(fill="both",expand=True,padx=32,pady=(0,8))
        foot=tk.Frame(self.main,bg=C["bg"]); foot.pack(fill="x",padx=32,pady=(0,13))
        tk.Label(foot,textvariable=self.status,bg=C["bg"],fg=C["muted"],font=(FONT,8)).pack(side="left")
        tk.Label(foot,text="LA LIGA  /  ANALYTICS WORKSPACE",bg=C["bg"],fg=C["muted"],font=(FONT,8,"bold")).pack(side="right")

    def load_data(self):
        ok,msg=self.manager.load_from_csv(DATA_FILE)
        self.side_count.config(text=f"{len(self.manager.matches):,} match records")
        self.status.set(("●  "+msg) if ok else ("!  "+msg))
        teams=self.manager.get_teams(); seasons=self.manager.get_seasons()
        self.selected_team.set(teams[0] if teams else "")
        self.selected_season.set(str(seasons[0]) if seasons else "All")

    def clear(self):
        for w in self.content.winfo_children(): w.destroy()

    def show_page(self,name):
        self.active_page=name
        for n,b in self.nav.items(): b.configure(bg=C["panel2"] if n==name else C["side"],fg=C["mint"] if n==name else C["muted"])
        self.page_title.config(text=name); self.clear()
        {"Overview":self.page_overview,"Team Lab":self.page_team,"Standings":self.page_standings,"Head to Head":self.page_h2h,"Match Vault":self.page_vault}[name]()

    def label(self,parent,text,size=10,color=None,bold=False,**kw):
        return tk.Label(parent,text=text,bg=kw.pop("bg",C["panel"]),fg=color or C["paper"],font=(FONT,size,"bold" if bold else "normal"),**kw)

    def panel(self,parent,bg=None,padx=18,pady=16):
        f=tk.Frame(parent,bg=bg or C["panel"],highlightthickness=1,highlightbackground=C["line"]); f.pack_propagate(False); return f

    def card(self,parent,title,value,sub,color):
        f=tk.Frame(parent,bg=C["panel"],highlightthickness=1,highlightbackground=C["line"])
        tk.Frame(f,bg=color,height=3).pack(fill="x")
        tk.Label(f,text=title.upper(),bg=C["panel"],fg=C["muted"],font=(FONT,8,"bold")).pack(anchor="w",padx=16,pady=(13,4))
        tk.Label(f,text=value,bg=C["panel"],fg=C["paper"],font=(FONT,23,"bold")).pack(anchor="w",padx=16)
        tk.Label(f,text=sub,bg=C["panel"],fg=color,font=(FONT,9)).pack(anchor="w",padx=16,pady=(2,13))
        return f

    def combo(self,parent,var,values,width=24):
        return ttk.Combobox(parent,textvariable=var,values=values,width=width,state="readonly",font=(FONT,10))

    def button(self,parent,text,command,primary=False):
        bg=C["coral"] if primary else C["panel2"]; fg=C["ink"] if primary else C["paper"]
        return tk.Button(parent,text=text,command=command,bg=bg,fg=fg,activebackground=C["mint"],activeforeground=C["ink"],bd=0,cursor="hand2",font=(FONT,9,"bold"),padx=14,pady=9)

    def table(self,parent,columns,headings=None,height=12):
        wrap=tk.Frame(parent,bg=C["panel"]); wrap.pack(fill="both",expand=True)
        tree=ttk.Treeview(wrap,columns=columns,show="headings",height=height)
        for col in columns:
            tree.heading(col,text=(headings or {}).get(col,col.replace("_"," ").upper()))
            tree.column(col,width=105,anchor="center",stretch=True)
        y=ttk.Scrollbar(wrap,orient="vertical",command=tree.yview); tree.configure(yscrollcommand=y.set)
        tree.pack(side="left",fill="both",expand=True); y.pack(side="right",fill="y")
        return tree

    def page_overview(self):
        allm=self.manager.matches; seasons=self.manager.get_seasons(); teams=self.manager.get_teams()
        season=str(seasons[0]) if seasons else "All"
        rows=league_table([m for m in allm if str(m.season)==season]) if season!="All" else league_table(allm)
        total=len(allm); goals=sum(m.gf for m in allm); avg=goals/total if total else 0
        hero=tk.Frame(self.content,bg=C["panel2"],highlightthickness=1,highlightbackground=C["line"]); hero.pack(fill="x",pady=(0,15))
        left=tk.Frame(hero,bg=C["panel2"]); left.pack(side="left",fill="both",expand=True,padx=23,pady=20)
        self.label(left,"THE BEAUTIFUL GAME, DECODED",9,C["mint"],True,bg=C["panel2"]).pack(anchor="w")
        self.label(left,"Every match has a story.\nFind it in the numbers.",22,C["paper"],True,bg=C["panel2"],justify="left").pack(anchor="w",pady=(8,7))
        self.label(left,"Explore form, attacking output and league momentum across your local LaLiga dataset.",10,C["muted"],bg=C["panel2"],wraplength=500,justify="left").pack(anchor="w")
        pitch=tk.Canvas(hero,width=205,height=150,bg=C["panel2"],highlightthickness=0); pitch.pack(side="right",padx=20,pady=14)
        pitch.create_rectangle(10,8,195,140,outline=C["mint"],width=2); pitch.create_line(102,8,102,140,fill=C["mint"]); pitch.create_oval(70,42,134,106,outline=C["mint"],width=2); pitch.create_rectangle(10,42,43,106,outline=C["mint"]); pitch.create_rectangle(162,42,195,106,outline=C["mint"]); pitch.create_oval(93,68,111,86,fill=C["coral"],outline=C["coral"])
        stats=tk.Frame(self.content,bg=C["bg"]); stats.pack(fill="x",pady=(0,15))
        values=[("MATCH RECORDS",f"{total:,}","Local observations",C["coral"]),("CLUBS TRACKED",str(len(teams)),"Across available seasons",C["mint"]),("GOALS RECORDED",f"{goals:,}","Goals for all team records",C["blue"]),("GOALS / RECORD",f"{avg:.2f}","Average attacking output",C["yellow"])]
        for i,(t,v,s,c) in enumerate(values): stats.grid_columnconfigure(i,weight=1); self.card(stats,t,v,s,c).grid(row=0,column=i,sticky="nsew",padx=(0 if i==0 else 9,0))
        lower=tk.Frame(self.content,bg=C["bg"]); lower.pack(fill="both",expand=True)
        a=tk.Frame(lower,bg=C["panel"],highlightthickness=1,highlightbackground=C["line"]); a.pack(side="left",fill="both",expand=True,padx=(0,8))
        b=tk.Frame(lower,bg=C["panel"],highlightthickness=1,highlightbackground=C["line"],width=310); b.pack(side="left",fill="both",expand=False,padx=(8,0)); b.pack_propagate(False)
        self.label(a,"SEASON POWER RANKING",10,C["paper"],True).pack(anchor="w",padx=17,pady=(15,2))
        self.label(a,f"Season {season}/{str(int(season)+1)[-2:] if season.isdigit() else ''} · ranked by points, goal difference, goals",9,C["muted"]).pack(anchor="w",padx=17,pady=(0,8))
        tree=self.table(a,("rank","team","played","points","gd"),{"rank":"#","team":"CLUB","played":"P","points":"PTS","gd":"GD"},height=7)
        for i,r in enumerate(rows[:8],1): tree.insert("","end",values=(f"{i:02}",r["team"],r["played"],r["points"],f"{r['gd']:+}"))
        self.label(b,"RECENT FORM SNAPSHOT",10,C["paper"],True).pack(anchor="w",padx=17,pady=(15,10))
        for r in rows[:5]:
            line=tk.Frame(b,bg=C["panel"]); line.pack(fill="x",padx=16,pady=5)
            tk.Label(line,text=r["team"],bg=C["panel"],fg=C["paper"],font=(FONT,9,"bold"),anchor="w").pack(side="left",fill="x",expand=True)
            tk.Label(line,text=f"{r['points']} PTS",bg=C["panel"],fg=C["mint"],font=(FONT,9,"bold")).pack(side="right")
        self.label(b,"Numbers are calculated from the loaded CSV; no live feed is implied.",8,C["muted"],wraplength=260,justify="left").pack(anchor="w",padx=17,pady=(14,0))

    def page_team(self):
        teams=self.manager.get_teams(); seasons=self.manager.get_seasons()
        bar=tk.Frame(self.content,bg=C["panel"],highlightthickness=1,highlightbackground=C["line"]); bar.pack(fill="x",pady=(0,14))
        self.label(bar,"CLUB",8,C["muted"],True).pack(side="left",padx=(16,8),pady=13)
        self.combo(bar,self.selected_team,teams,30).pack(side="left",pady=10)
        self.label(bar,"SEASON",8,C["muted"],True).pack(side="left",padx=(20,8))
        if self.selected_season.get() not in [str(s) for s in seasons] and seasons:self.selected_season.set(str(seasons[0]))
        self.combo(bar,self.selected_season,[str(s) for s in seasons],10).pack(side="left",pady=10)
        self.button(bar,"ANALYZE  ↗",self.refresh_team,True).pack(side="right",padx=14,pady=7)
        self.team_body=tk.Frame(self.content,bg=C["bg"]); self.team_body.pack(fill="both",expand=True); self.refresh_team()

    def refresh_team(self):
        if not hasattr(self,"team_body") or not self.team_body.winfo_exists(): return
        for w in self.team_body.winfo_children():w.destroy()
        team=self.selected_team.get(); season=self.selected_season.get()
        ms=[m for m in self.manager.matches if m.team==team and str(m.season)==season]
        s=team_summary(ms)
        cards=tk.Frame(self.team_body,bg=C["bg"]); cards.pack(fill="x",pady=(0,14))
        data=[("POINTS",s["points"],f"{s['wins']} wins",C["coral"]),("WIN RATE",f"{s['win_pct']}%",f"{s['played']} matches",C["mint"]),("GOAL DIFFERENCE",f"{s['gd']:+}",f"{s['gf']} for · {s['ga']} against",C["blue"]),("AVG POSSESSION",f"{s['avg_poss']}%","Mean possession",C["yellow"])]
        for i,(t,v,sub,c) in enumerate(data): cards.grid_columnconfigure(i,weight=1); self.card(cards,t,str(v),sub,c).grid(row=0,column=i,sticky="nsew",padx=(0 if i==0 else 8,0))
        mid=tk.Frame(self.team_body,bg=C["bg"]);mid.pack(fill="both",expand=True)
        chart=tk.Frame(mid,bg=C["panel"],highlightthickness=1,highlightbackground=C["line"]);chart.pack(side="left",fill="both",expand=True,padx=(0,8))
        recent=tk.Frame(mid,bg=C["panel"],highlightthickness=1,highlightbackground=C["line"],width=350);recent.pack(side="left",fill="both",expand=False,padx=(8,0));recent.pack_propagate(False)
        self.label(chart,"ATTACK PROFILE",10,C["paper"],True).pack(anchor="w",padx=18,pady=(15,0))
        self.label(chart,"Goals and expected goals per match",9,C["muted"]).pack(anchor="w",padx=18)
        cv=tk.Canvas(chart,bg=C["panel"],height=240,highlightthickness=0);cv.pack(fill="both",expand=True,padx=12,pady=10);cv.bind("<Configure>",lambda e:self.draw_bars(cv,[s["avg_gf"],s["avg_xg"],s["avg_xga"],s["avg_gf"]],["GOALS","XG","XGA","AVG GF"],[C["coral"],C["mint"],C["blue"],C["yellow"]]))
        self.label(recent,"FORM GUIDE",10,C["paper"],True).pack(anchor="w",padx=17,pady=(15,2))
        self.label(recent,"Latest available matches",9,C["muted"]).pack(anchor="w",padx=17,pady=(0,9))
        ordered=sorted(ms,key=lambda m:m.date)[-8:][::-1]
        for m in ordered:
            row=tk.Frame(recent,bg=C["panel2"]);row.pack(fill="x",padx=14,pady=4)
            color={"W":C["mint"],"D":C["yellow"],"L":C["red"]}[m.result]
            tk.Label(row,text=m.result,bg=color,fg=C["ink"],font=(FONT,9,"bold"),width=3,pady=5).pack(side="left",padx=7,pady=5)
            tk.Label(row,text=f"{m.date}   vs {m.opponent}",bg=C["panel2"],fg=C["paper"],font=(FONT,9),anchor="w").pack(side="left",fill="x",expand=True)
            tk.Label(row,text=f"{m.gf} : {m.ga}",bg=C["panel2"],fg=C["paper"],font=(FONT,10,"bold")).pack(side="right",padx=9)
        self.label(recent,f"Clean sheets  {s['clean_sheets']}     Shot accuracy  {s['shot_accuracy']}%",9,C["mint"],True).pack(anchor="w",padx=17,pady=12)

    def draw_bars(self,cv,vals,names,colors):
        cv.delete("all"); w=max(cv.winfo_width(),300); h=max(cv.winfo_height(),180); top=20; base=h-35; gap=w/(len(vals)*2+1); maxv=max(vals+[1])*1.2
        for i,(v,n,col) in enumerate(zip(vals,names,colors)):
            x=gap*(i*2+1); bh=(base-top)*(v/maxv); cv.create_rectangle(x,base-bh,x+gap,base,fill=col,outline="")
            cv.create_text(x+gap/2,base-bh-12,text=f"{v:.2f}",fill=C["paper"],font=(FONT,9,"bold"));cv.create_text(x+gap/2,base+16,text=n,fill=C["muted"],font=(FONT,8,"bold"))
        for j in range(1,4):
            y=top+(base-top)*j/4;cv.create_line(8,y,w-8,y,fill=C["line"],dash=(2,4))

    def page_standings(self):
        bar=tk.Frame(self.content,bg=C["panel"],highlightthickness=1,highlightbackground=C["line"]);bar.pack(fill="x",pady=(0,12))
        self.label(bar,"SEASON",8,C["muted"],True).pack(side="left",padx=(16,8),pady=12)
        seasons=[str(s) for s in self.manager.get_seasons()]
        self.combo(bar,self.selected_season,seasons,12).pack(side="left",pady=9)
        self.button(bar,"REFRESH TABLE",self.refresh_standings,True).pack(side="right",padx=13,pady=6)
        self.stand_body=tk.Frame(self.content,bg=C["panel"],highlightthickness=1,highlightbackground=C["line"]);self.stand_body.pack(fill="both",expand=True);self.refresh_standings()

    def refresh_standings(self):
        if not hasattr(self,"stand_body") or not self.stand_body.winfo_exists():return
        for w in self.stand_body.winfo_children():w.destroy()
        ms=[m for m in self.manager.matches if str(m.season)==self.selected_season.get()]
        rows=league_table(ms); self.label(self.stand_body,f"SEASON {self.selected_season.get()} / {str(int(self.selected_season.get())+1)[-2:] if self.selected_season.get().isdigit() else ''}  ·  {len(rows)} CLUBS",10,C["mint"],True).pack(anchor="w",padx=17,pady=13)
        tree=self.table(self.stand_body,("pos","team","played","wins","draws","losses","gf","ga","gd","points","win_pct"),{"pos":"POS","team":"CLUB","played":"P","wins":"W","draws":"D","losses":"L","gf":"GF","ga":"GA","gd":"GD","points":"PTS","win_pct":"WIN %"},height=18)
        for i,r in enumerate(rows,1):tree.insert("","end",values=(i,r["team"],r["played"],r["wins"],r["draws"],r["losses"],r["gf"],r["ga"],f"{r['gd']:+}",r["points"],f"{r['win_pct']:.1f}%"))

    def page_h2h(self):
        teams=self.manager.get_teams()
        self.h2h_a=tk.StringVar(value=teams[0] if teams else ""); self.h2h_b=tk.StringVar(value=teams[1] if len(teams)>1 else (teams[0] if teams else ""))
        bar=tk.Frame(self.content,bg=C["panel"],highlightthickness=1,highlightbackground=C["line"]);bar.pack(fill="x",pady=(0,14))
        self.label(bar,"CLUB A",8,C["muted"],True).pack(side="left",padx=(16,8),pady=12);self.combo(bar,self.h2h_a,teams,27).pack(side="left",pady=9)
        self.label(bar,"VS",10,C["coral"],True).pack(side="left",padx=14);self.combo(bar,self.h2h_b,teams,27).pack(side="left",pady=9)
        self.button(bar,"COMPARE  ⇄",self.refresh_h2h,True).pack(side="right",padx=13,pady=6)
        self.h2h_body=tk.Frame(self.content,bg=C["bg"]);self.h2h_body.pack(fill="both",expand=True);self.refresh_h2h()

    def refresh_h2h(self):
        if not hasattr(self,"h2h_body") or not self.h2h_body.winfo_exists():return
        for w in self.h2h_body.winfo_children():w.destroy()
        a,b=self.h2h_a.get(),self.h2h_b.get();r=head_to_head(self.manager.matches,a,b)
        hero=tk.Frame(self.h2h_body,bg=C["panel2"],highlightthickness=1,highlightbackground=C["line"]);hero.pack(fill="x",pady=(0,13))
        for i,(name,score,sub,col) in enumerate([(a,r["a_wins"],f"{r['a_goals']} goals",C["coral"]),("DRAW",r["draws"],f"{len(r['meetings'])} recorded meetings",C["yellow"]),(b,r["b_wins"],f"{r['b_goals']} goals",C["mint"])]):
            hero.grid_columnconfigure(i,weight=1);f=tk.Frame(hero,bg=C["panel2"]);f.grid(row=0,column=i,sticky="nsew",padx=12,pady=20)
            self.label(f,name.upper(),9,col,True,bg=C["panel2"]).pack();self.label(f,str(score),32,C["paper"],True,bg=C["panel2"]).pack(pady=4);self.label(f,sub,9,C["muted"],bg=C["panel2"]).pack()
        box=tk.Frame(self.h2h_body,bg=C["panel"],highlightthickness=1,highlightbackground=C["line"]);box.pack(fill="both",expand=True)
        self.label(box,"AVAILABLE MATCH RECORDS",10,C["paper"],True).pack(anchor="w",padx=16,pady=13)
        tree=self.table(box,("date","team","score","opponent","venue","result"),{"date":"DATE","team":"TEAM","score":"SCORE","opponent":"OPPONENT","venue":"VENUE","result":"RESULT"},height=13)
        for m in r["meetings"]:tree.insert("","end",values=(m.date,m.team,f"{m.gf} - {m.ga}",m.opponent,m.venue,m.result))
        if not r["meetings"]:self.label(box,"No direct meeting records were found for this pair.",10,C["muted"]).pack(anchor="w",padx=18,pady=15)

    def page_vault(self):
        bar=tk.Frame(self.content,bg=C["panel"],highlightthickness=1,highlightbackground=C["line"]);bar.pack(fill="x",pady=(0,12))
        tk.Label(bar,text="SEARCH",bg=C["panel"],fg=C["muted"],font=(FONT,8,"bold")).pack(side="left",padx=(13,7),pady=11)
        entry=tk.Entry(bar,textvariable=self.search_var,bg=C["panel2"],fg=C["paper"],insertbackground=C["paper"],relief="flat",font=(FONT,10),width=30);entry.pack(side="left",ipady=7,pady=7)
        self.button(bar,"FIND",self.refresh_vault).pack(side="left",padx=7)
        self.button(bar,"+ ADD MATCH",lambda:self.match_dialog(),True).pack(side="right",padx=12,pady=6)
        self.vault_body=tk.Frame(self.content,bg=C["panel"],highlightthickness=1,highlightbackground=C["line"]);self.vault_body.pack(fill="both",expand=True);self.refresh_vault()

    def refresh_vault(self):
        if not hasattr(self,"vault_body") or not self.vault_body.winfo_exists():return
        for w in self.vault_body.winfo_children():w.destroy()
        q=self.search_var.get().strip().lower();ms=[m for m in self.manager.matches if not q or q in " ".join(map(str,[m.match_id,m.date,m.team,m.opponent,m.season,m.result])).lower()]
        ms=sorted(ms,key=lambda m:m.date,reverse=True)
        self.label(self.vault_body,f"MATCH VAULT  /  {len(ms):,} RESULTS",10,C["mint"],True).pack(anchor="w",padx=15,pady=12)
        tree=self.table(self.vault_body,("id","date","season","team","score","opponent","venue","result","xg"),{"id":"ID","date":"DATE","season":"SEASON","team":"TEAM","score":"SCORE","opponent":"OPPONENT","venue":"VENUE","result":"W/D/L","xg":"XG"},height=17)
        for m in ms[:1500]:tree.insert("","end",iid=m.match_id,values=(m.match_id,m.date,f"{m.season}/{str(m.season+1)[-2:]}",m.team,f"{m.gf} - {m.ga}",m.opponent,m.venue,m.result,f"{m.xg:.2f}"))
        actions=tk.Frame(self.vault_body,bg=C["panel"]);actions.pack(fill="x",padx=12,pady=(8,12))
        def selected():
            ids=tree.selection()
            if not ids:messagebox.showinfo("Select a record","Choose a match row first.");return None
            return ids[0]
        self.button(actions,"EDIT SELECTED",lambda:(self.match_dialog(selected(),tree) if selected() else None)).pack(side="left",padx=(0,7))
        self.button(actions,"DELETE SELECTED",lambda:self.delete_selected(tree,selected),False).pack(side="left",padx=7)
        self.button(actions,"SAVE CSV",self.save_data,True).pack(side="right")

    def delete_selected(self,tree,getid):
        mid=getid()
        if not mid:return
        if messagebox.askyesno("Delete match","Delete this match record permanently from the local CSV after saving?"):
            try:self.manager.delete_match(mid);self.save_data(silent=True);self.refresh_vault();self.side_count.config(text=f"{len(self.manager.matches):,} match records")
            except ValueError as e:messagebox.showerror("Could not delete",str(e))

    def match_dialog(self,match_id=None,tree=None):
        old=self.manager.find_by_id(match_id) if match_id else None
        win=tk.Toplevel(self.root);win.title("Edit match" if old else "Add match");win.configure(bg=C["bg"]);win.geometry("570x690");win.transient(self.root);win.grab_set()
        tk.Label(win,text="MATCH RECORD",bg=C["bg"],fg=C["coral"],font=(FONT,9,"bold")).pack(anchor="w",padx=24,pady=(20,2))
        tk.Label(win,text="Edit the match details" if old else "Add a match to the dataset",bg=C["bg"],fg=C["paper"],font=(FONT,20,"bold")).pack(anchor="w",padx=24,pady=(0,12))
        fields=[("date","Date (YYYY-MM-DD)",old.date if old else "2025-08-16"),("matchweek","Matchweek (1–38)",str(old.matchweek) if old else "1"),("venue","Venue (Home/Away)",old.venue if old else "Home"),("team","Team",old.team if old else ""),("opponent","Opponent",old.opponent if old else ""),("gf","Goals for",str(old.gf) if old else "0"),("ga","Goals against",str(old.ga) if old else "0"),("xg","Expected goals (xG)",str(old.xg) if old else "0.0"),("xga","Expected goals against",str(old.xga) if old else "0.0"),("poss","Possession %",str(old.poss) if old else "50"),("sh","Shots",str(old.sh) if old else "0"),("sot","Shots on target",str(old.sot) if old else "0")]
        entries={}; grid=tk.Frame(win,bg=C["bg"]);grid.pack(fill="both",expand=True,padx=24)
        for i,(key,label,value) in enumerate(fields):
            row=i//2; col=i%2; cell=tk.Frame(grid,bg=C["bg"]);cell.grid(row=row,column=col,sticky="ew",padx=(0,10) if col==0 else (10,0),pady=5);grid.grid_columnconfigure(col,weight=1)
            tk.Label(cell,text=label.upper(),bg=C["bg"],fg=C["muted"],font=(FONT,8,"bold")).pack(anchor="w")
            ent=tk.Entry(cell,bg=C["panel2"],fg=C["paper"],insertbackground=C["paper"],relief="flat",font=(FONT,10));ent.pack(fill="x",ipady=8,pady=(4,0));ent.insert(0,value);entries[key]=ent
        def save():
            try:
                values={k:e.get() for k,e in entries.items()};clean=validate_match_form(values)
                mid=old.match_id if old else self.manager.next_id()
                m=Match(mid,clean["season"],clean["matchweek"],clean["date"],clean["venue"],clean["team"],clean["opponent"],clean["gf"],clean["ga"],clean["xg"],clean["xga"],clean["poss"],clean["sh"],clean["sot"])
                if old:self.manager.update_match(mid,m)
                else:self.manager.add_match(m)
                self.save_data(silent=True);win.destroy();self.side_count.config(text=f"{len(self.manager.matches):,} match records");self.refresh_vault();self.status.set("●  Match record saved to CSV")
            except (ValueError,KeyError) as e:messagebox.showerror("Check match details",str(e),parent=win)
        self.button(win,"SAVE MATCH RECORD",save,True).pack(fill="x",padx=24,pady=20)

    def save_data(self,silent=False):
        ok,msg=self.manager.save_to_csv(DATA_FILE);self.status.set("●  "+msg if ok else "!  "+msg)
        if not silent:messagebox.showinfo("Save CSV",msg) if ok else messagebox.showerror("Save failed",msg)

if __name__=="__main__":
    root=tk.Tk();app=LaLigaApp(root);root.mainloop()
