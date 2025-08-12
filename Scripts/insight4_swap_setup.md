Yes—facile. Ajoute un *préflight* qui vérifie l’état actuel et s’en sert avant d’agir. Voilà un patch compact à intégrer (ajoute la nouvelle option `--preflight-only` si tu veux juste checker et sortir) :

```bash
# --- en haut, après les defaults ---
PREFLIGHT_ONLY="false"

# --- parse args : ajoute ce case ---
      --preflight-only) PREFLIGHT_ONLY="true"; shift 1;;

# --- ajoute ces fonctions (avant main) ---
inspect_swap_state() {
  SWAP_EXISTS=false
  SWAP_ACTIVE=false
  SWAP_IN_FSTAB=false
  SWAP_SIZE_BYTES=0

  # existe / type sûr ?
  if [[ -e "$SWAP_PATH" ]]; then
    if [[ -d "$SWAP_PATH" ]]; then err "Path '$SWAP_PATH' is a directory"; exit 2; fi
    if [[ -b "$SWAP_PATH" || -c "$SWAP_PATH" ]]; then err "Path '$SWAP_PATH' is a device node"; exit 2; fi
    if [[ -f "$SWAP_PATH" || -L "$SWAP_PATH" ]]; then
      SWAP_EXISTS=true
      SWAP_SIZE_BYTES=$(stat -c %s "$SWAP_PATH" 2>/dev/null || echo 0)
    fi
  fi

  # actif ?
  if swapon --show=NAME --noheadings | grep -qx "$SWAP_PATH"; then
    SWAP_ACTIVE=true
  fi

  # présent dans fstab ?
  if awk -v p="$SWAP_PATH" '($1==p) && ($3=="none") && ($4 ~ /(^|,)swap(,|$)/){found=1} END{exit !found}' /etc/fstab; then
    SWAP_IN_FSTAB=true
  fi

  # autres swaps actifs (info)
  mapfile -t ACTIVE_LIST < <(swapon --show=NAME --noheadings || true)

  log "Preflight: path=$SWAP_PATH exists=$SWAP_EXISTS active=$SWAP_ACTIVE size=${SWAP_SIZE_BYTES}B in_fstab=$SWAP_IN_FSTAB"
  if ((${#ACTIVE_LIST[@]})); then
    log "Active swap devices: ${ACTIVE_LIST[*]}"
  else
    log "Active swap devices: (none)"
  fi
}

# --- dans main(), après la validation des args, AVANT le calcul de final_size_str ---
inspect_swap_state
[[ "$PREFLIGHT_ONLY" == "true" ]] && { log "Preflight only → exiting."; exit 0; }
```

Ce que ça t’apporte :

* Te dit si ton `SWAP_PATH` **existe**, est **actif**, sa **taille**, et s’il est dans **/etc/fstab**.
* Refuse des chemins foireux (répertoire / device node).
* Te liste aussi les **autres** swaps actifs (partitions ou zram) pour visibilité.
* Et comme ton script gère déjà “`--size` = absolu / `--increment` = ajout ou création si absent”, il utilisera directement ces infos pour décider quoi faire.

Tu peux tester juste la vérif :

```bash
sudo bash swap_setup.sh --path /swapfile --preflight-only
```

Puis exécuter pour de vrai.
