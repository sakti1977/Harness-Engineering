def save_profile(store, profile):
    store.append(profile)
    return {"synced": True}
