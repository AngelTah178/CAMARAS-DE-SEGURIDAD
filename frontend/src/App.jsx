import { useEffect, useState } from "react";
import "./styles.css";
import "./productos.css";
import Productos from "./Productos.jsx";

const TOKEN_KEY = "securitystock_access_token";

export default function App() {
  const [token, setToken] = useState(() => sessionStorage.getItem(TOKEN_KEY));
  const [admin, setAdmin] = useState(null);
  const [checking, setChecking] = useState(Boolean(token));
  const [usuario, setUsuario] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [view, setView] = useState("dashboard");
  const handleUnauthorized = () => {
    sessionStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setAdmin(null);
    setError("Tu sesión no es válida. Inicia sesión de nuevo.");
  };

  useEffect(() => {
    if (!token) {
      setAdmin(null);
      setChecking(false);
      return;
    }
    const controller = new AbortController();
    setChecking(true);
    fetch("/api/auth/me", {
      headers: { Authorization: `Bearer ${token}` },
      signal: controller.signal,
    })
      .then(async (response) => {
        if (!response.ok) throw new Error(response.status === 401 || response.status === 403 ? "Sesión inválida." : "No se pudo verificar la sesión.");
        return response.json();
      })
      .then((data) => {
        if (!controller.signal.aborted) setAdmin(data);
      })
      .catch((err) => {
        if (controller.signal.aborted) return;
        sessionStorage.removeItem(TOKEN_KEY);
        setToken(null);
        setAdmin(null);
        setError(err.message);
      })
      .finally(() => {
        if (!controller.signal.aborted) setChecking(false);
      });
    return () => controller.abort();
  }, [token]);

  async function login(event) {
    event.preventDefault();
    if (loading) return;
    setError("");
    setLoading(true);
    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ usuario: usuario.trim(), password }),
      });
      const data = await response.json();
      if (!response.ok || !data.access_token) {
        setError(response.status === 401 ? "Usuario o contraseña incorrectos." : "No se pudo iniciar sesión. Comprueba el servicio.");
        return;
      }
      sessionStorage.setItem(TOKEN_KEY, data.access_token);
      setPassword("");
      setToken(data.access_token);
    } catch {
      setError("Sin conexión con FastAPI. Verifica que el backend esté ejecutándose.");
    } finally {
      setLoading(false);
    }
  }

  function logout() {
    sessionStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setAdmin(null);
    setPassword("");
    setError("");
  }

  if (token && (checking || !admin)) {
    return <main className="min-vh-100 d-flex justify-content-center align-items-center">
      <div role="status" className="text-center">
        <div className="spinner-border text-primary mb-3" />
        <p>Verificando sesión…</p>
      </div>
    </main>;
  }

  if (admin) {
    return <div className="app-dashboard">
      <header className="app-topbar py-3">
        <div className="container d-flex align-items-center justify-content-between gap-3">
          <strong>◉ SecurityStock <span className="text-muted-app fw-normal">/ Panel administrativo</span></strong>
          <button className="btn btn-outline-secondary btn-sm" type="button" onClick={logout}>Cerrar sesión</button>
        </div>
      </header>
      <main className="container py-5">
        <nav className="d-flex gap-2 mb-4" aria-label="Secciones del sistema">
          <button type="button" className={`btn ${view === "dashboard" ? "btn-primary" : "btn-outline-primary"}`} onClick={() => setView("dashboard")}>Dashboard</button>
          <button type="button" className={`btn ${view === "productos" ? "btn-primary" : "btn-outline-primary"}`} onClick={() => setView("productos")}>Productos</button>
        </nav>
        {view === "productos" ? <Productos token={token} onUnauthorized={handleUnauthorized} /> : <>
        <p className="text-muted-app mb-1">Panel de control</p>
        <h1 className="h2 mb-4">Bienvenido, {admin.usuario}</h1>
        <section className="dashboard-card">
          <span className="badge text-bg-success mb-3">Sesión autenticada</span>
          <h2 className="h4">Inventario de cámaras de seguridad</h2>
          <p className="text-muted-app mb-0">Tu cuenta está validada por FastAPI y MongoDB Atlas. Consulta y administra productos desde la sección Productos. Los movimientos y la auditoría se implementarán en próximos sprints.</p>
        </section>
        </>}
      </main>
    </div>;
  }

  return <div className="auth-shell">
    <section className="auth-hero" aria-label="Presentación del sistema">
      <div className="hero-content">
        <div className="hero-symbol" aria-hidden="true">◉</div>
        <p className="text-uppercase fw-semibold small opacity-75">SecurityStock</p>
        <h1 className="display-5 fw-bold">Control de inventario de seguridad</h1>
        <p className="lead opacity-75 mt-3">Administra tus equipos de videovigilancia desde un único espacio seguro.</p>
      </div>
    </section>
    <main className="auth-panel">
      <section className="login-card" aria-labelledby="login-title">
        <span className="badge text-bg-light border mb-3">Acceso administrativo</span>
        <h2 className="h3 fw-bold" id="login-title">Iniciar sesión</h2>
        <p className="text-muted-app mb-4">Introduce las credenciales del administrador.</p>
        <form onSubmit={login}>
          <div className="mb-3">
            <label htmlFor="usuario" className="form-label fw-semibold">Usuario</label>
            <input className="form-control form-control-lg" id="usuario" value={usuario} onChange={(e) => setUsuario(e.target.value)} autoComplete="username" maxLength={64} required disabled={loading} />
          </div>
          <div className="mb-3">
            <label htmlFor="password" className="form-label fw-semibold">Contraseña</label>
            <input className="form-control form-control-lg" id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" required disabled={loading} />
          </div>
          {error && <div role="alert" className="alert alert-danger py-2">{error}</div>}
          <button type="submit" disabled={loading} className="btn btn-primary btn-lg w-100">
            {loading ? "Ingresando…" : "Entrar al sistema"}
          </button>
        </form>
        <p className="small text-muted-app mt-4 mb-0 text-center">Acceso reservado para administradores autorizados.</p>
      </section>
    </main>
  </div>;
}
