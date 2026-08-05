# VLLM Backport

A VLLM fork that focuses on running Deepseek V4 Flash 0731 on Ampere at this moment.

Currently achieving 1783 tps prefill and 355 tps decoding on 8xA6000 and this should also work on A100.

## Docker Usage

Prebuilt images are published to Docker Hub on every push:

| Image | Target GPUs |
| --- | --- |
| `lazymio/vllm-backport:latest-sm86` (also `:latest`) | Ampere sm86 (A6000, RTX 30xx) |
| `lazymio/vllm-backport:latest-sm80` | Ampere sm80 (A100) |

Images are single-arch builds (no FA3/Hopper kernels), so pick the tag matching your GPU. The entrypoint is `vllm serve`.

### Docker Compose

```yaml
services:
  vllm:
    image: lazymio/vllm-backport:latest-sm86  # A100: use :latest-sm80
    command: >
      deepseek-ai/DeepSeek-V4-Flash-0731
      --tensor-parallel-size 8
    ports:
      - "8000:8000"
    volumes:
      - ~/.cache/huggingface:/root/.cache/huggingface
    environment:
      - HUGGING_FACE_HUB_TOKEN=${HUGGING_FACE_HUB_TOKEN:-}
    ipc: host
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

Then:

```bash
docker compose up -d
curl http://localhost:8000/v1/models
```

Adjust the model and `--tensor-parallel-size` to your setup; `ipc: host` is required for multi-GPU tensor parallelism.
