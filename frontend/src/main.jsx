import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Routes, Route, Link, useNavigate } from "react-router-dom";
import {
  ArrowRight, BrainCircuit, CheckCircle2, Clock3, HeartHandshake, Leaf,
  LogIn, LogOut, MapPin, PackageCheck, Search, ShieldCheck, Truck, Users,
  Sparkles, TimerReset, ClipboardCheck
} from "lucide-react";
import {
  login, logout, register, getMe, listDonations, createDonation,
  requestPickup, recommended, myDonations, stats, pickups, updatePickup
} from "./api";
import "./styles.css";

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    if (!localStorage.getItem("access_token")) return setLoading(false);
    getMe().then(setUser).catch(logout).finally(() => setLoading(false));
  }, []);
  if (loading) return <div className="loader">Loading ZeroBite AI...</div>;
  return <>
    <Navbar user={user} setUser={setUser} />
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login setUser={setUser} />} />
      <Route path="/register" element={<Register setUser={setUser} />} />
      <Route path="/donations" element={<Donations user={user} />} />
      <Route path="/donate" element={<Donate user={user} />} />
      <Route path="/dashboard" element={<Dashboard user={user} />} />
    </Routes>
    <Footer />
  </>;
}

function Navbar({ user, setUser }) {
  const nav = useNavigate();
  return <header className="nav"><div className="nav-inner">
    <Link className="brand" to="/"><span className="logo"><Leaf size={19} /></span>Zero<span>Bite</span><b>AI</b></Link>
    <nav>
      <Link to="/">Home</Link><Link to="/donations">Find food</Link>
      {user && <Link to="/dashboard">Dashboard</Link>}
      {user?.role === "donor" && <Link to="/donate">Donate</Link>}
      {user ? <button onClick={() => { logout(); setUser(null); nav("/"); }}><LogOut size={15} /> Logout</button>
        : <Link className="nav-btn" to="/login"><LogIn size={15} /> Login</Link>}
    </nav>
  </div></header>;
}

function Home() {
  const workflow = [
    [Users, "Create an account", "Each user has a separate account and role-based dashboard."],
    [PackageCheck, "Post surplus", "Donors add food type, quantity, prepared time and pickup details."],
    [BrainCircuit, "AI prioritizes", "AI estimates expiry from prepared time + food type, then ML scores rescue urgency."],
    [Truck, "Request pickup", "NGOs and volunteers can request available donations for rescue."],
    [CheckCircle2, "Track status", "Pickup requests move through pending, accepted, collected and delivered."],
    [ShieldCheck, "Secure access", "JWT authentication and backend role checks protect private actions."],
    [HeartHandshake, "Measure impact", "Dashboards show rescued meals, active donations and priority levels."],
    [MapPin, "Location-aware", "Pickup location is captured for human-readable handoff and future routing."],
  ];
  return <main>
    <section className="hero"><div className="hero-grid">
      <div><span className="eyebrow"><BrainCircuit size={15} /> AI-POWERED FOOD RESCUE</span>
        <h1>Rescue surplus food <em>before it becomes waste.</em></h1>
        <p>ZeroBite connects donors, NGOs and volunteers through an end-to-end food rescue workflow with AI-assisted expiry estimation and ML rescue-priority scoring.</p>
        <div className="actions"><Link className="btn primary" to="/register">Create an account <ArrowRight size={17} /></Link><Link className="btn soft" to="/donations">Find food</Link></div>
      </div>
      <div className="ai-card"><div className="ai-head"><BrainCircuit /><span>AI FOOD RESCUE ENGINE</span></div>
        <div className="score"><strong>AI</strong><span>built in</span></div>
        <h3>Expiry + rescue priority</h3>
        <p>Prepared time + food type → AI-estimated expiry → ML priority score.</p>
        <div className="reason"><TimerReset /> Expiry is calculated automatically</div>
        <div className="reason"><BrainCircuit /> Priority is scored from the rescue window</div>
      </div>
    </div></section>
    <section className="impact"><div><strong>AI expiry estimation</strong><span>Prepared time + food type</span></div><div><strong>ML priority scoring</strong><span>0–100 rescue urgency</span></div><div><strong>Role-based workflow</strong><span>Donor, NGO and volunteer</span></div><div><strong>JWT API</strong><span>Protected REST actions</span></div></section>
    <section className="section"><div className="container"><div className="center"><span className="eyebrow">END-TO-END WORKFLOW</span><h2>One platform, with intelligence built in.</h2><p>Every step in the screenshot workflow is represented as a real application feature.</p></div>
      <div className="cards">{workflow.map(([Icon, title, text]) => <Info key={title} icon={<Icon />} title={title} text={text} />)}</div>
    </div></section>
  </main>;
}
function Info({ icon, title, text }) { return <article className="info"><div>{icon}</div><h3>{title}</h3><p>{text}</p></article>; }

function Auth({ title, subtitle, children }) { return <main className="auth"><div className="auth-card"><div className="auth-logo"><span className="logo"><Leaf /></span></div><h2>{title}</h2><p>{subtitle}</p>{children}</div></main>; }
function Field({ label, value, onChange, type = "text", required = true, placeholder = "" }) {
  return <label>{label}<input type={type} value={value} required={required} placeholder={placeholder} onChange={e => onChange(e.target.value)} /></label>;
}
function Login({ setUser }) {
  const nav = useNavigate(), [form, setForm] = useState({ username: "", password: "" }), [error, setError] = useState("");
  return <Auth title="Welcome back" subtitle="Sign in to your ZeroBite account."><form onSubmit={async e => { e.preventDefault(); setError(""); try { setUser(await login(form.username, form.password)); nav("/dashboard"); } catch (err) { setError(err.response?.data?.detail || "Login failed."); } }}>
    <Field label="Username" value={form.username} onChange={v => setForm({ ...form, username: v })} />
    <Field label="Password" type="password" value={form.password} onChange={v => setForm({ ...form, password: v })} />
    {error && <div className="error">{error}</div>}<button className="btn primary full">Sign in <ArrowRight /></button>
    <p className="auth-foot">New user? <Link to="/register">Create an account</Link></p>
  </form></Auth>;
}
function Register({ setUser }) {
  const nav = useNavigate(), [form, setForm] = useState({ username: "", email: "", password: "", first_name: "", last_name: "", phone: "", role: "donor" }), [error, setError] = useState("");
  const update = (k, v) => setForm({ ...form, [k]: v });
  return <Auth title="Create your account" subtitle="Choose a role to participate in food rescue."><form onSubmit={async e => { e.preventDefault(); setError(""); try { await register(form); setUser(await login(form.username, form.password)); nav("/dashboard"); } catch (err) { setError(formatError(err.response?.data) || "Registration failed."); } }}>
    <div className="two"><Field label="First name" value={form.first_name} onChange={v => update("first_name", v)} /><Field label="Last name" value={form.last_name} onChange={v => update("last_name", v)} /></div>
    <Field label="Username" value={form.username} onChange={v => update("username", v)} /><Field label="Email" type="email" value={form.email} onChange={v => update("email", v)} />
    <div className="two"><Field label="Password" type="password" value={form.password} onChange={v => update("password", v)} /><Field label="Phone" value={form.phone} onChange={v => update("phone", v)} /></div>
    <label>Role<select value={form.role} onChange={e => update("role", e.target.value)}><option value="donor">Donor</option><option value="ngo">NGO</option><option value="volunteer">Volunteer</option></select></label>
    {error && <div className="error">{error}</div>}<button className="btn primary full">Create account <ArrowRight /></button>
  </form></Auth>;
}

function Donations({ user }) {
  const [items, setItems] = useState([]), [q, setQ] = useState(""), [message, setMessage] = useState("");
  const load = () => listDonations(q).then(setItems).catch(() => setMessage("Unable to load donations."));
  useEffect(() => { load(); const t = setInterval(load, 10000); return () => clearInterval(t); }, [q]);
  const claim = async id => { if (!user) return setMessage("Please log in as an NGO or volunteer to request a pickup."); try { await requestPickup(id); setMessage("Pickup request created successfully."); load(); } catch (e) { setMessage(formatError(e.response?.data) || "Request failed."); } };
  return <main className="section"><div className="container"><div className="page-title"><span className="eyebrow">LIVE-REFRESHED AI RANKING</span><h1>Available donations</h1><p>Active records refresh automatically every 10 seconds and expired records are hidden.</p></div>
    <div className="search"><Search /><input placeholder="Search food or location..." value={q} onChange={e => setQ(e.target.value)} /></div>{message && <div className="notice">{message}</div>}
    <div className="donation-grid">{items.map(d => <DonationCard key={d.id} d={d} onClaim={claim} user={user} />)}</div>{!items.length && <div className="empty">No active donations found.</div>}
  </div></main>;
}
function DonationCard({ d, onClaim, user }) {
  const level = d.ai_label || "MEDIUM";
  return <article className="donation"><div className="food-img"><BrainCircuit size={42} /><span className={`priority ${level.toLowerCase()}`}>{level} · {Math.round(d.ai_score || 0)}/100</span></div>
    <div className="donation-body"><div className="mini"><span>{d.status}</span><small><MapPin size={13} /> {d.pickup_location}</small></div>
      <h3>{d.food_name}</h3><p>{d.quantity_meals} meals · {foodLabel(d.food_type)}</p>
      <div className="reason"><Clock3 size={15} /> {d.hours_to_expiry?.toFixed(1)} hours remaining</div>
      <div className="ai-reason"><Sparkles size={15} /><span>{d.ai_expiry_reason || "AI expiry estimate pending"}</span></div>
      <div className="ai-reason"><BrainCircuit size={15} /><span>{d.ai_reason || "AI priority pending"}</span></div>
      {user?.role !== "donor" && <button className="btn primary full" onClick={() => onClaim(d.id)}>Request pickup <ArrowRight /></button>}
    </div></article>;
}

function Donate({ user }) {
  const nav = useNavigate();
  const [form, setForm] = useState({ food_name: "", food_type: "rice", quantity_meals: 25, prepared_at: "", pickup_location: "", notes: "" });
  const [msg, setMsg] = useState(""); const [error, setError] = useState(""); const [result, setResult] = useState(null);
  if (!user || user.role !== "donor") return <main className="auth"><div className="auth-card"><h2>Donor account required</h2><p>Only donor accounts can publish surplus food.</p><Link className="btn primary full" to="/login">Login</Link></div></main>;
  const update = (k, v) => setForm({ ...form, [k]: v });
  const submit = async e => { e.preventDefault(); setError(""); setMsg(""); setResult(null); try {
    const payload = { ...form, prepared_at: new Date(form.prepared_at).toISOString(), quantity_meals: Number(form.quantity_meals) };
    const created = await createDonation(payload); setResult(created); setMsg("Donation published. AI expiry and rescue priority were calculated automatically.");
    setForm({ food_name: "", food_type: "rice", quantity_meals: 25, prepared_at: "", pickup_location: "", notes: "" });
  } catch (e2) { setError(formatError(e2.response?.data) || "Unable to publish donation."); } };
  return <main className="section"><div className="container narrow"><div className="page-title"><span className="eyebrow">DONOR MODULE</span><h1>Post surplus food</h1><p>Enter the prepared time. You do <strong>not</strong> enter an expiry time or coordinates — AI calculates the expiry automatically.</p></div>
    <div className="form-card"><form onSubmit={submit}>
      <Field label="Food name" value={form.food_name} onChange={v => update("food_name", v)} placeholder="e.g. Vegetable Biryani" />
      <label>Food type<select value={form.food_type} onChange={e => update("food_type", e.target.value)}><option value="rice">Rice / Biryani</option><option value="bread">Bread / Bakery</option><option value="curry">Curry / Dal</option><option value="vegetables">Vegetables</option><option value="fruit">Fruit</option><option value="other">Other</option></select></label>
      <Field label="Quantity (meals)" type="number" value={form.quantity_meals} onChange={v => update("quantity_meals", v)} />
      <Field label="Prepared Date & Time" type="datetime-local" value={form.prepared_at} onChange={v => update("prepared_at", v)} />
      <Field label="Pickup location" value={form.pickup_location} onChange={v => update("pickup_location", v)} placeholder="e.g. Guntur Community Center" />
      <label>Notes <span className="optional">(optional)</span><textarea value={form.notes} onChange={e => update("notes", e.target.value)} placeholder="Allergen or handoff details, if needed" /></label>
      <div className="ai-form-note"><Sparkles /><div><strong>AI will calculate</strong><span>Expiry time from prepared time + food type, then rescue priority from the estimated rescue window.</span></div></div>
      {error && <div className="error">{error}</div>}{msg && <div className="notice">{msg}</div>}
      {result && <div className="result-grid"><Result label="AI expiry" value={formatDate(result.expiry_at)} /><Result label="Rescue priority" value={`${result.ai_label} · ${Math.round(result.ai_score)}/100`} /><Result label="AI window" value={`${Number(result.ai_expiry_hours).toFixed(1)} hours`} /></div>}
      <div className="form-actions"><button className="btn primary full">Publish & run AI <BrainCircuit /></button><button type="button" className="btn soft full" onClick={() => nav("/dashboard")}>Go to dashboard</button></div>
    </form></div>
  </div></main>;
}
function Result({ label, value }) { return <div className="result"><span>{label}</span><strong>{value}</strong></div>; }

function Dashboard({ user }) {
  const [data, setData] = useState({ stats: null, rec: [], mine: [], pickups: [] }), [error, setError] = useState("");
  const load = async () => { if (!user) return; try { const [s, r, m, p] = await Promise.all([stats(), recommended(), myDonations(), pickups()]); setData({ stats: s, rec: r, mine: m, pickups: p }); } catch (e) { setError("Unable to refresh dashboard."); } };
  useEffect(() => { load(); const t = setInterval(load, 10000); return () => clearInterval(t); }, [user]);
  if (!user) return <main className="auth"><div className="auth-card"><h2>Login required</h2><p>Sign in to view your role-based dashboard.</p><Link className="btn primary full" to="/login">Login</Link></div></main>;
  const change = async (id, status) => { try { await updatePickup(id, status); load(); } catch (e) { setError(formatError(e.response?.data) || "Status update failed."); } };
  const s = data.stats || {};
  return <main className="dashboard"><div className="container"><div className="dash-head"><div><span className="eyebrow">{user.role.toUpperCase()} DASHBOARD</span><h1>Food rescue control center</h1><p>Role-based actions, AI ranking and pickup status in one place.</p></div>{user.role === "donor" && <Link className="btn primary" to="/donate">Post surplus food <ArrowRight /></Link>}</div>
    {error && <div className="error">{error}</div>}
    <section className="metrics"><Metric icon={<PackageCheck />} value={s.total_donations || 0} label="Total donations" /><Metric icon={<Clock3 />} value={s.active_donations || 0} label="Active donations" /><Metric icon={<HeartHandshake />} value={s.rescued_meals || 0} label="Rescued meals" /></section>
    {user.role === "donor" ? <DonorDashboard mine={data.mine} pickups={data.pickups} change={change} /> : <PartnerDashboard rec={data.rec} pickups={data.pickups} change={change} />}
  </div></main>;
}
function DonorDashboard({ mine, pickups: ps, change }) { return <>
  <section className="panel"><div className="panel-head"><div><h2>Your donations</h2><p>AI-estimated expiry and ML rescue priority for every post.</p></div><PackageCheck /></div>
    {mine.length ? mine.map(d => <div className="rec" key={d.id}><div><strong>{d.food_name} · {d.quantity_meals} meals</strong><span>{d.status} · expiry {formatDate(d.expiry_at)} · {d.pickup_location}</span></div><b className={`pill ${(d.ai_label || "medium").toLowerCase()}`}>{d.ai_label} {Math.round(d.ai_score || 0)}/100</b></div>) : <div className="empty">No donations posted yet.</div>}
  </section>
  <PickupPanel pickups={ps} change={change} role="donor" />
</>; }
function PartnerDashboard({ rec, pickups: ps, change, role }) { return <>
  <section className="panel"><div className="panel-head"><div><h2>AI recommendations</h2><p>Highest-priority available donations.</p></div><BrainCircuit /></div>
    {rec.slice(0, 8).map(d => <div className="rec" key={d.id}><div><strong>{d.food_name} · {d.quantity_meals} meals</strong><span>{d.pickup_location} · {d.hours_to_expiry?.toFixed(1)} hours left</span></div><b className={`pill ${(d.ai_label || "medium").toLowerCase()}`}>{d.ai_label} {Math.round(d.ai_score || 0)}/100</b></div>)}
    {!rec.length && <div className="empty">No available donations right now.</div>}
  </section>
  <PickupPanel pickups={ps} change={change} role={role || "partner"} />
</>; }
function PickupPanel({ pickups: ps, change, role }) { return <section className="panel" style={{ marginTop: 20 }}><div className="panel-head"><div><h2>Pickup requests</h2><p>{role === "donor" ? "Requests received for your donations." : "Your pickup workflow."}</p></div><Truck /></div>
  {ps.length ? ps.map(p => <div className="rec pickup-row" key={p.id}><div><strong>{p.donation_details?.food_name || `Donation #${p.donation}`}</strong><span>{p.requester_name || "partner"} · {p.status} · {p.donation_details?.pickup_location || "pickup location"}</span></div>
    <div className="pickup-actions">{role === "donor" && p.status === "pending" && <button className="btn soft" onClick={() => change(p.id, "accepted")}>Accept</button>}{role !== "donor" && p.status === "accepted" && <button className="btn soft" onClick={() => change(p.id, "collected")}>Mark collected</button>}{role !== "donor" && p.status === "collected" && <button className="btn soft" onClick={() => change(p.id, "delivered")}>Mark delivered</button>}{(p.status === "pending" || p.status === "accepted") && <span className={`status-dot ${p.status}`}><ClipboardCheck size={14} /> {p.status}</span>}</div>
  </div>) : <div className="empty">No pickup requests yet.</div>}
</section>; }
function Metric({ icon, value, label }) { return <div className="metric"><div>{icon}</div><strong>{value}</strong><span>{label}</span></div>; }
function Footer() { return <footer><div className="container"><strong>ZeroBite AI</strong><p>B.Tech final-year project · React + Django REST + scikit-learn · SQLite demo / MySQL deployment</p></div></footer>; }

function foodLabel(v) { return ({ rice: "Rice / Biryani", bread: "Bread / Bakery", curry: "Curry / Dal", vegetables: "Vegetables", fruit: "Fruit", other: "Other" }[v] || v); }
function formatDate(v) { return v ? new Date(v).toLocaleString([], { dateStyle: "medium", timeStyle: "short" }) : "—"; }
function formatError(data) { if (!data) return ""; if (typeof data === "string") return data; if (data.detail) return data.detail; return Object.entries(data).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(", ") : v}`).join(" | "); }

createRoot(document.getElementById("root")).render(<BrowserRouter><App /></BrowserRouter>);
