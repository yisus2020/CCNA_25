# 00. Cisco IOS basics (start here)

> Document version: 1.0 | Updated: 2026-11-12 | Targets: Cisco IOS XE 17.x; exam blueprint CCNA 200-301

Zero-to-working CLI knowledge. Everything in later chapters assumes you are comfortable with this one.
Commands are shown for IOS / IOS-XE routers and switches. `R1#` and `SW1#` are the prompts; you type what comes after.

> Lab warning: commands marked with ⚠ can erase configuration, reload the device or cut your own connection. Run them on lab gear (Packet Tracer, GNS3, CML, real lab devices), never on a production device without a maintenance window and a rollback plan.

## 1. CLI modes

| Mode | Prompt | How to enter | Used for |
|---|---|---|---|
| User EXEC | `R1>` | login | very limited `show`, ping |
| Privileged EXEC | `R1#` | `enable` | all `show`, copy, reload, debug |
| Global configuration | `R1(config)#` | `configure terminal` | device-wide settings |
| Interface configuration | `R1(config-if)#` | `interface g0/0` | IP, speed, duplex, shutdown |
| Line configuration | `R1(config-line)#` | `line console 0`, `line vty 0 15` | console, SSH/Telnet access |
| Router configuration | `R1(config-router)#` | `router ospf 1` | routing protocols |
| VLAN configuration | `SW1(config-vlan)#` | `vlan 10` | VLAN names |

```
R1> enable
R1# configure terminal
R1(config)# interface gigabitEthernet 0/0
R1(config-if)# exit            ! back one level
R1(config)# end                ! straight back to privileged EXEC (Ctrl+Z does the same)
R1# disable                    ! back to user EXEC
```

## 2. CLI productivity

| Key / command | Effect |
|---|---|
| `?` | context help; `show ?` lists options, `sh ip?` lists commands starting with "ip" |
| `Tab` | complete the command |
| `Ctrl+A` / `Ctrl+E` | start / end of line |
| `Ctrl+R` | redisplay the line (useful after a syslog message interrupts typing) |
| `Ctrl+Shift+6` | break a running ping or traceroute |
| `Up` / `Down` or `Ctrl+P` / `Ctrl+N` | command history |
| `do show run` | run an EXEC command from inside any config mode |
| `no <command>` | remove a setting, e.g. `no shutdown`, `no ip address` |
| `default <command>` | return a setting to its default |

Abbreviations work if they are unambiguous: `conf t`, `int g0/1`, `sh ip int br`.

Output filtering:
```
show running-config | include ip address
show running-config | section ospf
show running-config | begin interface
show ip interface brief | exclude unassigned
show running-config | include ^hostname
terminal length 0                      ! no "--More--" paging for this session
```

## 3. Initial configuration of a router or switch

```
Router> enable
Router# configure terminal
Router(config)# hostname R1
R1(config)# no ip domain-lookup                      ! stops the 60 s hang on typos
R1(config)# enable secret Str0ng!Pass                ! hashed; always prefer over "enable password"
R1(config)# service password-encryption              ! weak (type 7) obfuscation for line passwords
R1(config)# banner motd # Authorized access only #
R1(config)# line console 0
R1(config-line)# password C0nsole!Pass
R1(config-line)# login
R1(config-line)# logging synchronous                 ! syslog does not break what you type
R1(config-line)# exec-timeout 10 0                   ! 10 minutes idle logout
R1(config-line)# exit
R1(config)# interface g0/0
R1(config-if)# description LAN to SW1
R1(config-if)# ip address 192.168.1.1 255.255.255.0
R1(config-if)# no shutdown
R1(config-if)# end
R1# copy running-config startup-config               ! SAVE (or: write memory)
```

Notes:
- `enable secret` wins over `enable password` if both exist.
- A router interface is **administratively down** by default; a switch interface is up by default.
- Nothing you type is saved until `copy running-config startup-config`.

### Remote management with SSH (preferred over Telnet)
```
R1(config)# ip domain-name lab.local
R1(config)# username admin secret Adm1n!Pass
R1(config)# crypto key generate rsa modulus 2048     ! needs hostname + domain name first
R1(config)# ip ssh version 2
R1(config)# line vty 0 15
R1(config-line)# login local                         ! use the local user database
R1(config-line)# transport input ssh                 ! SSH only, no Telnet
R1(config-line)# exec-timeout 10 0
```
Verify: `show ip ssh`, `show ssh`, `show users`, `show line vty 0 15`.

### Switch management address (Layer 2 switch)
A Layer 2 switch has no routed ports; give it an IP on a VLAN interface (SVI):
```
SW1(config)# interface vlan 1
SW1(config-if)# ip address 192.168.1.2 255.255.255.0
SW1(config-if)# no shutdown
SW1(config-if)# exit
SW1(config)# ip default-gateway 192.168.1.1          ! needed to be reachable from other subnets
```
(Best practice is a dedicated management VLAN rather than VLAN 1; see the VLAN chapter.)

## 4. Files, memory and reloading

| Memory | Holds | Survives reboot? |
|---|---|---|
| ROM | bootstrap / ROMMON | yes |
| Flash | IOS image, other files | yes |
| NVRAM | startup-config | yes |
| RAM | running-config, routing/ARP/MAC tables | no |

```
show running-config            ! what is active now
show startup-config            ! what loads at boot
copy running-config startup-config
copy running-config tftp:      ! backup to a TFTP server (prompts for address and name)
show flash:                    ! files and free space
show version                   ! IOS version, uptime, reload reason, config register, serial number
show boot                      ! boot variables (on switches)
```

⚠ Dangerous:
```
erase startup-config           ! (also: write erase) wipes the saved config
reload                         ! reboots; answer "no" to the save prompt only if you mean to discard changes
delete vlan.dat                ! on switches, VLAN database lives in flash (needed for a full switch reset)
```
Config register: `0x2102` = normal boot. `0x2142` = ignore startup-config at boot (used for password recovery from ROMMON; set it back to `0x2102` afterwards with `config-register 0x2102`).

## 5. The `show` commands you will use every day

```
show running-config
show ip interface brief          ! one line per interface: IP, status, protocol
show interfaces                  ! counters, errors, duplex
show interfaces status           ! switches: port, status, VLAN, duplex, speed
show interfaces description
show ip route                    ! routers
show mac address-table           ! switches
show arp                         ! IP to MAC cache
show vlan brief                  ! switches
show cdp neighbors detail
show version
show clock
show users                       ! who is logged in
show history
show logging                     ! buffer of syslog messages
```

Reading `show ip interface brief`:

| Status | Protocol | Meaning |
|---|---|---|
| up | up | working at layers 1 and 2 |
| administratively down | down | someone typed `shutdown` (fix: `no shutdown`) |
| down | down | layer 1 problem: no cable, far end down, bad cable, wrong SFP |
| up | down | layer 2 problem: encapsulation mismatch, no keepalives, clocking issue (serial) |

## 6. Interface basics

```
R1(config)# interface range g0/1 - 4        ! apply the same settings to several ports (switch)
SW1(config-if-range)# description Access ports
SW1(config-if-range)# speed 100
SW1(config-if-range)# duplex full
SW1(config-if-range)# shutdown              ! ⚠ takes the ports down
SW1(config-if-range)# no shutdown
```
Autonegotiation is the default and the safest. If you hard-set speed/duplex on one side only, the other side may fall back to half duplex: a classic duplex mismatch (see chapter 01).

## 7. Troubleshooting the CLI itself

| Message | Meaning | Fix |
|---|---|---|
| `% Invalid input detected at '^' marker` | typo, or wrong mode | check the caret position; check you are in the right mode (`?`) |
| `% Incomplete command.` | missing argument | add `?` at the end to see what is expected |
| `% Ambiguous command` | abbreviation matches several commands | type more characters |
| Device hangs for ~60 s after a typo | it tried to resolve the word as a hostname | `no ip domain-lookup`; break with `Ctrl+Shift+6` |
| Config disappeared after a reboot | never saved | `copy running-config startup-config` |
| Cannot SSH in | see checklist below | |

SSH checklist:
1. Reachability: `ping` the device IP from the client; is the SVI/interface up/up?
2. `show ip ssh` says "SSH Disabled"? You are missing the hostname, domain name or RSA key.
3. `line vty` has `login local` but there is no `username`? Add one.
4. `transport input ssh` on the vty lines, and the client uses SSH version 2.
5. An ACL on the vty lines (`access-class`) or on the path is blocking the client.
6. Layer 2 switch: is `ip default-gateway` set when the client is on another subnet?

## 8. Mini lab
1. Two routers connected back-to-back, or one router and one switch, in a simulator.
2. Set hostnames, `enable secret`, console password, banner, `no ip domain-lookup`.
3. Give R1 `192.168.1.1/24` and the switch SVI `192.168.1.2/24`; ping both ways.
4. Enable SSH on both and connect from R1 to SW1 with `ssh -l admin 192.168.1.2`.
5. Save, `reload`, confirm the config survived. Then deliberately skip `copy run start` once and see what happens.

See also the existing quick notes in `../BASIC_COMMAND/`.
