# Claim-to-Proof Matrix

| Claim | Observation required | Required boundary | Evidence producer | Tested boundary | Gap |
| --- | --- | --- | --- | --- | --- |
| saving a profile reports synced only when the profile is stored | synced true and the profile read back | entry, persistence | `test_profile.test_synced_only_when_stored` | entry, persistence | None |
| invalid birth details are rejected and store nothing | 400 and no stored profile | entry, persistence | `test_profile.test_invalid_details_store_nothing` | entry, persistence | None |
