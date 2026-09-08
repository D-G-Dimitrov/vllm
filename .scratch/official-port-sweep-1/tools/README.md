# tools/

Scripts the port grind runs. They used to live in /tmp (lost on reboot); this is the durable copy.

    ./tools/fast.sh <up-sha10> [title] [@notefile]   # default per-item pipeline (pick->gates->land->ledger->sync)
    ./tools/audit.sh                                # counts + next actionable in file order

Land/tick take shas only. land.sh fetches from jetson-222 and pushes origin; run from the vllm-mitaka clone.
