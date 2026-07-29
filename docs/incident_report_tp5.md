# Incident Report — SSH port unreachable on srv-tp-01

**Service:** TCP-SSH (`10.31.10.41:22`)  
**Environment:** Lab / TP Monitoring  
**Date:** 2026-07-29  
**Author:** On-call (TP5 simulation)  
**Status:** Resolved

---

## Incident summary

On 2026-07-29, external monitoring (Uptime Kuma) detected that the SSH service on host `10.31.10.41` became unreachable. The outage was caused by a temporary firewall rule (`iptables` DROP on TCP/22) applied during a controlled availability test. The public HTTP service and gateway ping checks were not affected. The rule was removed and SSH connectivity was restored within a few minutes.

---

## Severity and impact

| Item | Detail |
|------|--------|
| **Severity** | Medium (lab) / would be High in production if remote admin access is required |
| **Affected service** | SSH (TCP port 22) |
| **Unaffected** | HTTP-Apache (port 80), Ping-Gateway |
| **Users / operators** | Remote SSH access blocked for ~4 minutes |
| **Duration** | ≈ 08:33–08:37 UTC (~4 minutes) |

---

## Timeline (UTC)

| Time (UTC) | Status | Event |
|------------|--------|-------|
| 08:33 | Detected | Uptime Kuma alert fired: SSH port unreachable on `10.31.10.41:22` (`Request timeout`). Discord notification sent. |
| 08:33 | Acknowledged | On-call engineer received Discord alert and correlated with the ongoing firewall test. |
| 08:36 | Mitigated | Offending `iptables` INPUT DROP rule on TCP/22 identified and removed. |
| 08:37 | Resolved | Uptime Kuma monitor TCP-SSH returned to **Up**; status page updated with a resolved incident note. |

*Local reference (Europe/Paris, UTC+2): detection ≈ 10:33, recovery ≈ 10:37.*

---

## Root cause analysis

A host firewall rule was intentionally added to simulate an outage:

```bash
sudo iptables -A INPUT -p tcp --dport 22 -j DROP
```

This dropped inbound SSH traffic, so TCP probes from Uptime Kuma timed out. The root cause is therefore an **operator-applied packet filter**, not an application crash or network path failure.

---

## Resolution steps taken

1. Confirmed Discord / Uptime Kuma alert for TCP-SSH Down.
2. Verified HTTP and ping monitors still Up (blast radius limited to SSH).
3. Removed the DROP rule:

```bash
sudo iptables -D INPUT -p tcp --dport 22 -j DROP
```

4. Waited for the next successful check; monitor returned **En ligne**.
5. Published a resolved incident message on the public status page.

---

## Action items / preventive measures

| Action | Owner | Due |
|--------|-------|-----|
| Document firewall change procedure (console/VNC required before blocking SSH) | Ops / student | 2026-08-05 |
| Prefer maintenance windows + Status Page “Maintenance” mode for planned tests | Ops | 2026-08-05 |
| Keep Discord notification linked to all critical external monitors | Ops | Done (TP5) |
| Review accidental leftover `iptables` rules after drills (`iptables -L -n`) | On-call | After each drill |

---

## References

- Uptime Kuma dashboard / TCP-SSH monitor history
- Discord downtime notification (TP5)
- Public status page « Statut des services »
