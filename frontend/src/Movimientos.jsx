import { useEffect, useState } from "react";

const KEY = "securitystock_pending_movement";
const initial = { productoId: "", tipo: "entrada", cantidad: "", stockObjetivo: "", motivo: "" };
const labels = { entrada: "Entrada", salida: "Salida", ajuste: "Ajuste" };

export default function Movimientos({ token, onUnauthorized }) {
  const [productos, setProductos] = useState([]);
  const [movimientos, setMovimientos] = useState([]);
  const [form, setForm] = useState(initial);
  const [pending, setPending] = useState(() => {
    try { return JSON.parse(sessionStorage.getItem(KEY) || "null"); } catch { return null; }
  });
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [refresh, setRefresh] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    async function load() {
      setLoading(true);
      try {
        const headers = { Authorization: `Bearer ${token}` };
        const [a, b] = await Promise.all([
          fetch("/api/productos?estado=activo&limite=100", { headers, signal: controller.signal }),
          fetch("/api/movimientos?limite=100", { headers, signal: controller.signal }),
        ]);
        if ([a.status, b.status].some(status => status === 401 || status === 403)) {
          onUnauthorized();
          return;
        }
        if (!a.ok || !b.ok) throw new Error("No fue posible cargar los datos de inventario.");
        const [products, moves] = await Promise.all([a.json(), b.json()]);
        if (!controller.signal.aborted) {
          setProductos(products.items || []);
          setMovimientos(moves.items || []);
        }
      } catch (err) {
        if (!controller.signal.aborted) setError(err.message);
      } finally {
        if (!controller.signal.aborted) setLoading(false);
      }
    }
    load();
    return () => controller.abort();
  }, [token, onUnauthorized, refresh]);

  async function transmit(payload) {
    setSaving(true);
    setError("");
    setSuccess("");
    try {
      const res = await fetch("/api/movimientos", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(payload),
      });
      if (res.status === 401 || res.status === 403) {
        onUnauthorized();
        return;
      }
      const result = await res.json().catch(() => ({}));
      if (!res.ok) {
        const message = typeof result.detail === "string" ? result.detail : "No se pudo guardar el movimiento.";
        if (res.status === 503 || (res.status === 409 && message.includes("concurrencia"))) {
          setError(`${message} Conservamos el identificador; reintenta la operación pendiente.`);
          return;
        }
        // Estos errores confirman que no se aplicó un movimiento nuevo.
        sessionStorage.removeItem(KEY);
        setPending(null);
        setError(message);
        return;
      }
      sessionStorage.removeItem(KEY);
      setPending(null);
      setForm(initial);
      setSuccess("Movimiento registrado correctamente.");
      setRefresh(n => n + 1);
    } catch {
      setError("La respuesta de la red es incierta. Reintenta solamente la operación pendiente, con el mismo identificador.");
    } finally {
      setSaving(false);
    }
  }

  function submit(e) {
    e.preventDefault();
    if (saving || pending) return;
    const target = Number(form.stockObjetivo);
    const qty = Number(form.cantidad);
    if (!form.productoId || form.motivo.trim().length < 3 ||
        (form.tipo === "ajuste"
          ? form.stockObjetivo === "" || !Number.isInteger(target) || target < 0
          : form.cantidad === "" || !Number.isInteger(qty) || qty <= 0)) {
      setError("Completa los campos con valores válidos.");
      return;
    }
    if (!globalThis.crypto?.randomUUID) {
      setError("Se necesita localhost o HTTPS para generar identificadores seguros.");
      return;
    }
    const request = {
      productoId: form.productoId,
      tipo: form.tipo,
      motivo: form.motivo.trim(),
      solicitudId: globalThis.crypto.randomUUID(),
      ...(form.tipo === "ajuste" ? { stockObjetivo: target } : { cantidad: qty }),
    };
    sessionStorage.setItem(KEY, JSON.stringify(request));
    setPending(request);
    transmit(request);
  }

  const lookup = new Map(productos.map(p => [p.id, p.sku]));
  return <section>
    <h1 className="h3 mb-1">Movimientos de inventario</h1>
    <p className="text-muted-app mb-4">Entradas, salidas, ajustes e historial de existencias.</p>
    <div className="dashboard-card mb-4">
      <h2 className="h5 mb-3">Registrar movimiento</h2>
      {error && <div role="alert" className="alert alert-danger">{error}</div>}
      {success && <div role="status" className="alert alert-success">{success}</div>}
      {pending && <div role="alert" className="alert alert-warning">
        <strong>Operación pendiente de confirmar.</strong>
        <p className="small mb-2">Identificador: {pending.solicitudId}. No inicies otra solicitud hasta resolver esta operación.</p>
        <button type="button" className="btn btn-warning btn-sm" disabled={saving} onClick={() => transmit(pending)}>Reintentar misma operación</button>
      </div>}
      <form className="row g-3" onSubmit={submit}>
        <div className="col-md-6">
          <label className="form-label" htmlFor="mov-producto">Producto activo</label>
          <select id="mov-producto" className="form-select" required disabled={saving || !!pending} value={form.productoId} onChange={e => setForm(p => ({ ...p, productoId: e.target.value }))}>
            <option value="">Seleccionar producto</option>
            {productos.map(p => <option key={p.id} value={p.id}>{p.sku} · {p.nombre} (stock {p.stock})</option>)}
          </select>
        </div>
        <div className="col-md-3">
          <label htmlFor="mov-tipo" className="form-label">Tipo</label>
          <select id="mov-tipo" className="form-select" value={form.tipo} disabled={saving || !!pending} onChange={e => setForm(p => ({ ...p, tipo: e.target.value }))}>
            <option value="entrada">Entrada</option><option value="salida">Salida</option><option value="ajuste">Ajuste</option>
          </select>
        </div>
        <div className="col-md-3">
          <label className="form-label" htmlFor="mov-cantidad">{form.tipo === "ajuste" ? "Stock objetivo" : "Cantidad"}</label>
          <input id="mov-cantidad" className="form-control" required type="number" step="1" min={form.tipo === "ajuste" ? 0 : 1} disabled={saving || !!pending}
            value={form.tipo === "ajuste" ? form.stockObjetivo : form.cantidad}
            onChange={e => setForm(p => ({ ...p, [form.tipo === "ajuste" ? "stockObjetivo" : "cantidad"]: e.target.value }))}/>
        </div>
        <div className="col-12">
          <label className="form-label" htmlFor="mov-motivo">Motivo</label>
          <textarea id="mov-motivo" className="form-control" required minLength={3} maxLength={300} rows={2} disabled={saving || !!pending}
            value={form.motivo} onChange={e => setForm(p => ({ ...p, motivo: e.target.value }))}/>
        </div>
        <div className="col-12 d-flex gap-2">
          <button type="submit" className="btn btn-primary" disabled={saving || !!pending}>{saving ? "Registrando…" : "Registrar movimiento"}</button>
          <button type="button" className="btn btn-outline-secondary" disabled={saving || !!pending} onClick={() => setForm(initial)}>Limpiar</button>
        </div>
      </form>
    </div>
    <div className="dashboard-card">
      <div className="d-flex justify-content-between align-items-center mb-3 gap-2">
        <h2 className="h5 mb-0">Historial reciente</h2>
        <button type="button" className="btn btn-outline-primary btn-sm" disabled={loading} onClick={() => setRefresh(n => n + 1)}>Actualizar</button>
      </div>
      <div className="table-responsive">
        <table className="table table-hover align-middle">
          <thead><tr><th>Fecha</th><th>Producto</th><th>Tipo</th><th>Cantidad</th><th>Anterior</th><th>Posterior</th><th>Motivo</th></tr></thead>
          <tbody>{movimientos.map(m => <tr key={m.id}>
            <td>{new Date(m.creadoEn).toLocaleString("es-MX")}</td>
            <td>{lookup.get(m.productoId) || m.productoId}</td>
            <td>{labels[m.tipo] || m.tipo}</td>
            <td>{m.cantidad}</td><td>{m.stockAnterior}</td><td>{m.stockPosterior}</td><td>{m.motivo}</td>
          </tr>)}</tbody>
        </table>
        {loading && <p role="status">Cargando movimientos…</p>}
        {!loading && movimientos.length === 0 && <p className="text-muted-app">No hay movimientos registrados.</p>}
      </div>
      <p className="small text-muted-app mb-0">Se muestran los últimos 100 movimientos.</p>
    </div>
  </section>;
}
