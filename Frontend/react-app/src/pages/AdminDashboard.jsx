import React, { useEffect, useMemo, useState } from "react";
import axios from "axios";
import { API_BASE_URL } from "../utils/api";

const AdminDashboard = () => {
  const [users, setUsers] = useState([]);
  const [experts, setExperts] = useState([]);
  const [badges, setBadges] = useState([]);
  const [regions, setRegions] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [authorized, setAuthorized] = useState(false);

  const adminKey = useMemo(() => {
    try { return localStorage.getItem('tg_admin_key') || ''; } catch { return ''; }
  }, []);

  useEffect(() => {
    if (!authorized) {
      const promptKey = adminKey || window.prompt('Enter admin access key:');
      if (promptKey && promptKey.length >= 6) {
        try { localStorage.setItem('tg_admin_key', promptKey); } catch {}
        setAuthorized(true);
      }
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!authorized) return;
    async function fetchAll() {
      setLoading(true);
      try {
        const [usersRes, expertsRes, badgesRes, regionsRes, catsRes] = await Promise.all([
          axios.get(`${API_BASE_URL}/api/admin/users`),
          axios.get(`${API_BASE_URL}/api/admin/experts`),
          axios.get(`${API_BASE_URL}/api/admin/badges`),
          axios.get(`${API_BASE_URL}/api/admin/regions`),
          axios.get(`${API_BASE_URL}/api/admin/categories`),
        ]);
        setUsers(usersRes.data);
        setExperts(expertsRes.data);
        setBadges(badgesRes.data);
        setRegions(regionsRes.data);
        setCategories(catsRes.data);
      } catch (err) {
        // eslint-disable-next-line
        console.error("Admin fetch error:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchAll();
  }, [authorized]);

  if (!authorized) {
    return (
      <div className="p-8 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 min-h-screen">
        <h1 className="text-2xl font-bold">Admin</h1>
        <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">Access key required. Reload page to retry.</p>
      </div>
    );
  }

  return (
    <div className="p-8 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 min-h-screen">
      <h1 className="text-3xl font-bold mb-6">Admin Dashboard</h1>
      {loading ? <p>Loading...</p> : (
        <div className="space-y-8">
          <section>
            <h2 className="text-xl font-semibold mb-2">Users</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full bg-white dark:bg-gray-800 rounded shadow">
                <thead>
                  <tr>
                    <th className="px-3 py-2">ID</th>
                    <th className="px-3 py-2">Username</th>
                    <th className="px-3 py-2">Email</th>
                    <th className="px-3 py-2">Active</th>
                    <th className="px-3 py-2">Created</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map(u => (
                    <tr key={u.id}>
                      <td className="px-3 py-2">{u.id}</td>
                      <td className="px-3 py-2">{u.username}</td>
                      <td className="px-3 py-2">{u.email}</td>
                      <td className="px-3 py-2">{u.is_active ? "Yes" : "No"}</td>
                      <td className="px-3 py-2">{u.created_at}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-2">Experts</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full bg-white dark:bg-gray-800 rounded shadow">
                <thead>
                  <tr>
                    <th className="px-3 py-2">ID</th>
                    <th className="px-3 py-2">Username</th>
                    <th className="px-3 py-2">Full Name</th>
                    <th className="px-3 py-2">Organization</th>
                    <th className="px-3 py-2">Badge</th>
                    <th className="px-3 py-2">Verified</th>
                    <th className="px-3 py-2">Verified At</th>
                  </tr>
                </thead>
                <tbody>
                  {experts.map(e => (
                    <tr key={e.id}>
                      <td className="px-3 py-2">{e.id}</td>
                      <td className="px-3 py-2">{e.username}</td>
                      <td className="px-3 py-2">{e.full_name}</td>
                      <td className="px-3 py-2">{e.organization}</td>
                      <td className="px-3 py-2">{e.badge_id}</td>
                      <td className="px-3 py-2">{e.is_verified ? "Yes" : "No"}</td>
                      <td className="px-3 py-2">{e.verified_at || "-"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-2">Badges</h2>
            <ul className="list-disc pl-6">
              {badges.map(b => (
                <li key={b.id} className="mb-1">
                  <span className="font-semibold" style={{ color: b.color }}>{b.name}</span>: {b.description}
                </li>
              ))}
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-2">Regions</h2>
            <div className="flex flex-wrap gap-2">
              {regions.map(r => (
                <span key={r} className="px-3 py-1 rounded bg-blue-100 text-blue-800 font-medium">{r.toUpperCase()}</span>
              ))}
            </div>
          </section>

          <section>
            <h2 className="text-xl font-semibold mb-2">Categories</h2>
            <div className="flex flex-wrap gap-2">
              {categories.map(c => (
                <span key={c} className="px-3 py-1 rounded bg-green-100 text-green-800 font-medium">{c}</span>
              ))}
            </div>
          </section>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;
