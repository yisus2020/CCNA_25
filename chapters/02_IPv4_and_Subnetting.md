# 02. IPv4 addressing and subnetting

> Document version: 1.0 | Updated: 2026-11-12 | Targets: Cisco IOS XE 17.x; exam blueprint CCNA 200-301

Exam domain 1 and 3 (Network Fundamentals, IP Connectivity). Everything about IPv4 addressing, subnet maths, VLSM, host configuration and the addressing troubleshooting that goes with it.

## 1. Address basics

An IPv4 address is 32 bits, written as four octets (dotted decimal). The mask splits it into a **network part** and a **host part**.

| Prefix | Mask | Block size (interesting octet) | Hosts per subnet |
|---|---|---|---|
| /8 | 255.0.0.0 | 1 (1st octet) | 16,777,214 |
| /16 | 255.255.0.0 | 1 (2nd octet) | 65,534 |
| /24 | 255.255.255.0 | 1 (3rd octet) | 254 |
| /25 | 255.255.255.128 | 128 | 126 |
| /26 | 255.255.255.192 | 64 | 62 |
| /27 | 255.255.255.224 | 32 | 30 |
| /28 | 255.255.255.240 | 16 | 14 |
| /29 | 255.255.255.248 | 8 | 6 |
| /30 | 255.255.255.252 | 4 | 2 |
| /31 | 255.255.255.254 | 2 | 2 (point-to-point links only, RFC 3021) |
| /32 | 255.255.255.255 | 1 | 1 (host route, loopback) |

Hosts = 2^h - 2, where h is the number of host bits (subtract network and broadcast addresses).

### Classes and special ranges
| Range | Meaning |
|---|---|
| 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16 | **Private** (RFC 1918), not routable on the Internet, need NAT |
| 127.0.0.0/8 | Loopback |
| 169.254.0.0/16 | **APIPA / link-local**: a host that failed to get a DHCP lease gives itself one of these |
| 224.0.0.0/4 | Multicast (224.0.0.5 and .6 OSPF, 224.0.0.9 RIPv2, 224.0.0.102 HSRP v2 / 224.0.0.18 VRRP) |
| 240.0.0.0/4 | Reserved |
| 255.255.255.255 | Limited broadcast |
| Class A / B / C | first octet 1-126 / 128-191 / 192-223 (classful history, still asked in the exam) |

Address types: **unicast** (one to one), **broadcast** (one to all in the subnet), **multicast** (one to a group).

## 2. Subnet maths: the quick method

For any address/prefix:
1. Find the **interesting octet** (the one where the mask is not 0 or 255).
2. **Block size** = 256 - mask value in that octet.
3. **Network** = largest multiple of the block size that is <= the address value in that octet (earlier octets copied, later octets 0).
4. **Broadcast** = next network - 1 (later octets 255).
5. **Usable range** = network + 1 to broadcast - 1.

### Worked examples (verified)

**Example 1: 192.168.10.77/26**
- Mask 255.255.255.192, interesting octet = 4th, block = 64.
- Multiples of 64: 0, 64, 128, 192 → 77 falls in 64.
- Network 192.168.10.64, broadcast 192.168.10.127, usable .65 to .126 (62 hosts).

**Example 2: 172.16.45.200/20**
- Mask 255.255.240.0, interesting octet = 3rd, block = 16.
- Multiples of 16: ... 32, 48 → 45 falls in 32.
- Network 172.16.32.0, broadcast 172.16.47.255, usable 172.16.32.1 to 172.16.47.254 (4,094 hosts).

**Example 3: 10.1.1.130/25**
- Block = 128 → 130 falls in 128.
- Network 10.1.1.128, broadcast 10.1.1.255, usable .129 to .254 (126 hosts).

### Same subnet or not?
Two hosts can talk directly (no router) only if they have the **same network address** under the same mask.
Example: 192.168.10.60/26 and 192.168.10.70/26 → networks are .0 and .64 → **different** subnets, a router is needed even though they look close.

### Choosing a mask for N hosts
Find the smallest h with 2^h - 2 >= N: 2 hosts → /30, 6 → /29, 14 → /28, 30 → /27, 62 → /26, 126 → /25, 254 → /24.

## 3. VLSM (variable length subnet masks)

Rule: allocate the **largest** subnets first, then the smaller ones, so blocks stay aligned and do not overlap.

**Example: 192.168.1.0/24, requirements: LAN A 100 hosts, LAN B 50, LAN C 25, one router link (2 hosts)**

| Subnet | Need | Mask | Network | Usable range | Broadcast |
|---|---|---|---|---|---|
| LAN A | 100 | /25 (126) | 192.168.1.0 | .1 - .126 | .127 |
| LAN B | 50 | /26 (62) | 192.168.1.128 | .129 - .190 | .191 |
| LAN C | 25 | /27 (30) | 192.168.1.192 | .193 - .222 | .223 |
| WAN link | 2 | /30 (2) | 192.168.1.224 | .225 - .226 | .227 |

Free space left: 192.168.1.228 to .255.

### Summarisation (route aggregation)
Find the common leading bits of the networks. Example: 10.1.0.0/24, 10.1.1.0/24, 10.1.2.0/24, 10.1.3.0/24 → the first 22 bits are identical → **10.1.0.0/22**. Summaries only work when the blocks are contiguous and aligned to a power of two.

## 4. Configuring IPv4 on Cisco devices

### Router interface
```
R1(config)# interface g0/0
R1(config-if)# description LAN to SW1
R1(config-if)# ip address 192.168.1.1 255.255.255.0
R1(config-if)# no shutdown
```
Router interfaces are **shut down by default**; switch ports are up by default.

### Secondary address (rare)
```
ip address 10.9.9.1 255.255.255.0 secondary
```

### Loopback
```
interface loopback0
 ip address 1.1.1.1 255.255.255.255
```
Loopbacks never go down; useful as router ID and management address.

### Switch management address
```
SW1(config)# interface vlan 1
SW1(config-if)# ip address 192.168.1.2 255.255.255.0
SW1(config-if)# no shutdown
SW1(config)# ip default-gateway 192.168.1.1
```

### DHCP client on a router interface
```
interface g0/1
 ip address dhcp
```

### Verify
```
show ip interface brief
show interfaces g0/0
show ip interface g0/0
show running-config interface g0/0
show ip route connected
```

## 5. ARP

ARP maps an IPv4 address to a MAC address on the local subnet. A host that wants to reach a destination **outside** its subnet ARPs for the **default gateway** instead.

```
R1# show ip arp
SW1# show ip arp         ! on a switch with an SVI
C:\> arp -a              ! Windows
$ arp -a  |  ip neigh    ! Mac, Linux
```
Entries with "Incomplete" mean nobody answered the ARP request: wrong VLAN, dead host, wrong subnet or a filtered/down link.

## 6. Host settings and what a host needs

A working host needs: **IP, mask, default gateway, DNS server**.

| Windows | Mac / Linux |
|---|---|
| `ipconfig /all` | `ifconfig` or `ip addr` |
| `ipconfig /release` and `/renew` | `sudo dhclient -r` / `-v` (Linux) |
| `route print` | `netstat -rn` or `ip route` |
| `nslookup name` | `dig name` / `nslookup name` |
| `tracert` | `traceroute` |

## 7. Troubleshooting IPv4 addressing

| Symptom | Likely cause | Check / fix |
|---|---|---|
| Host has 169.254.x.x | DHCP unreachable or no lease | Check the port VLAN, DHCP server, `ip helper-address` on the gateway; renew |
| Can ping neighbours but not other subnets | Missing or wrong default gateway | `ipconfig /all`; gateway must be in the same subnet as the host |
| Cannot ping the gateway | Wrong mask, wrong VLAN, port down, port security | Compare network address of host and gateway; `show interfaces status`; `show vlan brief` |
| Works by IP, fails by name | DNS | `nslookup`; check DNS servers in DHCP or host config |
| Two hosts, "duplicate IP" warning | Address conflict | `show ip arp`, find the second MAC; fix static or DHCP exclusions |
| Router interface `up/down` or `administratively down` | Shutdown, no cable, no carrier | `no shutdown`, check cable and far end |
| Router interface `up/up` but pings fail | Wrong IP/mask on one side | Both ends of a link must be in the same subnet |
| `% x.x.x.x overlaps with GigabitEthernet0/1` | Two interfaces in the same subnet | Re-plan the addressing |
| Pings from the router fail only on the first packet (`.!!!!`) | ARP resolving | Normal |
| Intermittent reachability | Duplex/CRC (chapter 01), loops, flapping link | `show interfaces`, `show logging` |

### Subnet mistakes seen in the exam
- Using the **network** or **broadcast** address as a host address.
- A mask typed as `255.255.255.255` on a LAN interface.
- Gateway outside the host subnet.
- Overlapping VLSM blocks.
- Discontiguous summaries.

## 8. Quick lab
1. Take 172.20.0.0/16 and carve out: 500 hosts, 120 hosts, 60 hosts, three point-to-point links. Write the table by hand, then configure it on routers and check with `show ip interface brief`.
2. Break it: change one mask to /25 on a host, and use `ping`, `show ip arp` and `show ip route` to find the break.
3. Summarise all your subnets into the smallest possible aggregate.
