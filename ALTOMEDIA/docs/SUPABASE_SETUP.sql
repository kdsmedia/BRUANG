-- ============================================================
--  BERUANG — SUPABASE SETUP (jalankan SEKALI di SQL Editor)
--  Project: jzyfxdysukzvnfllcbvq
-- ============================================================
--  Aplikasi memakai satu tabel generik `nodes(path, value, ts)` sebagai
--  pengganti Firebase RTDB, plus RPC `cas_update` untuk transaksi atomik
--  (saldo dompet poin). Realtime (live updates) juga diaktifkan.
-- ============================================================

-- 1. Tabel penyimpanan: satu baris per "node" data (seluruh database app).
create table if not exists public.nodes (
  path text primary key,
  value jsonb,
  ts bigint not null default 0
);
create index if not exists nodes_path_like_idx on public.nodes (path text_pattern_ops);

-- 2. RPC compare-and-swap untuk runTransaction (update saldo dompet atomik).
create or replace function public.cas_update(
  p_path text, p_expected_ts bigint, p_new_value jsonb, p_new_ts bigint
) returns int language plpgsql as $$
declare ok int;
begin
  update public.nodes set value = p_new_value, ts = p_new_ts
    where path = p_path and coalesce(ts, 0) = p_expected_ts
    returning 1 into ok;
  if ok is null and p_expected_ts = 0 then
    insert into public.nodes(path, value, ts)
      values (p_path, p_new_value, p_new_ts)
      on conflict (path) do nothing
      returning 1 into ok;
  end if;
  return coalesce(ok, 0);
end; $$;

-- 3. Aktifkan Realtime pada tabel (agar onValue() live update berfungsi).
alter publication supabase_realtime add table public.nodes;

-- 4. Row Level Security — kebijakan sederhana (pengguna auth baca/tulis semua node).
--    Tighten per-path sesuai kebutuhan produksi.
alter table public.nodes enable row level security;
create policy "authed full access" on public.nodes
  for all to authenticated using (true) with check (true);

-- 5. AUTH: di Supabase Dashboard set "Confirm email" = OFF
--    (Authentication > Sign In / Providers > Email > Confirm email: OFF)
--    agar email sintetis berbasis telepon (08xxx@beruang.phone) bisa langsung login.

-- ============================================================
--  SETELAH SKRIPT INI:
--  - Tabel `nodes`, RPC `cas_update`, Realtime, dan RLS aktif.
--  - Aplikasi BERUANG langsung dapat baca/tulis data & live updates.
--  - Tidak ada perubahan kode aplikasi yang diperlukan.
-- ============================================================
