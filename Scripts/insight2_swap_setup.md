Presque 👌 — tu as levé les gros risques (plus d’`eval`, validation, fstab atomique, check espace, Btrfs ok).
Il reste **2 points à corriger** (sinon ça casse en pratique) + 2 mini-ajustements :

### 1) `configure_sysctl()` — variables perdues dans le sous-shell

`run` lance `bash -lc`, donc `$SWAPPINESS`, `$VFS_PRESSURE` et `$f` **ne sont pas exportées** → elles deviennent vides.
Remplace la ligne par une version où *le parent* fait l’expansion :

```bash
run "printf '%s\n%s\n' 'vm.swappiness=$SWAPPINESS' 'vm.vfs_cache_pressure=$VFS_PRESSURE' > '$f'"
```

### 2) `setup_zram()` — même problème pour `$cfg` et `$ZRAM_PERCENT`

Ton heredoc est évalué dans le sous-shell : `$cfg` n’existe pas là-bas. Fais comme ci-dessous :

```bash
run "printf '%s\n%s\n%s\n' '[zram0]' 'zram-size = ram/${ZRAM_PERCENT}' 'compression-algorithm = zstd' > '$cfg'"
run "systemctl daemon-reload"
run "systemctl enable --now dev-zram0.swap || systemctl restart systemd-zram-setup@zram0.service || true"
```

### 3) Ordre d’écriture `/etc/fstab`

En cas d’échec pendant la création, tu auras déjà modifié `fstab`.
**Déplace `update_fstab` après** `resize_or_create_swapfile` et juste avant `swapon` (ou après, peu importe, mais après la création réussie).

### 4) Micro-nits

* Dans `create_swapfile_ext()`, `fallocate -l` sur fichier existant suffit, ok. Ajoute un `sync` facultatif si tu veux être ultra-prudent avant `mkswap` (pas obligatoire).
* Pour Btrfs très strict : si dispo, préfère `btrfs filesystem mkswapfile -s "$size_str" "$path"` (mais garde ton fallback `dd`).

Si tu appliques 1) et 2) (et idéalement 3)), **oui : ton script est propre et “safe”** pour un usage root automatisé. Tu veux que je te renvoie le bloc complet corrigé ?
