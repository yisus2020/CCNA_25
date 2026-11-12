# 01. Network fundamentals: models, media, interfaces and the troubleshooting method

> Document version: 1.0 | Updated: 2026-11-12 | Targets: Cisco IOS XE 17.x; exam blueprint CCNA 200-301

Exam domain 1 (Network Fundamentals). This chapter covers the models, components, cabling, interface/Ethernet behaviour and the generic troubleshooting method. IP addressing is in chapters 02 and 03.

## 1. Reference models

| # | OSI layer | TCP/IP layer | PDU | Examples |
|---|---|---|---|---|
| 7 | Application | Application | data | HTTP, DNS, DHCP, SSH, SNMP |
| 6 | Presentation | Application | data | TLS, JSON, encoding |
| 5 | Session | Application | data | session setup/teardown |
| 4 | Transport | Transport | segment (TCP) / datagram (UDP) | TCP, UDP, ports |
| 3 | Network | Internet | packet | IP, ICMP, routers |
| 2 | Data link | Network access | frame | Ethernet, MAC, switches, VLAN tags |
| 1 | Physical | Network access | bits | cables, signals, hubs |

Encapsulation: data → segment (adds TCP/UDP header) → packet (adds IP header) → frame (adds Ethernet header + FCS trailer) → bits. De-encapsulation is the reverse. Switches look at the frame header, routers at the packet header.

### Common ports and protocols to know
| Port | Protocol | Port | Protocol |
|---|---|---|---|
| 20/21 TCP | FTP data / control | 80 TCP | HTTP |
| 22 TCP | SSH | 443 TCP | HTTPS |
| 23 TCP | Telnet | 110 TCP | POP3 |
| 25 TCP | SMTP | 143 TCP | IMAP |
| 53 UDP/TCP | DNS | 161/162 UDP | SNMP / traps |
| 67/68 UDP | DHCP server / client | 69 UDP | TFTP |
| 123 UDP | NTP | 514 UDP | Syslog |
| 3389 TCP | RDP | 179 TCP | BGP |

### TCP versus UDP
| | TCP | UDP |
|---|---|---|
| Connection | connection-oriented (3-way handshake SYN, SYN-ACK, ACK) | connectionless |
| Reliability | sequence numbers, ACKs, retransmission, flow control (window) | none (application handles it) |
| Overhead | 20-byte header minimum | 8-byte header |
| Used by | web, email, SSH, file transfer | DNS queries, DHCP, VoIP/video, TFTP, NTP |

## 2. Ethernet frame and switching behaviour

Ethernet II frame: preamble, destination MAC (6), source MAC (6), type (2), payload (46 to 1500), FCS (4). Standard MTU is 1500 bytes. Frames below 64 bytes are "runts"; above 1518 (without VLAN tag) are "giants" unless jumbo frames are enabled.

A switch:
1. **Learns** the source MAC of each incoming frame and records it against the ingress port and VLAN.
2. **Forwards** known unicast out the single learned port.
3. **Floods** unknown unicast, broadcast and (by default) multicast out all other ports in the VLAN.
4. **Filters** frames whose destination is on the same port they came from.
5. **Ages out** entries (default 300 s).

```
show mac address-table
show mac address-table dynamic
show mac address-table address aaaa.bbbb.cccc
show mac address-table interface g0/1
clear mac address-table dynamic        ! ⚠ momentary flooding while it relearns
```

Collision domain: each switch port is its own collision domain (full duplex means no collisions at all). Broadcast domain: all ports of a VLAN (a router interface or a VLAN boundary ends it). Hubs: one collision domain and one broadcast domain, half duplex only.

## 3. Network components and architectures

| Device | Layer | Role |
|---|---|---|
| Hub / repeater | 1 | repeats bits to all ports (obsolete) |
| Switch (L2) | 2 | frame forwarding by MAC, VLANs |
| Multilayer switch (L3) | 2-3 | switching plus IP routing between VLANs (SVIs, routed ports) |
| Router | 3 | forwards packets between networks, WAN edge |
| Next-gen firewall (NGFW) | 3-7 | stateful filtering, application awareness, IPS, URL filtering |
| IPS | 3-7 | inline detection and blocking of attacks |
| Access point (AP) | 1-2 | bridges Wi-Fi clients to the wired LAN |
| Wireless LAN controller (WLC) | 2-7 | central management of lightweight APs (CAPWAP) |
| Endpoints, servers | | the things being connected |
| PoE | 1 | power over Ethernet: 802.3af (15.4 W), 802.3at (30 W), 802.3bt (60/100 W) |

Topologies and architectures to recognise:
- **Two-tier (collapsed core)**: access + distribution/core combined. Typical for small and medium sites.
- **Three-tier**: access, distribution, core. Large campus.
- **Spine-leaf**: every leaf connects to every spine; predictable low latency; data centre.
- **SOHO**: one device doing routing, switching, Wi-Fi and firewall.
- **WAN**: point-to-point leased line, MPLS L3VPN, Metro Ethernet, Internet VPN, SD-WAN.
- **On-premises versus cloud**: IaaS, PaaS, SaaS differ by how much you manage. Virtual machines, containers and hypervisors (type 1 bare metal, type 2 hosted) are covered in chapter 04.

## 4. Physical layer: cabling and interfaces

| Medium | Typical use | Max distance |
|---|---|---|
| UTP Cat5e/Cat6 | 1000BASE-T | 100 m |
| UTP Cat6a | 10GBASE-T | 100 m |
| Multimode fiber (MMF) | 1000BASE-SX, 10GBASE-SR | roughly 220 m to 550 m (SX), 300 m to 400 m (SR), by fiber grade |
| Single-mode fiber (SMF) | 1000BASE-LX, 10GBASE-LR | 10 km and beyond |

- **Straight-through** cable: PC to switch, router to switch. **Crossover**: like devices (switch to switch, router to PC). Modern ports with **auto-MDIX** adapt automatically (`mdix auto`, default on newer gear).
- Fiber needs the correct transceiver (SFP/SFP+) on both ends and Tx connected to Rx. A fiber link that is "down/down" is often a swapped pair or a wrong wavelength/type.

### Ethernet speed and duplex
- Autonegotiation is the default and recommended.
- Gigabit and faster should always autonegotiate.
- **Duplex mismatch** (one side full, the other half): link stays up but performance is terrible, with late collisions and CRC errors on the half-duplex side. It happens when one side is hard-coded and the other autonegotiates (the auto side falls back to half duplex at speeds of 10/100).

```
interface g0/1
 speed 100
 duplex full
 ! ... or leave both at "auto" (the default)
```

## 5. Reading interface counters

```
SW1# show interfaces g0/1
GigabitEthernet0/1 is up, line protocol is up (connected)
  ...
  Full-duplex, 1000Mb/s
  ...
  5 minute input rate 2000 bits/sec, 3 packets/sec
     0 runts, 0 giants, 0 throttles
     12 input errors, 12 CRC, 0 frame, 0 overrun, 0 ignored
     0 output errors, 0 collisions, 1 interface resets
     0 late collision, 0 deferred
```

| Counter | Likely cause | What to do |
|---|---|---|
| CRC / input errors rising | bad cable, bad connector, EMI, duplex mismatch, faulty NIC | replace/test cable, check duplex and speed on both ends |
| Runts | collisions, duplex mismatch, faulty NIC | check duplex |
| Giants | jumbo frames or MTU mismatch, faulty NIC | check MTU on both ends |
| Late collisions | duplex mismatch, cable too long | fix duplex, check cable length |
| Collisions on a full-duplex port | should be zero; duplex mismatch | fix duplex |
| Output drops | congestion (egress queue full) | QoS, faster link, find the heavy talker |
| Input queue drops / overruns | the device cannot keep up | check CPU, traffic pattern |
| Interface resets, carrier transitions | flapping link, bad cable/transceiver, `err-disable` | check logs, replace cable/SFP |

Reset the counters to take a clean baseline: `clear counters g0/1` (harmless, but you lose history).
```
show interfaces status                  ! compact: connected, notconnect, disabled, err-disabled
show interfaces g0/1 counters errors
show logging | include UPDOWN|LINK|ERR
```
Status words on a switch port:

| `show interfaces status` | Meaning |
|---|---|
| connected | link up |
| notconnect | no link (cable, far side down) |
| disabled | administratively shut |
| err-disabled | the switch shut it for a violation (port security, BPDU guard, loop, link flap). Fix the cause, then `shutdown` / `no shutdown` |

## 6. The troubleshooting method

Use a method instead of guessing:

1. **Define the problem**: who, what, since when, what changed? Reproduce it.
2. **Gather facts** with `show`, `ping`, `traceroute`, logs.
3. **Isolate** with one of the approaches:
   - **Bottom-up** (layer 1 to 7): best when you suspect physical or link problems.
   - **Top-down** (layer 7 to 1): best when the problem looks application-specific.
   - **Divide and conquer**: start in the middle (e.g. layer 3 with ping) and move up or down depending on the result.
   - **Follow the path**: trace the traffic hop by hop from source to destination.
   - **Compare configurations**: against a working device or a known-good baseline.
   - **Swap the component**: replace cable, port, SFP, module.
4. **Propose and apply one fix** at a time, with a rollback.
5. **Verify** end to end, **document** the cause and the fix.

### The connectivity ladder (works for almost any "can't reach X")
```
1. Link up on my port?                    show interfaces status / show ip interface brief
2. Correct IP, mask, gateway on the host? ipconfig /all   |   ifconfig / ip addr
3. Can I reach my gateway?                ping <default-gateway>
4. ARP resolved?                          arp -a   |   show arp
5. Can I reach something past the gateway by IP?   ping 8.8.8.8
6. Does name resolution work?             nslookup example.com
7. Where does it stop?                    traceroute / tracert
8. Is something filtering?                show access-lists, firewall logs
```
Interpretation: if step 5 works and step 6 fails, it is DNS. If 3 fails on the same subnet, it is layer 1/2 (cable, VLAN, port security, wrong mask). If 3 works and 5 fails, it is routing, NAT or an ACL beyond the gateway.

### ping and traceroute on IOS
```
ping 192.168.1.1
ping 192.168.1.1 source g0/0 repeat 100 size 1400     ! extended options
traceroute 8.8.8.8
```
Ping result characters:

| Char | Meaning |
|---|---|
| `!` | reply received |
| `.` | timeout (no reply, or first packet while ARP resolves) |
| `U` | destination unreachable (a router had no route or an ACL rejected) |
| `M` | could not fragment (DF set, MTU issue) |
| `?` | unknown packet type |

`traceroute` showing `* * *` at a hop means that hop did not answer (it may still forward traffic: rate-limited or filtered ICMP). If it stops forever at hop N, look at hop N+1 or at the return path.

## 7. CDP and LLDP (neighbour discovery) as a troubleshooting tool

```
show cdp neighbors
show cdp neighbors detail          ! neighbour IPs, platform, IOS
show lldp neighbors
lldp run                           ! LLDP is off by default on Cisco
no cdp run                         ! disable CDP globally (security hardening)
```
Use them to confirm what is really plugged into a port before touching anything.

## 8. Quick lab
1. Two PCs, one switch. Give both PCs addresses in one subnet. `ping`, then `show mac address-table` and `show arp` to see learning happen.
2. Hard-code `speed 100` / `duplex full` on the switch port only and watch what the PC side negotiates, then `show interfaces` on both ends.
3. Shut the switch port, look at `show interfaces status`, then `no shutdown`.
4. Practice the ladder: break each step on purpose (wrong mask, wrong gateway, wrong DNS) and see which step fails.
