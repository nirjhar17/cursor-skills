# Network Configuration Checks (CRITICAL)

## NIC & Interface

| Check | sosreport Path |
|---|---|
| NIC list + state | `sos_commands/networking/ip_address` or `proc/net/dev` |
| MTU per interface | `sos_commands/networking/ip_address` |
| NIC driver + speed | `sos_commands/networking/ethtool_*` |
| Ring buffer current/max | `sos_commands/networking/ethtool_-g_*` |
| Bonding config | `proc/net/bonding/*` |
| VLAN sub-interfaces | `sos_commands/networking/ip_-d_link` |

## NetworkManager

| Check | sosreport Path |
|---|---|
| NM connection method | `sos_commands/networkmanager/nmcli_con_show_*` — check `ipv4.method` (manual vs auto/DHCP) |
| Parent vs child IP conflict | Compare: parent NIC using DHCP while VLAN child has static IP |
| DHCP client activity | `var/log/messages` — grep for `dhclient\|DHCP\|dhcp` |

## Traffic Health

| Check | sosreport Path |
|---|---|
| RxDrop / TxDrop | `proc/net/dev` or xsos NETDEV section |
| TCP buffer overruns | `sos_commands/networking/netstat_-s` — grep "pruned from receive queue" |
| No buffer space errors | `var/log/messages` or `sos_commands/logs/journalctl*` — grep "No buffer space" |

## Routing

| Check | sosreport Path |
|---|---|
| Routing table | `sos_commands/networking/ip_route` or `route_-n` |

## Sysctl — Network

| Check | sosreport Path |
|---|---|
| rmem_max | `proc/sys/net/core/rmem_max` |
| wmem_max | `proc/sys/net/core/wmem_max` |
| rmem_default | `proc/sys/net/core/rmem_default` |
| wmem_default | `proc/sys/net/core/wmem_default` |
| netdev_max_backlog | `proc/sys/net/core/netdev_max_backlog` |
| netdev_budget | `proc/sys/net/core/netdev_budget` |
| somaxconn | `proc/sys/net/core/somaxconn` |
| tcp_rmem | `proc/sys/net/ipv4/tcp_rmem` |
| tcp_wmem | `proc/sys/net/ipv4/tcp_wmem` |
| tcp_keepalive_time | `proc/sys/net/ipv4/tcp_keepalive_time` |
| tcp_keepalive_intvl | `proc/sys/net/ipv4/tcp_keepalive_intvl` |
| tcp_keepalive_probes | `proc/sys/net/ipv4/tcp_keepalive_probes` |
| ip_local_port_range | `proc/sys/net/ipv4/ip_local_port_range` |

## Cross-Tier Network Alignment

| Check | What to compare |
|---|---|
| Chrony NTP sources | Same time servers across all tiers? |
| DNS resolv.conf | Same nameservers? |
| /etc/hosts | Consistent entries? |
| nsswitch.conf | Same `hosts:` lookup order? |
| MTU | Matching across interconnected interfaces? |
| ip_local_port_range | Sufficient for expected connections? |
| Kernel version | Same or compatible across tiers? |
