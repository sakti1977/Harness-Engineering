\set ON_ERROR_STOP 0
\set U '11111111-1111-1111-1111-111111111111'
-- Device 1 and device 2 both pull: revision 1 after the first push.
SELECT public.sync_push(:'U', '{"chart":{"v":1}}', '[{"observation_id":"o0","timestamp":"2026-11-01T00:00:00Z","text":"first","category":"c","exchange_index":0}]', NULL, false);
-- Device 1 pushes on top of revision 1 (correct).
SELECT 'device1' AS who, public.sync_push(:'U', '{"chart":{"v":2}}', '[{"observation_id":"o1","timestamp":"2026-11-02T00:00:00Z","text":"from device 1","category":"c","exchange_index":1}]', 1, false);
-- Device 2 still holds revision 1 and pushes stale coaching. Must be a conflict.
SELECT 'device2_stale' AS who, public.sync_push(:'U', '{"chart":{"v":3}}', '[{"observation_id":"o2","timestamp":"2026-11-03T00:00:00Z","text":"from stale device 2","category":"c","exchange_index":2}]', 1, false);
SELECT 'final_observations' AS what, string_agg(observation_id, ',' ORDER BY observation_id) AS ids FROM public.coaching_observations WHERE user_id = :'U';
SELECT 'final_revision' AS what, revision FROM public.user_profiles WHERE user_id = :'U';
