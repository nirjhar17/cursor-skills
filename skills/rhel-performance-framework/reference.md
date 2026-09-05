# RHEL performance command cheat sheet

Companion to [SKILL.md](SKILL.md). Source: [RHEL Performance Tuning Course](2311eeda-bdf5-4d5d-8517-803427266637).

## Baseline and USE

```bash
lscpu
nproc
free -h
numactl --hardware
tuned-adm active
tuned-adm verify
uptime
```

Errors first:

```bash
ras-mc-ctl --summary
ras-mc-ctl --errors
dmesg -T | tail -100
ip -s link
ethtool -S ethX | grep -iE 'drop|err|fail'
```

## CPU

```bash
mpstat -P ALL 1
vmstat 1
sar -q
pidstat 1
top
perf stat -e cycles,instructions,cache-misses,dTLB-load-misses -- <cmd>
chrt -p <pid>
```

## Memory

```bash
free -h
vmstat 1
grep -E 'Huge|Anon|MemAvailable|Swap' /proc/meminfo
cat /sys/kernel/mm/transparent_hugepage/enabled
sysctl vm.swappiness vm.overcommit_memory vm.dirty_ratio vm.dirty_background_ratio
numactl --hardware
numastat -p <pid>
```

Oracle PGA check (DBA):

```sql
SELECT name, value/1024/1024/1024 AS gb
FROM v$pgastat
WHERE name IN ('total PGA allocated','maximum PGA allocated');
```

Never in production:

```bash
# echo 1 > /proc/sys/vm/drop_caches
```

## I/O

```bash
iostat -xz 1
cat /sys/block/sda/queue/scheduler
fio --name=randread --ioengine=libaio --direct=1 --bs=8k --rw=randread \
    --numjobs=8 --iodepth=32 --size=10G --runtime=60 --time_based
```

## Network (three levels)

```bash
ethtool -g ethX
ethtool -G ethX rx 4096 tx 4096
ethtool -k ethX
ethtool -S ethX | grep -i drop
sysctl net.core.rmem_max net.core.wmem_max net.core.netdev_max_backlog
sysctl net.ipv4.tcp_rmem net.ipv4.tcp_wmem net.ipv4.tcp_mem
ping -c 5 <peer>
iperf3 -s
iperf3 -c <peer> -t 10
```

## TuneD and persistence

```bash
tuned-adm list
tuned-adm recommend
tuned-adm profile oracle
tuned-adm active
tuned-adm verify
sysctl -a | less
sysctl --system
grubby --info=ALL
```

Custom profile skeleton (`/etc/tuned/profiles/my-oracle/tuned.conf`):

```ini
[main]
summary=Site Oracle overrides
include=oracle

[sysctl]
vm.swappiness=10
kernel.numa_balancing=0
```

Then: `tuned-adm profile my-oracle`

## Oracle OS knobs (verify, do not blindly apply)

```bash
dnf install tuned-profiles-oracle
tuned-adm profile oracle
grep Huge /proc/meminfo
cat /sys/kernel/mm/transparent_hugepage/enabled
sysctl vm.swappiness kernel.numa_balancing kernel.shmmax kernel.shmall kernel.sem
```
