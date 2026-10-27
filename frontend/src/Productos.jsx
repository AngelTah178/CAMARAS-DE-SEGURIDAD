import { useEffect, useState } from "react";

const categorias = ["camara", "dvr", "nvr", "accesorio"];
const initial = { sku: "", nombre: "", categoria: "camara", precio: "", stockMinimo: "0", marca: "", modelo: "" };

export default function Productos({ token, onUnauthorized }) {
  const [rows, setRows] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [searchInput, setSearchInput] = useState("");
  const [search, setSearch] = useState("");
  const [categoria, setCategoria] = useState("");
  const [estado, setEstado] = useState("activo");
  const [busy, setBusy] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(initial);
  const [refresh, setRefresh] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    async function load() {
      setBusy(true);
      setError("");
      try {
        const qs = new URLSearchParams({ pagina: String(page), limite: "10" });
        if (search) qs.set("buscar", search);
        if (categoria) qs.set("categoria", categoria);
        if (estado) qs.set("estado", estado);
        const response = await fetch(`/api/productos?${qs}`, {
          headers: { Authorization: `Bearer ${token}` },
          signal: controller.signal,
        });
        if (response.status === 401 || response.status === 403) {
          onUnauthorized();
          return;
        }
        if (!response.ok) throw new Error("No fue posible consultar los productos.");
        const data = await response.json();
        if (!controller.signal.aborted) {
          setRows(data.items);
          setTotal(data.total);
        }
      } catch (err) {
        if (!controller.signal.aborted) setError(err.message);
      } finally {
        if (!controller.signal.aborted) setBusy(false);
      }
    }
    load();
    return () => controller.abort();
  }, [token, page, search, categoria, estado, refresh, onUnauthorized]);

  function openCreate() {
    setEditing("new");
    setForm({ ...initial });
    setError("");
    setNotice("");
  }
  function openEdit(row) {
    setEditing(row);
    setForm({ sku: row.sku, nombre: row.nombre, categoria: row.categoria, precio: String(row.precio), stockMinimo: String(row.stockMinimo), marca: row.marca || "", modelo: row.modelo || "" });
    setError("");
    setNotice("");
  }
  function update(key, value) { setForm(previous => ({ ...previous, [key]: value })); }

  async function save(event) {
    event.preventDefault();
    if (saving) return;
    setError("");
    setSaving(true);
    const creating = editing === "new";
    const payload = {
      nombre: form.nombre.trim(),
      categoria: form.categoria,
      precio: Number(form.precio),
      stockMinimo: Number(form.stockMinimo),
      marca: form.marca.trim(),
      modelo: form.modelo.trim(),
    };
    if (creating) payload.sku = form.sku.trim();
    try {
      const response = await fetch(creating ? "/api/productos" : `/api/productos/${editing.id}`, {
        method: creating ? "POST" : "PATCH",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(payload),
      });
      if (response.status === 401 || response.status === 403) { onUnauthorized(); return; }
      if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        throw new Error(response.status === 409 ? "El SKU ya está registrado." : typeof body.detail === "string" ? body.detail : "Revisa los datos del formulario.");
      }
      setEditing(null);
      setNotice(creating ? "Producto registrado correctamente." : "Producto actualizado correctamente.");
      setPage(1);
      setRefresh(n => n + 1);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  async function deactivate(row) {
    if (!window.confirm(`¿Desactivar ${row.nombre} (${row.sku})? El producto seguirá en MongoDB.`)) return;
    setError("");
    setNotice("");
    try {
      const response = await fetch(`/api/productos/${row.id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.status === 401 || response.status === 403) { onUnauthorized(); return; }
      if (!response.ok) throw new Error("No se pudo desactivar el producto.");
      setNotice("Producto desactivado.");
      setRefresh(n => n + 1);
    } catch (err) { setError(err.message); }
  }

  const pages = Math.max(1, Math.ceil(total / 10));
  return <section className="mt-4">
    <div className="d-flex justify-content-between align-items-center gap-3 flex-wrap mb-3">
      <div><h2 className="h4 mb-1">Productos</h2><p className="text-muted-app mb-0">Cámaras, DVR, NVR y accesorios.</p></div>
      <button className="btn btn-primary" onClick={openCreate}>+ Registrar producto</button>
    </div>
    <div className="dashboard-card mb-3">
      <form className="row g-2" onSubmit={e => { e.preventDefault(); setPage(1); setSearch(searchInput.trim()); }}>
        <div className="col-md-5"><label htmlFor="buscar-producto" className="form-label">Buscar por nombre o SKU</label><input id="buscar-producto" className="form-control" value={searchInput} onChange={e => setSearchInput(e.target.value)} maxLength={100} /></div>
        <div className="col-md-3"><label htmlFor="categoria-filtro" className="form-label">Categoría</label><select id="categoria-filtro" className="form-select" value={categoria} onChange={e => { setCategoria(e.target.value); setPage(1); }}><option value="">Todas</option>{categorias.map(c => <option key={c} value={c}>{c.toUpperCase()}</option>)}</select></div>
        <div className="col-md-2"><label htmlFor="estado-filtro" className="form-label">Estado</label><select id="estado-filtro" className="form-select" value={estado} onChange={e => { setEstado(e.target.value); setPage(1); }}><option value="">Todos</option><option value="activo">Activos</option><option value="inactivo">Inactivos</option></select></div>
        <div className="col-md-2 d-flex align-items-end"><button className="btn btn-outline-primary w-100" type="submit">Buscar</button></div>
      </form>
    </div>
    {notice && <div role="status" className="alert alert-success">{notice}</div>}
    {error && <div role="alert" className="alert alert-danger">{error}</div>}
    <div className="dashboard-card">
      <div className="table-responsive">
        <table className="table table-hover align-middle">
          <thead><tr><th>SKU</th><th>Producto</th><th>Categoría</th><th>Precio</th><th>Stock</th><th>Estado</th><th>Acciones</th></tr></thead>
          <tbody>{rows.map(row => <tr key={row.id}><td>{row.sku}</td><td><strong>{row.nombre}</strong><div className="small text-muted-app">{[row.marca, row.modelo].filter(Boolean).join(" · ")}</div></td><td>{row.categoria.toUpperCase()}</td><td>${Number(row.precio).toFixed(2)}</td><td>{row.stock}</td><td><span className={`badge text-bg-${row.estado === "activo" ? "success" : "secondary"}`}>{row.estado}</span></td><td><div className="d-flex gap-2">{row.estado === "activo" && <><button className="btn btn-outline-primary btn-sm" onClick={() => openEdit(row)}>Editar</button><button className="btn btn-outline-danger btn-sm" onClick={() => deactivate(row)}>Desactivar</button></>}</div></td></tr>)}</tbody>
        </table>
        {!busy && rows.length === 0 && <p className="text-center text-muted-app py-3">No hay productos para estos filtros.</p>}
        {busy && <p role="status" className="text-muted-app">Cargando productos…</p>}
      </div>
      <div className="d-flex justify-content-between align-items-center gap-2 flex-wrap">
        <span className="text-muted-app small">{total} productos · página {page} de {pages}</span>
        <div className="btn-group"><button className="btn btn-outline-secondary btn-sm" disabled={page <= 1 || busy} onClick={() => setPage(n => n - 1)}>Anterior</button><button className="btn btn-outline-secondary btn-sm" disabled={page >= pages || busy} onClick={() => setPage(n => n + 1)}>Siguiente</button></div>
      </div>
    </div>
    {editing && <div className="product-modal-backdrop" role="presentation"><section className="product-modal dashboard-card" role="dialog" aria-modal="true" aria-labelledby="product-form-title">
      <div className="d-flex justify-content-between align-items-center mb-3"><h3 className="h5 mb-0" id="product-form-title">{editing === "new" ? "Registrar producto" : "Editar producto"}</h3><button type="button" className="btn-close" aria-label="Cerrar" disabled={saving} onClick={() => setEditing(null)} /></div>
      <form onSubmit={save}><div className="row g-3">
        <div className="col-md-6"><label className="form-label" htmlFor="sku">SKU</label><input id="sku" className="form-control" value={form.sku} onChange={e => update("sku", e.target.value)} required disabled={editing !== "new" || saving} maxLength={50} /></div>
        <div className="col-md-6"><label className="form-label" htmlFor="nombre">Nombre</label><input id="nombre" className="form-control" value={form.nombre} onChange={e => update("nombre", e.target.value)} required maxLength={150} disabled={saving} /></div>
        <div className="col-md-6"><label className="form-label" htmlFor="categoria">Categoría</label><select id="categoria" className="form-select" value={form.categoria} onChange={e => update("categoria", e.target.value)} disabled={saving}>{categorias.map(c => <option key={c} value={c}>{c.toUpperCase()}</option>)}</select></div>
        <div className="col-md-6"><label className="form-label" htmlFor="precio">Precio</label><input id="precio" type="number" min="0" step="0.01" className="form-control" value={form.precio} onChange={e => update("precio", e.target.value)} required disabled={saving} /></div>
        <div className="col-md-6"><label className="form-label" htmlFor="stock-min">Stock mínimo</label><input id="stock-min" type="number" min="0" step="1" className="form-control" value={form.stockMinimo} onChange={e => update("stockMinimo", e.target.value)} required disabled={saving} /></div>
        <div className="col-md-6"><label className="form-label" htmlFor="marca">Marca</label><input id="marca" className="form-control" value={form.marca} onChange={e => update("marca", e.target.value)} maxLength={80} disabled={saving} /></div>
        <div className="col-md-6"><label className="form-label" htmlFor="modelo">Modelo</label><input id="modelo" className="form-control" value={form.modelo} onChange={e => update("modelo", e.target.value)} maxLength={80} disabled={saving} /></div>
      </div><p className="small text-muted-app mt-3">El stock inicial es 0. Las existencias se modificarán desde movimientos.</p>
      <div className="d-flex justify-content-end gap-2"><button className="btn btn-outline-secondary" type="button" disabled={saving} onClick={() => setEditing(null)}>Cancelar</button><button className="btn btn-primary" type="submit" disabled={saving}>{saving ? "Guardando…" : "Guardar"}</button></div></form>
    </section></div>}
  </section>;
}
