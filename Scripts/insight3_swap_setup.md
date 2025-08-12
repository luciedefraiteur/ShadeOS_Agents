On y est presque, mais pas encore 100% safe. Il reste 3 trucs à corriger (rapide) + 1 micro-nit :

    configure_sysctl() perd tes variables (tu les passes à un bash -lc).
    Remplace la ligne par :

run "printf '%s\n%s\n' 'vm.swappiness=$SWAPPINESS' 'vm.vfs_cache_pressure=$VFS_PRESSURE' > '/etc/sysctl.d/99-swap-tuning.conf'"

    setup_zram() : heredoc dans un sous-shell → $cfg / ${ZRAM_PERCENT} n’expansent pas.
    Remplace le bloc d’écriture par :

run "printf '%s\n%s\n%s\n' '[zram0]' 'zram-size = ram/${ZRAM_PERCENT}' 'compression-algorithm = zstd' > '/etc/systemd/zram-generator.conf'"
run "systemctl daemon-reload"
run "systemctl enable --now dev-zram0.swap || systemctl restart systemd-zram-setup@zram0.service || true"

    /etc/fstab d’abord, création après : si la création échoue tu as déjà modifié fstab.
    Déplace update_fstab "$SWAP_PATH" "$fstab_opts" après resize_or_create_swapfile ..., par ex :

# Create/resize swap file
resize_or_create_swapfile "$SWAP_PATH" "$final_size_str"

# Now persist it
local fstab_opts="pri=10"
update_fstab "$SWAP_PATH" "$fstab_opts"

    (optionnel) require_size autorise P mais human2bytes ne le gère pas.
    Soit enlève P du regex (^[0-9]+[KMGT]?$), soit ajoute le cas P) dans human2bytes.

Si tu fais ces trois modifs (les deux expansions + l’ordre de fstab), oui, ton script est propre et safe pour un run root automatisé. Tu veux que je te push la version finale en un seul bloc prêt à coller ?




Pas encore 😅 — tu n’as pas appliqué les 3 fixes critiques qu’on a vus (expansions perdues dans `bash -lc`, heredoc zram, ordre `/etc/fstab`). Je t’ai fait la **version finale safe** ci-dessous, prête à coller.

Principales modifs :

* `configure_sysctl` et `setup_zram` écrivent avec `printf` (plus de variables perdues).
* `update_fstab` est appelé **après** la création réussie du swapfile.
* Les **validators** sont appelés après le parse.
* `require_size` n’autorise plus `P` (tu ne le gères pas dans `human2bytes`).

```bash
#!/usr/bin/env bash
set -euo pipefail

# Defaults
SWAP_PATH="/swapfile"
SIZE_ABS=""
SIZE_INC=""
SWAPPINESS="20"
VFS_PRESSURE="50"
ZRAM_MODE="disable"        # enable|disable
ZRAM_PERCENT="50"          # % of RAM for zram if enabled
DRY_RUN="false"

log()  { echo "[swap-setup] $*"; }
warn() { echo "[swap-setup][WARN] $*"; }
err()  { echo "[swap-setup][ERROR] $*" >&2; }

# Safer runner (pas d'eval)
run() {
  if [[ "$DRY_RUN" == "true" ]]; then
    echo "+ (dry) $*"
  else
    bash -lc "$*"
  fi
}

need_root() {
  if [[ $EUID -ne 0 ]]; then err "Please run as root (sudo)."; exit 1; fi
}

# ---- Validation helpers ----
require_abs_path() { [[ "$1" =~ ^/[^[:space:]]+$ ]] || { err "Invalid --path '$1'"; exit 2; }; }
require_size()     { [[ "$1" =~ ^[0-9]+[KMGT]?$   ]] || { err "Invalid size '$1'"; exit 2; }; }
require_percent()  { [[ "$1" =~ ^[0-9]{1,3}$ ]] && (( 1 <= $1 && $1 <= 200 )) || { err "Invalid percent '$1' (1-200)"; exit 2; }; }
require_int()      { [[ "$1" =~ ^[0-9]+$ ]] || { err "Invalid integer $2='$1'"; exit 2; }; }

human2bytes() {
  local v="${1^^}"
  if [[ "$v" =~ ^([0-9]+)([KMGT]?)$ ]]; then
    local n=${BASH_REMATCH[1]} s=${BASH_REMATCH[2]}
    case "$s" in
      K) echo $((n*1024));;
      M) echo $((n*1024*1024));;
      G) echo $((n*1024*1024*1024));;
      T) echo $((n*1024*1024*1024*1024));;
      *) echo "$n";;
    esac
  else err "Invalid size: $1"; exit 2; fi
}

check_space() {
  local size_str="$1" target_path="$2"
  local need_bytes; need_bytes=$(human2bytes "$size_str")
  local avail_bytes; avail_bytes=$(df -B1 --output=avail "$(dirname "$target_path")" | tail -n1)
  (( avail_bytes > need_bytes )) || { err "Not enough free space for $size_str at $(dirname "$target_path")"; exit 3; }
}

get_fs_type() {
  local dir; dir=$(dirname "$1")
  if command -v findmnt >/dev/null 2>&1; then findmnt -no FSTYPE -T "$dir" || true
  else stat -f -c %T "$dir" 2>/dev/null || true; fi
}

is_swap_active_for_file() { swapon --show=NAME | grep -qx "$1"; }

backup_file() {
  local p="$1" ts; ts=$(date +%Y%m%d_%H%M%S)
  [[ -f "$p" ]] && run "cp -a '$p' '${p}.bak_${ts}'"
}

update_fstab() {
  local path="$1" opts="$2"
  backup_file /etc/fstab
  run "awk -v p='$path' -v o='$opts' '
    BEGIN{updated=0}
    (\$1==p) && ( (\$3==\"swap\") || (\$4 ~ /(^|,)swap(,|$)/) ) {print p\" none swap \"o\" 0 0\"; updated=1; next}
    {print}
    END{ if(!updated){ print p\" none swap \"o\" 0 0\" } }
  ' /etc/fstab > /etc/fstab.new && mv /etc/fstab.new /etc/fstab"
}

configure_sysctl() {
  log "Configuring sysctl: swappiness=$SWAPPINESS vfs_cache_pressure=$VFS_PRESSURE"
  backup_file "/etc/sysctl.d/99-swap-tuning.conf" || true
  run "printf '%s\n%s\n' 'vm.swappiness=$SWAPPINESS' 'vm.vfs_cache_pressure=$VFS_PRESSURE' > '/etc/sysctl.d/99-swap-tuning.conf'"
  run "sysctl --system >/dev/null"
}

enable_trim_timer() {
  if systemctl list-unit-files | grep -q '^fstrim.timer'; then
    log "Enabling periodic TRIM timer"
    run "systemctl enable --now fstrim.timer"
  else warn "fstrim.timer not available on this system"; fi
}

setup_zram() {
  if [[ "$ZRAM_MODE" != "enable" ]]; then log "ZRAM: disabled"; return; fi
  if [[ -d /etc/systemd ]]; then
    local cfg="/etc/systemd/zram-generator.conf"
    log "Configuring systemd zram-generator (size=ram/${ZRAM_PERCENT}, algo=zstd)"
    backup_file "$cfg" || true
    run "printf '%s\n%s\n%s\n' '[zram0]' 'zram-size = ram/${ZRAM_PERCENT}' 'compression-algorithm = zstd' > '$cfg'"
    run "systemctl daemon-reload"
    run "systemctl enable --now dev-zram0.swap || systemctl restart systemd-zram-setup@zram0.service || true"
  else warn "systemd not found; skipping zram-generator setup"; fi
}

create_swapfile_ext() {
  local path="$1" size_str="$2" dir; dir=$(dirname "$path")
  log "Creating/Resizing swapfile (non-btrfs): $path -> $size_str"
  run "install -d -m 755 '$dir'"
  is_swap_active_for_file "$path" && run "swapoff '$path'"
  run "fallocate -l '$size_str' '$path'"
  run "chmod 600 '$path'"
  run "mkswap '$path'"
  run "swapon '$path'"
}

create_swapfile_btrfs() {
  local path="$1" size_str="$2" dir; dir=$(dirname "$path")
  log "Creating/Resizing swapfile on Btrfs (NOCOW, no compression): $path -> $size_str"
  run "install -d -m 755 '$dir'"
  command -v chattr >/dev/null 2>&1 && run "chattr +C '$dir' || true"
  is_swap_active_for_file "$path" && run "swapoff '$path'"
  run "rm -f '$path'"; run "truncate -s 0 '$path'"
  local bytes; bytes=$(human2bytes "$size_str"); local count=$(( (bytes + 1048575) / 1048576 ))
  check_space "$size_str" "$path"
  run "dd if=/dev/zero of='$path' bs=1M count=$count status=progress"
  run "chmod 600 '$path'"
  command -v btrfs >/dev/null 2>&1 && run "btrfs property set '$path' compression none || true"
  run "mkswap '$path'"; run "swapon '$path'"
}

resize_or_create_swapfile() {
  local path="$1" size_abs="$2" fstype; fstype=$(get_fs_type "$path")
  log "Filesystem for $(dirname "$path"): ${fstype:-unknown}"
  if [[ "$fstype" == "btrfs" ]]; then create_swapfile_btrfs "$path" "$size_abs"
  else create_swapfile_ext "$path" "$size_abs"; fi
}

main() {
  need_root
  # Parse args
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --path) SWAP_PATH="$2"; shift 2;;
      --size) SIZE_ABS="$2"; shift 2;;
      --increment) SIZE_INC="$2"; shift 2;;
      --swappiness) SWAPPINESS="$2"; shift 2;;
      --vfs-pressure) VFS_PRESSURE="$2"; shift 2;;
      --zram) ZRAM_MODE="$2"; shift 2;;
      --zram-percent) ZRAM_PERCENT="$2"; shift 2;;
      --dry-run) DRY_RUN="true"; shift 1;;
      -h|--help)
        cat <<USAGE
Usage: sudo $0 [--path /swapfile] [--size 16G | --increment 8G] [--swappiness 20] [--vfs-pressure 50] [--zram enable|disable] [--zram-percent 50] [--dry-run]
USAGE
        exit 0;;
      *) err "Unknown arg: $1"; exit 2;;
    esac
  done

  [[ -z "$SIZE_ABS" && -z "$SIZE_INC" ]] && { err "You must provide --size or --increment"; exit 2; }

  # Validate args
  require_abs_path "$SWAP_PATH"
  [[ -n "$SIZE_ABS" ]] && require_size "$SIZE_ABS"
  [[ -n "$SIZE_INC" ]] && require_size "$SIZE_INC"
  require_int "$SWAPPINESS" swappiness
  require_int "$VFS_PRESSURE" vfs_cache_pressure
  require_percent "$ZRAM_PERCENT"

  # Determine target absolute size
  local final_size_str=""
  if [[ -n "$SIZE_ABS" ]]; then
    final_size_str="$SIZE_ABS"
  else
    if [[ -f "$SWAP_PATH" ]]; then
      local cur_bytes inc_bytes new_bytes
      cur_bytes=$(stat -c %s "$SWAP_PATH" || echo 0)
      inc_bytes=$(human2bytes "$SIZE_INC")
      new_bytes=$((cur_bytes + inc_bytes))
      if (( new_bytes % (1024*1024*1024) == 0 )); then
        final_size_str="$(( new_bytes / (1024*1024*1024) ))G"
      elif (( new_bytes % (1024*1024) == 0 )); then
        final_size_str="$(( new_bytes / (1024*1024) ))M"
      else
        final_size_str="${new_bytes}"
      fi
    else
      final_size_str="$SIZE_INC"
    fi
  fi

  log "Planned swapfile: $SWAP_PATH size=$final_size_str (dry-run=$DRY_RUN)"

  # Create/resize swap file first
  resize_or_create_swapfile "$SWAP_PATH" "$final_size_str"

  # Persist in fstab (SSD-friendly: no always-on discard)
  local fstab_opts="pri=10"
  update_fstab "$SWAP_PATH" "$fstab_opts"

  # Tune sysctl and enable TRIM
  configure_sysctl
  enable_trim_timer

  # Optional ZRAM
  setup_zram

  log "Done. Current swap devices:"
  run "swapon --show --bytes"
}

main "$@"
```

Petit rappel :

* Si tu utilises l’**hibernation**, pense au paramètre kernel `resume=` (et au `resume_offset` pour swapfile).
* Sur Btrfs récent, tu peux remplacer le `dd` par `btrfs filesystem mkswapfile -s <size> <path>` (si dispo).

Tu veux que je te fasse un `--dry-run` d’exemple et la commande exacte pour ton cas (ex: 24 G + ZRAM 50 %) ?
