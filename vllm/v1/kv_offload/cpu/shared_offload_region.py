# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright contributors to the vLLM project
import fcntl
import json
import mmap
import os
import time

import torch

from vllm.logger import init_logger
from vllm.platforms import current_platform

logger = init_logger(__name__)


def _reclaim_stale_regions(exclude_path: str) -> int:
    """Delete offload region files whose owning engine is gone.

    Every process holds a shared flock on its region file for the file's
    whole lifetime (taken right after open, fd kept open until cleanup),
    and the kernel drops flocks automatically on process death --
    including SIGKILL. A region file we can lock exclusively therefore
    has no live owner. Without this reaper, every fail-fast boot crash
    leaks its region into /dev/shm (engine ids are fresh per boot) until
    the free-space precheck refuses to boot at all, turning a transient
    crash into a permanent crash loop that restart policies cannot heal.

    Files younger than 60s are skipped: a booting sibling engine's
    workers open+lock their creator's file within moments, and the grace
    period keeps the reaper away from that window. Regions created by
    builds that predate flocking are indistinguishable from stale ones;
    they are only safe to reap because deployments stop the old engine
    before starting a new build.
    """
    reclaimed = 0
    try:
        names = os.listdir("/dev/shm")
    except OSError:
        return 0
    for name in names:
        if not (name.startswith("vllm_offload_") and name.endswith(".mmap")):
            continue
        path = os.path.join("/dev/shm", name)
        if path == exclude_path:
            continue
        try:
            if time.time() - os.stat(path).st_mtime < 60.0:
                continue
            fd = os.open(path, os.O_RDWR)
        except OSError:
            continue
        try:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError:
                continue  # lock held -> a live engine owns this region
            for p in (path, path + ".meta"):
                try:
                    os.unlink(p)
                except OSError:
                    pass
            reclaimed += 1
            logger.warning(
                "Reclaimed stale KV offload region %s (no live owner holds "
                "its lock)",
                path,
            )
        finally:
            os.close(fd)
    return reclaimed


def _wait_for_file_size(fd: int, expected_size: int, timeout: float = 30.0) -> None:
    """Spin-wait until the file reaches expected_size (creator truncated it)."""
    deadline = time.monotonic() + timeout
    while True:
        if os.fstat(fd).st_size >= expected_size:
            return
        if time.monotonic() > deadline:
            raise TimeoutError(
                f"Timed out waiting for mmap file to reach {expected_size} bytes"
            )
        time.sleep(0.005)


class SharedOffloadRegion:
    """
    Single mmap-backed memory region shared across all workers for a
    vLLM instance.  Workers coordinate via the filesystem: the first worker
    to open the file with O_EXCL becomes the creator and calls ftruncate;
    the rest open the existing file and wait until it reaches the expected
    size.  Each worker then mmap()s the full file.

    File path: /dev/shm/vllm_offload_{engine_id}.mmap
    """

    BLOCK_SIZE_ALIGNMENT: int = mmap.PAGESIZE

    def __init__(
        self,
        engine_id: str,
        num_blocks: int,
        rank: int | None,
        kv_bytes_per_block: int,
        cpu_page_size: int,
    ) -> None:
        self.page_size = mmap.PAGESIZE
        assert kv_bytes_per_block % self.page_size == 0

        self.num_blocks = num_blocks
        self._row_stride = kv_bytes_per_block
        self.total_size_bytes = self.num_blocks * self._row_stride

        self.mmap_path = f"/dev/shm/vllm_offload_{engine_id}.mmap"
        self._creator = False  # set True only if this worker creates the file
        self.rank = rank
        if rank is not None:
            # byte offset to this worker's first slot within each block row
            self._worker_offset = rank * cpu_page_size
            # exclusive upper bound for this worker's area within each row
            self._worker_area_end = (rank + 1) * cpu_page_size
        try:
            # Exclusive create — only one worker succeeds
            self.fd: int | None = os.open(
                self.mmap_path, os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o600
            )
            # Advertise liveness: hold a shared lock on the region file for
            # as long as this process lives (fd stays open until cleanup).
            # The reaper below only deletes region files nobody holds a
            # lock on, so this is what protects OUR region from a sibling
            # engine's reaper.
            fcntl.flock(self.fd, fcntl.LOCK_SH)
            # Reap regions leaked by dead engines (fail-fast crashes are
            # SIGKILLed and cannot clean up after themselves) BEFORE the
            # free-space check, so a crash loop frees its own garbage and
            # the restart policy can actually self-heal.
            _reclaim_stale_regions(self.mmap_path)
            # Fail fast with an actionable message if /dev/shm cannot hold the
            # region. Otherwise page allocation fails later as an inscrutable
            # EFAULT/SIGBUS. Stale regions from SIGKILLed engines (e.g.
            # docker force-recreate) are the usual culprit.
            vfs = os.statvfs("/dev/shm")
            free = vfs.f_bavail * vfs.f_frsize
            if free < self.total_size_bytes:
                stale = [
                    f
                    for f in os.listdir("/dev/shm")
                    if f.startswith("vllm_offload_") and f != os.path.basename(self.mmap_path)
                ]
                os.close(self.fd)
                os.unlink(self.mmap_path)
                raise RuntimeError(
                    f"/dev/shm has {free / 1e9:.1f} GB free but the KV offload "
                    f"region needs {self.total_size_bytes / 1e9:.1f} GB "
                    "(after reaping stale regions). Other offload regions "
                    f"present: {stale or 'none'} - these are live (lock held) "
                    "or too young to reap. Free /dev/shm space or increase "
                    "its size."
                )
            os.ftruncate(self.fd, self.total_size_bytes)
            # Publish the region geometry so late-joining processes can verify
            # they agree. PP stages computing different geometries used to
            # race on this file: the loser waited forever for a size the
            # winner never set, or worse, mapped overlapping incompatible
            # layouts. Written atomically so openers never see a partial file.
            meta_tmp = self.mmap_path + ".meta.tmp"
            with open(meta_tmp, "w") as f:
                json.dump(
                    {
                        "num_blocks": self.num_blocks,
                        "row_stride": self._row_stride,
                        "total_size_bytes": self.total_size_bytes,
                    },
                    f,
                )
            os.replace(meta_tmp, self.mmap_path + ".meta")
            self._creator = True
            logger.info(
                "Created mmap file %s (%.2f GB)",
                self.mmap_path,
                self.total_size_bytes / 1e9,
            )
        except FileExistsError:
            self.fd = os.open(self.mmap_path, os.O_RDWR)
            # Same liveness lock as the creator: joiners keep the region
            # alive too (the creator process alone may die first).
            fcntl.flock(self.fd, fcntl.LOCK_SH)
            meta_path = self.mmap_path + ".meta"
            deadline = time.monotonic() + 30.0
            while not os.path.exists(meta_path):
                if time.monotonic() > deadline:
                    raise TimeoutError(
                        f"Timed out waiting for {meta_path}; the region "
                        "creator did not publish its geometry."
                    )
                time.sleep(0.05)
            with open(meta_path) as f:
                meta = json.load(f)
            expected = {
                "num_blocks": self.num_blocks,
                "row_stride": self._row_stride,
                "total_size_bytes": self.total_size_bytes,
            }
            if meta != expected:
                raise RuntimeError(
                    "Shared KV offload region geometry mismatch: creator "
                    f"published {meta} but this process computed {expected}. "
                    "All workers and the scheduler must derive one geometry "
                    "(see KVCacheConfig.max_worker_kv_bytes_per_block); with "
                    "pipeline parallelism a per-stage mismatch here would "
                    "silently corrupt offloaded KV."
                )
            _wait_for_file_size(self.fd, self.total_size_bytes)
            logger.info("Opened existing mmap file %s", self.mmap_path)

        self.mmap_obj: mmap.mmap | None = mmap.mmap(
            self.fd,
            self.total_size_bytes,
            flags=mmap.MAP_SHARED,
            prot=mmap.PROT_READ | mmap.PROT_WRITE,
        )

        # Forbid transparent huge pages on this mapping. khugepaged collapses
        # neighbouring 4K pages into 2M pages asynchronously; a huge page
        # spanning two ranks' slot boundaries makes their per-slot
        # cudaHostRegister ranges overlap at the physical-page level, and the
        # cross-process pin/DMA-map churn during early warmup surfaces as a
        # probabilistic async cudaErrorInvalidValue (boot-time crash race).
        _MADV_NOHUGEPAGE = getattr(mmap, "MADV_NOHUGEPAGE", 15)
        try:
            self.mmap_obj.madvise(_MADV_NOHUGEPAGE)
        except OSError:
            logger.warning("MADV_NOHUGEPAGE not supported; leaving THP enabled")

        # MADV_POPULATE_WRITE was added in Linux 5.14 (value 23).
        _MADV_POPULATE_WRITE = getattr(mmap, "MADV_POPULATE_WRITE", 23)
        if rank is not None:
            # Populate only this worker's pages (one slot per block row).
            worker_offset = rank * cpu_page_size
            _t0 = time.perf_counter()
            page_size = self.page_size
            for block in range(num_blocks):
                raw_offset = block * self._row_stride + worker_offset
                aligned_offset = (raw_offset // page_size) * page_size
                end = raw_offset + cpu_page_size
                aligned_length = end - aligned_offset
                self.mmap_obj.madvise(
                    _MADV_POPULATE_WRITE, aligned_offset, aligned_length
                )
            logger.debug(
                "MADV_POPULATE_WRITE loop: %d blocks in %.3f s",
                num_blocks,
                time.perf_counter() - _t0,
            )
        else:
            # No rank — populate the entire shared region in one call.
            _t0 = time.perf_counter()
            self.mmap_obj.madvise(_MADV_POPULATE_WRITE, 0, self.total_size_bytes)
            logger.debug(
                "MADV_POPULATE_WRITE entire region: %.3f s", time.perf_counter() - _t0
            )

        self._base = torch.frombuffer(memoryview(self.mmap_obj), dtype=torch.int8)
        self._views: list[torch.Tensor] = []
        self.is_pinned: bool = False

    def create_next_view(self, tensor_page_size: int) -> torch.Tensor:
        """Allocate a strided int8 view for this worker, one canonical tensor.

        Must be called once per canonical tensor. The full mmap layout is:

            worker0_block0 | worker1_block0 | ... | worker{M-1}_block0
            worker0_block1 | worker1_block1 | ... | worker{M-1}_block1
            ...

        Each worker_block cell is cpu_page_size bytes and holds all canonical
        tensors for that worker and block concatenated:
            [ tensor0_data | tensor1_data | ... | tensor{L-1}_data ]

        Consecutive rows are separated by row_stride = cpu_page_size * M.

        Returns an int8 tensor of shape (num_blocks, tensor_page_size) with stride
        (row_stride, 1).  Using int8 keeps stride == bytes, so swap_blocks
        address arithmetic works without any dtype conversion.

        Args:
            tensor_page_size: Bytes per block for this  tensor.
        """
        assert self.rank is not None
        new_offset = self._worker_offset + tensor_page_size
        assert new_offset <= self._worker_area_end, (
            f"Worker offset {new_offset} exceeds worker area end "
            f"{self._worker_area_end} (overflowed by "
            f"{new_offset - self._worker_area_end} bytes)"
        )
        worker_layer_view = torch.as_strided(
            self._base,
            size=(self.num_blocks, tensor_page_size),
            stride=(self._row_stride, 1),
            storage_offset=self._worker_offset,
        )
        self._worker_offset = new_offset
        self._views.append(worker_layer_view)
        return worker_layer_view

    def create_kv_memoryview(self) -> memoryview:
        """Return a zero-copy memoryview over the entire KV buffer.

        Shape: (num_blocks, row_stride_bytes). Secondary tiers address
        block *b* as ``view[b]``.
        """
        kv_tensor = self._base.view(self.num_blocks, self._row_stride)
        np_arr = kv_tensor.numpy()
        assert np_arr.ctypes.data == self._base.data_ptr(), (
            "view()/numpy() created a copy instead of sharing the mmap buffer; "
            "secondary tiers require zero-copy access to primary KV data"
        )
        return memoryview(np_arr)

    def cleanup(self) -> None:
        # Do NOT cudaHostUnregister here: with per-slot pinning that is tens
        # of thousands of driver calls taking minutes, during which a crashed
        # engine looks hung -- the container never exits, so the docker
        # restart policy cannot self-heal a boot-time failure. The driver
        # releases every pin automatically when the process exits, which is
        # exactly where cleanup() runs.
        if self.is_pinned and self._base is not None:
            self._pinned_slot_offsets = []
            self.is_pinned = False
            self.is_pinned = False
        # Release views before _base: each view holds a _base reference and a
        # direct StorageImpl reference.  Freeing views first lets both refcounts
        # drop so the storage (which holds the mmap_obj buffer export) is freed
        # before mmap_obj.close() is called below.
        if self._views is not None:
            self._views.clear()
        self._base = None
        if self.mmap_obj:
            try:
                self.mmap_obj.close()
            except Exception:
                logger.warning("Failed to close mmap_obj", exc_info=True)
            self.mmap_obj = None
        if self.fd is not None:
            try:
                os.close(self.fd)
            except Exception:
                logger.warning("Failed to close fd %s", self.fd, exc_info=True)
            self.fd = None
        if self._creator and getattr(self, "mmap_path", None):
            try:
                os.unlink(self.mmap_path)
                try:
                    os.unlink(self.mmap_path + ".meta")
                except OSError:
                    pass
                logger.info("Removed mmap file %s", self.mmap_path)
            except Exception:
                logger.warning(
                    "Failed to unlink path %s", self.mmap_path, exc_info=True
                )
            self._creator = False
