#!/usr/bin/env bash
# Safe swap setup/resize helper for Linux (SSD-friendly)
# - Creates or resizes a swapfile on SSD/HDD
# - Handles Btrfs (NOCOW + no compression) correctly
# - Makes changes persistent in /etc/fstab
# - Tunes swappiness and vfs_cache_pressure
# - Optionally configures ZRAM (compressed swap in RAM)
#
# USAGE EXAMPLES
#   sudo bash Scripts/swap_setup.sh --size 16G                       # create/resize /swapfile to 16G
#   sudo bash Scripts/swap_setup.sh --increment 8G                   # add +8G to current /swapfile
#   sudo bash Scripts/swap_setup.sh --path /var/swap/swapfile --size 24G
#   sudo bash Scripts/swap_setup.sh --size 16G --zram enable --zram-percent 50
#   sudo bash Scripts/swap_setup.sh --dry-run --size 16G             # preview changes only
#
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

log() { echo "[swap-setup] $*"; }
warn() { echo "[swap-setup][WARN] $*"; }
err() { echo "[swap-setup][ERROR] $*" >&2; }
# Safer command runner: avoid eval; execute via bash -lc
run() {
  if [[ "$DRY_RUN" == "true" ]]; then
    echo "+ (dry) $*"
  else
    bash -lc "$*"
  fi
}

need_root() {
  if [[ $EUID -ne 0 ]]; then
    err "Please run as root (sudo)."
    exit 1
  fi
}

# ---- Arguments validation helpers ----
require_abs_path() {
  [[ "$1" =~ ^/[^[:space:]]+$ ]] || { err "Invalid --path '$1' (must be absolute, no spaces)"; exit 2; }
}
require_size() {
  [[ "$1" =~ ^[0-9]+[KMGTP]?$ ]] || { err "Invalid size '$1'"; exit 2; }
}
require_percent() {
  [[ "$1" =~ ^[0-9]{1,3}$ ]] && (( 1 <= $1 && $1 <= 200 )) || { err "Invalid percent '$1' (1-200)"; exit 2; }
}
require_int() {
  local val="$1"; local name="$2"
  [[ "$val" =~ ^[0-9]+$ ]] || { err "Invalid integer $name='$val'"; exit 2; }
}

human2bytes() {
  # supports K/M/G/T suffixes (binary 1024)
  local v="$1"; v=${v^^}
  if [[ "$v" =~ ^([0-9]+)([KMGT]?)$ ]]; then
    local n=${BASH_REMATCH[1]}
    local s=${BASH_REMATCH[2]}
    case "$s" in
      K) echo $((n*1024));;
      M) echo $((n*1024*1024));;
      G) echo $((n*1024*1024*1024));;
      T) echo $((n*1024*1024*1024*1024));;
      *) echo "$n";;
    esac
  else
    err "Invalid size: $1"; exit 2
  fi
}

# Check there is enough free space before allocating a file
check_space() {
  local size_str="$1"; local target_path="$2"
  local need_bytes; need_bytes=$(human2bytes "$size_str")
  local avail_bytes
  avail_bytes=$(df -B1 --output=avail "$(dirname "$target_path")" | tail -n1)
  (( avail_bytes > need_bytes )) || { err "Not enough free space for $size_str at $(dirname "$target_path")"; exit 3; }
}

get_fs_type() {
  local path="$1"
  # resolve to directory (parent of file)
  local dir; dir=$(dirname "$path")
  # use findmnt if available for reliable FS type
  if command -v findmnt >/dev/null 2>&1; then
    findmnt -no FSTYPE -T "$dir" || true
  else
    stat -f -c %T "$dir" 2>/dev/null || true
  fi
}

is_swap_active_for_file() {
  local path="$1"
  swapon --show=NAME | grep -qx "$path"
}

backup_file() {
  local p="$1"
  local ts; ts=$(date +%Y%m%d_%H%M%S)
  if [[ -f "$p" ]]; then
    run "cp -a '$p' '${p}.bak_${ts}'"
  fi
}

update_fstab() {
  local path="$1" opts="$2"
  backup_file /etc/fstab
  # Rewrite atomically using awk: update matching line or append if missing
  run "awk -v p='$path' -v o='$opts' 'BEGIN{updated=0} $1==p && $3==\"swap\" {print p\" none swap \"o\" 0 0\"; updated=1; next} {print} END{ if(!updated){ print p\" none swap \"o\" 0 0\" } }' /etc/fstab > /etc/fstab.new && mv /etc/fstab.new /etc/fstab"
}

configure_sysctl() {
  local f="/etc/sysctl.d/99-swap-tuning.conf"
  log "Configuring sysctl: swappiness=$SWAPPINESS vfs_cache_pressure=$VFS_PRESSURE"
  backup_file "$f" || true
  run "bash -lc 'printf "vm.swappiness=%s\nvm.vfs_cache_pressure=%s\n" "$SWAPPINESS" "$VFS_PRESSURE" > "$f"'"
  run "sysctl --system >/dev/null"
}

enable_trim_timer() {
  if systemctl list-unit-files | grep -q '^fstrim.timer'; then
    log "Enabling periodic TRIM timer"
    run "systemctl enable --now fstrim.timer"
  else
    warn "fstrim.timer not available on this system"
  fi
}

setup_zram() {
  if [[ "$ZRAM_MODE" != "enable" ]]; then
    log "ZRAM: disabled (use --zram enable to turn on)"
    return
  fi
  if [[ -d /etc/systemd ]]; then
    local cfg="/etc/systemd/zram-generator.conf"
    log "Configuring systemd zram-generator (size=ram/${ZRAM_PERCENT}, algo=zstd)"
    backup_file "$cfg" || true
    run "bash -lc 'cat > "$cfg" <<EOC
[zram0]
zram-size = ram/${ZRAM_PERCENT}
compression-algorithm = zstd
EOC'"
    run "systemctl daemon-reload"
    # Prefer enabling the generated swap unit; fall back to legacy service name
    run "systemctl enable --now dev-zram0.swap || systemctl restart systemd-zram-setup@zram0.service || true"
  else
    warn "systemd not found; skipping zram-generator setup"
  fi
}

create_swapfile_ext() {
  local path="$1" size_str="$2"
  log "Creating/Resizing swapfile on non-btrfs using fallocate: $path -> $size_str"
  # Ensure parent dir exists
  run "install -d -m 755 '$(dirname "$path")'"
  if is_swap_active_for_file "$path"; then run "swapoff '$path'"; fi
  if [[ ! -f "$path" ]]; then
    run "fallocate -l '$size_str' '$path'"
  else
    run "fallocate -l '$size_str' '$path'"
  fi
  run "chmod 600 '$path'"
  run "mkswap '$path'"
  run "swapon '$path'"
}

create_swapfile_btrfs() {
  local path="$1" size_str="$2"
  log "Creating/Resizing swapfile on Btrfs (NOCOW, no compression): $path -> $size_str"
  local dir; dir=$(dirname "$path")
  run "install -d -m 755 '$dir'"
  # Set NOCOW on directory to ensure new file inherits (most reliable)
  if command -v chattr >/dev/null 2>&1; then
    run "chattr +C '$dir' || true"
  fi
  # Ensure no compression property on the swap file (applied after creation too)
  if is_swap_active_for_file "$path"; then run "swapoff '$path'"; fi
  # Recreate file to be safe
  run "rm -f '$path'"
  run "truncate -s 0 '$path'"
  # For btrfs, use dd (not fallocate), pre-allocate fully
  local count
  # Convert to bytes then to MiB chunks for progress
  local bytes; bytes=$(human2bytes "$size_str")
  count=$(( (bytes + 1048575) / 1048576 ))
  check_space "$size_str" "$path"
  run "dd if=/dev/zero of='$path' bs=1M count=$count status=progress"
  run "chmod 600 '$path'"
  # Disable compression explicitly
  if command -v btrfs >/dev/null 2>&1; then
    run "btrfs property set '$path' compression none || true"
  fi
  run "mkswap '$path'"
  run "swapon '$path'"
}

resize_or_create_swapfile() {
  local path="$1" size_abs="$2"
  local fstype; fstype=$(get_fs_type "$path")
  log "Filesystem for $(dirname "$path"): ${fstype:-unknown}"
  if [[ "$fstype" == "btrfs" ]]; then
    create_swapfile_btrfs "$path" "$size_abs"
  else
    create_swapfile_ext "$path" "$size_abs"
  fi
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

  if [[ -z "$SIZE_ABS" && -z "$SIZE_INC" ]]; then
    err "You must provide --size or --increment"
    exit 2
  fi

  # Determine target absolute size
  local final_size_str=""
  if [[ -n "$SIZE_ABS" ]]; then
    final_size_str="$SIZE_ABS"
  else
    # increment from current (if file exists) else treat as absolute
    if [[ -f "$SWAP_PATH" ]]; then
      local cur_bytes; cur_bytes=$(stat -c %s "$SWAP_PATH" || echo 0)
      local inc_bytes; inc_bytes=$(human2bytes "$SIZE_INC")
      local new_bytes=$((cur_bytes + inc_bytes))
      # Format back to G if divisible else bytes
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

  # SSD-friendly fstab opts (avoid always-on discard; keep priority only)
  local fstab_opts="pri=10"
  update_fstab "$SWAP_PATH" "$fstab_opts"

  # Create/resize swap file
  resize_or_create_swapfile "$SWAP_PATH" "$final_size_str"

  # Tune sysctl and enable TRIM
  configure_sysctl
  enable_trim_timer

  # Optional ZRAM
  setup_zram

  log "Done. Current swap devices:";
  run "swapon --show --bytes"
}

main "$@"
