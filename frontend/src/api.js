import axios from "axios";
const api=axios.create({baseURL:"/api"});
api.interceptors.request.use(c=>{const t=localStorage.getItem("access_token");if(t)c.headers.Authorization=`Bearer ${t}`;return c;});
api.interceptors.response.use(r=>r,async e=>{if(e.response?.status===401&&localStorage.getItem("refresh_token")){try{const r=await axios.post("/api/auth/token/refresh/",{refresh:localStorage.getItem("refresh_token")});localStorage.setItem("access_token",r.data.access);e.config.headers.Authorization=`Bearer ${r.data.access}`;return api(e.config)}catch{logout()}}throw e});
export async function register(data){return (await api.post("/auth/register/",data)).data}
export async function login(username,password){const r=(await api.post("/auth/token/",{username,password})).data;localStorage.setItem("access_token",r.access);localStorage.setItem("refresh_token",r.refresh);return getMe()}
export async function getMe(){return (await api.get("/auth/me/")).data}
export function logout(){localStorage.removeItem("access_token");localStorage.removeItem("refresh_token")}
export async function listDonations(q=""){return (await api.get(`/donations/donations/?active=true${q?`&q=${encodeURIComponent(q)}`:""}`)).data}
export async function createDonation(data){return (await api.post("/donations/donations/",data)).data}
export async function requestPickup(id,message=""){return (await api.post(`/donations/donations/${id}/request_pickup/`,{message})).data}
export async function myDonations(){return (await api.get("/donations/donations/my/")).data}
export async function recommended(){return (await api.get("/donations/donations/recommended/")).data}
export async function stats(){return (await api.get("/donations/donations/stats/")).data}
export async function pickups(){return (await api.get("/donations/pickup-requests/")).data}
export async function updatePickup(id,status){return (await api.post(`/donations/pickup-requests/${id}/status/`,{status})).data}
