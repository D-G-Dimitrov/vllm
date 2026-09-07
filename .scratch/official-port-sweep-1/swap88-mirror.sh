#!/usr/bin/env bash
# Mirror the in-flight item-88 swap resolution off its single-copy location.
#
# WHY: the 42 resolved paths of swap/qwen-88 exist ONLY as a git index + working
# tree inside jetson-222:~/dev/vllm-swap88. They cannot be committed yet (files are
# still unmerged), so they cannot go to origin as a branch. This script snapshots
# them -- working-tree content, every unmerged index stage, and the worktree's gitdir
# metadata -- into the mitaka/backport-ledger branch (already durable on origin) and
# back to jetson as part of the scratch tarball. Two extra copies, one of them remote.
#
# Usage: .scratch/official-port-sweep-1/swap88-mirror.sh ["commit message"]
# Safe to re-run. Never touches the swap worktree's content (read-only on jetson).
set -euo pipefail

HOST=${SWAP_HOST:-jetson-222}
REMOTE_DIR=${SWAP_REMOTE_DIR:-dev/vllm-swap88}
MAC_REPO=${MAC_REPO:-/Users/mitaka/Projects/PyCharm/vllm-mitaka}
LEDGER="$MAC_REPO/.scratch/official-port-sweep-1/swap88-mirror"
MSG=${1:-"ledger: swap88 mirror"}
TAR=swap88-state.tar.gz

mkdir -p "$LEDGER"

echo "swap88-mirror: snapshotting $HOST:~/$REMOTE_DIR"
ssh -o ConnectTimeout=25 "$HOST" "bash -s" "$REMOTE_DIR" <<'REMOTE' > /tmp/swap88-mirror.report
set -eu
cd ~/"$1" || { echo "MISSING worktree ~/$1"; exit 1; }
WT=$(pwd); ST=/tmp/swap88-stage; rm -rf "$ST" /tmp/swap88-state.tar.gz; mkdir -p "$ST/meta" "$ST/worktree" "$ST/stages" "$ST/gitdir"

HEAD_SHA=$(git rev-parse HEAD)
BASE=$(git rev-parse HEAD)
git status --porcelain > "$ST/meta/status_porcelain.txt"
git rev-parse --abbrev-ref HEAD > "$ST/meta/branch.txt"
echo "$HEAD_SHA" > "$ST/meta/head.txt"
git rev-parse --git-dir > "$ST/meta/gitdir_path.txt"
GD=$(git rev-parse --git-dir)

# tracked-dirty = staged vs HEAD, unstaged vs index, and unmerged. Union, sorted, unique.
{ git diff --cached --name-only HEAD || true
  git diff --name-only || true
  git ls-files -u | awk '{print $4}' || true; } | sort -u \
  | grep -vE '\.so$|\.so\.|__pycache__|^\.' > "$ST/meta/dirty_paths.txt" || true

N=0
while IFS= read -r f; do
  [ -n "$f" ] || continue
  if [ -f "$f" ]; then
    mkdir -p "$ST/worktree/$(dirname "$f")"
    cp -p "$f" "$ST/worktree/$f"; N=$((N+1))
  else
    echo "DELETED_IN_WORKTREE: $f" >> "$ST/meta/deleted_paths.txt"
  fi
done < "$ST/meta/dirty_paths.txt"
echo "$N" > "$ST/meta/worktree_file_count.txt"

# Every index stage for every unmerged path: :1 base, :2 ours, :3 theirs.
git ls-files -u | awk '{print $2" "$3" "$4}' | while read -r sha stage path; do
  [ -n "$path" ] || continue
  safe=$(printf '%s' "$path" | tr '/' '%')
  git show ":$stage:$path" > "$ST/stages/$safe.stage$stage" 2>/dev/null || echo "STAGE_FAIL $stage $path" >> "$ST/meta/stage_failures.txt"
done
git ls-files -u | sed 's/^/    /' > "$ST/meta/unmerged_stages.txt"
[ -f "$GD/MERGE_MSG" ] && cp "$GD/MERGE_MSG" "$ST/meta/MERGE_MSG" || true
[ -f "$GD/CHERRY_PICK_HEAD" ] && git show CHERRY_PICK_HEAD --no-patch --format='%H %s' > "$ST/meta/CHERRY_PICK_HEAD.txt" || true
git log -1 --format='%H %s' "$HEAD_SHA" > "$ST/meta/head_subject.txt"

# The worktree's own gitdir metadata (index carries the conflict stages for exact restore).
cp -p "$GD/index" "$ST/gitdir/index" 2>/dev/null || echo "no index copied" > "$ST/gitdir/INDEX_MISSING"
for m in HEAD MERGE_MSG ORIG_HEAD commondir gitdir; do [ -e "$GD/$m" ] && cp -p "$GD/$m" "$ST/gitdir/$m" 2>/dev/null || true; done

cat > "$ST/RESTORE.md" <<'DOC'
# Restoring this snapshot

Contents: `worktree/` (working-tree bytes of every tracked-dirty path), `stages/`
(every unmerged index stage, `%`-escaped path + `.stage1|2|3`), `gitdir/` (the
worktree's own `index`, `HEAD`, `MERGE_MSG`), `meta/` (status, path lists, head).

Preferred restore is always the real branch (`git clone`/`fetch` `swap/qwen-88` once
it has a commit). This snapshot is for the pre-commit window only.

On the host that has the objects (`e16d574bb` + official `e126687a9a`):

    git worktree add ~/dev/vllm-swap88 -b swap/qwen-88 <head.txt sha>   # or reuse it
    tar xzf swap88-state.tar.gz -C /tmp/r
    # 1. recreate the unmerged index exactly (base, ours, theirs).
    #    meta/unmerged_stages.txt lines are: '    <mode> <sha> <stage>\t<path>'
    sed 's/^ *//' /tmp/r/meta/unmerged_stages.txt | while read -r mode sha stage path; do
      g=$(git hash-object -w "/tmp/r/stages/$(printf '%s' "$path" | tr '/' '%').stage$stage")
      git update-index --cacheinfo "$mode,$g,$path"
    done
    # 2. working-tree bytes
    ( cd /tmp/r/worktree && find . -type f -print0 | while IFS= read -r -d '' f; do
        mkdir -p ~/dev/vllm-swap88/$(dirname "$f"); cp "$f" ~/dev/vllm-swap88/"$f"; done )
    # 3. copy the 8 .so from ~/dev/vllm-so-d4d703c.tgz (excluded from this snapshot)
    cp /tmp/r/gitdir/index ~/dev/vllm-swap88/$(cd ~/dev/vllm-swap88 && git rev-parse --git-dir)/index

Verify after restore: `git status --porcelain` must equal `meta/status_porcelain.txt`,
and `md5 -q` of a sample of `worktree/` files must match the restored files.
DOC

tar czf /tmp/swap88-state.tar.gz -C "$ST" .
echo "head=$(cat "$ST/meta/head.txt")"
echo "dirty_paths=$(wc -l < "$ST/meta/dirty_paths.txt")"
echo "worktree_files=$(cat "$ST/meta/worktree_file_count.txt")"
echo "unmerged_paths=$(git ls-files -u | awk '{print $4}' | sort -u | wc -l)"
echo "stage_blobs=$(ls "$ST/stages" | wc -l)"
echo "deleted_in_worktree=$(wc -l < "${ST}/meta/deleted_paths.txt" 2>/dev/null || echo 0)"
echo "size_bytes=$(wc -c < /tmp/swap88-state.tar.gz)"
echo "sha256=$(shasum -a 256 /tmp/swap88-state.tar.gz | cut -d' ' -f1)"
REMOTE

scp -q "$HOST":/tmp/swap88-state.tar.gz "$LEDGER/$TAR"
LOCAL_SHA=$(shasum -a 256 "$LEDGER/$TAR" | awk '{print $1}')
REMOTE_SHA=$(grep '^sha256=' /tmp/swap88-mirror.report | cut -d= -f2)
[ "$LOCAL_SHA" = "$REMOTE_SHA" ] || { echo "SWAP88-MIRROR: sha mismatch local=$LOCAL_SHA remote=$REMOTE_SHA"; exit 1; }

{ echo "captured_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  grep -E '^(head|dirty_paths|worktree_files|unmerged_paths|stage_blobs|size_bytes|sha256)=' /tmp/swap88-mirror.report
  echo "sha256_verified=local==remote"
  echo "note=re-run of swap88-mirror.sh; the swap worktree is mid-cherry-pick (-n) and uncommittable until the last conflict resolves"
} > "$LEDGER/LATEST.txt"

echo "swap88-mirror: sha verified $LOCAL_SHA -> committing to ledger"
"$MAC_REPO/.scratch/official-port-sweep-1/ledger-sync.sh" "$MSG"

LTX=/Users/mitaka/Projects/PyCharm/vllm-ledger
LT=$(git -C "$LTX" rev-parse "HEAD:official-port-sweep-1/swap88-mirror/$TAR" 2>/dev/null | cut -c1-9 || true)
IN_TAR_SHA=$(git -C "$LTX" show "HEAD:official-port-sweep-1/swap88-mirror/$TAR" 2>/dev/null | shasum -a 256 | awk '{print $1}')
echo "swap88-mirror: blob_in_ledger_commit=$LT tar_sha_in_commit=${IN_TAR_SHA:0:12}"
[ "$IN_TAR_SHA" = "$REMOTE_SHA" ] && echo "swap88-mirror: OK (origin + jetson scratch tarball both carry it)" \
  || { echo "swap88-mirror: ASSERT FAIL (tarball in ledger != snapshot just taken; a concurrent change happened?)"; exit 1; }
