-- ============================================================
--  BERUANG — SUPABASE SETUP (jalankan SEKALI di SQL Editor)
--  Project: jzyfxdysukzvnfllcbvq
--  Region : ap-south-1
-- ============================================================
--  Skrip LENGKAP & IDEMPOTENT (boleh dijalankan berulang tanpa error).
--  Mencakup:
--    1. Tabel `nodes` (pengganti Firebase RTDB) + index
--    2. RPC `cas_update` (transaksi atomik saldo dompet)
--    3. Realtime (live updates)
--    4. Row Level Security untuk `nodes`
--    5. Storage bucket `media` + policy (upload gambar posting/story/avatar)
--    6. GRANT akses eksekusi & konfigurasi Auth (di dashboard)
-- ============================================================


-- ============================================================
--  1. TABEL NODES — satu baris per "node" data (seluruh database app)
-- ============================================================
create table if not exists public.nodes (
  path text primary key,
  value jsonb,
  ts bigint not null default 0
);

-- Index untuk query path LIKE 'prefix/%' (rekonstruksi tree pada onValue).
create index if not exists nodes_path_like_idx on public.nodes (path text_pattern_ops);


-- ============================================================
--  2. RPC cas_update — compare-and-swap untuk runTransaction
--     (update saldo dompet poin secara atomik, anti race condition)
-- ============================================================
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

-- Berikan izin eksekusi RPC ke user yang login (anon tidak butuh ini).
grant execute on function public.cas_update(text, bigint, jsonb, bigint) to authenticated;


-- ============================================================
--  3. REALTIME — aktifkan live updates pada tabel nodes
--     (agar onValue() di aplikasi langsung update tanpa refresh)
-- ============================================================
do $$
begin
  if not exists (
    select 1 from pg_publication_tables
    where pubname = 'supabase_realtime' and tablename = 'nodes'
  ) then
    alter publication supabase_realtime add table public.nodes;
  end if;
end $$;


-- ============================================================
--  4. ROW LEVEL SECURITY untuk tabel nodes
--     (user login baca/tulis semua node app; anon read agar halaman
--      publik tetap jalan sebelum login jika diperlukan)
-- ============================================================
alter table public.nodes enable row level security;

-- Policy digeser ke DROP dulu lalu CREATE agar idempotent.
drop policy if exists "authed full access" on public.nodes;
create policy "authed full access" on public.nodes
  for all to authenticated using (true) with check (true);

-- Izin eksplisit (RLS aktif, tapi pastikan grant dasar ada).
grant select, insert, update, delete on public.nodes to authenticated;


-- ============================================================
--  5. STORAGE BUCKET "media" — penyimpanan gambar
--     (posting, story, foto profil). Jika bucket belum ada, aplikasi
--      fallback ke base64 di DB (lambat & boros). Buat bucket ini agar
--      upload menyimpan public URL yang cepat & ringan.
-- ============================================================

-- 5a. Buat bucket PUBLIC bernama "media".
insert into storage.buckets (id, name, public)
  values ('media', 'media', true)
  on conflict (id) do nothing;

-- 5b. Policy STORAGE — siapa saja bisa baca (public URL), user login bisa upload.
--     DROP dulu lalu CREATE agar idempotent (tidak error jika di-run ulang).
drop policy if exists "media read" on storage.objects;
create policy "media read" on storage.objects
  for select to anon, authenticated using (bucket_id = 'media');

drop policy if exists "media upload" on storage.objects;
create policy "media upload" on storage.objects
  for insert to authenticated with check (bucket_id = 'media');

drop policy if exists "media update" on storage.objects;
create policy "media update" on storage.objects
  for update to authenticated using (bucket_id = 'media');

drop policy if exists "media delete" on storage.objects;
create policy "media delete" on storage.objects
  for delete to authenticated using (bucket_id = 'media');


-- ============================================================
--  6. KONFIGURASI AUTH (DILAKUKAN DI DASHBOARD, BUKAN SQL)
--  ============================================================
--  Supabase Dashboard > Authentication > Sign In / Providers > Email:
--    - Confirm email : OFF   (wajib! agar email sintetis 08xxx@beruang.phone
--                              bisa langsung login tanpa verifikasi)
--    - Enable Email provider: ON
--  Opsional (jika ingin koneksi S3 dari server/CLI):
--    - Dashboard > Storage > S3 Connection > gunakan kredensial S3
--      (endpoint: https://jzyfxdysukzvnfllcbvq.storage.supabase.co/storage/v1/s3,
--       region: ap-south-1). Aplikasi browser/APK TIDAK butuh S3 — cukup
--      bucket + policy di atas.

-- ============================================================
--  SETELAH SKRIP INI:
--    - Tabel `nodes`, RPC `cas_update`, Realtime, RLS aktif.
--    - Bucket Storage `media` + policy aktif (upload gambar via public URL).
--    - Aplikasi BERUANG langsung dapat baca/tulis data, live updates,
--      dan upload gambar ke Storage tanpa delay/bug.
--    - Tidak ada perubahan kode aplikasi yang diperlukan.
-- ============================================================
