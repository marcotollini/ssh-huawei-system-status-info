import argparse
import json
import logging


def setup_logging(debug):
    logger = logging.getLogger()
    if not debug:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.DEBUG)
    c_handler = logging.StreamHandler()
    c_format = logging.Formatter(
        '[%(asctime)s] %(levelname)s - %(name)s - %(message)s')
    c_handler.setFormatter(c_format)
    logger.addHandler(c_handler)


def main():
    parser = argparse.ArgumentParser(
        description='Save the processes status of Huawei routers on a file')

    parser.add_argument('-d', '--debug', dest='debug', action='store_const',
                        const=True, default=False, help='Debug mode')
    parser.add_argument('-p', '--console', dest='console', action='store_const',
                        const=True, default=False, help='Write the state also on the console')

    parser.add_argument('-c', '--config', dest='config_path',
                        help='Configuration file')

    args = parser.parse_args()

    setup_logging(args.debug)

    with open(args.config_path, 'r') as config_fp:
        config = json.load(config_fp)
    logging.info(f'config file correctly loaded with {len(config)} routers')


if __name__ == "__main__":
    # main()
    text = """Cpu utilization statistics at 2021-02-25 10:46:53 787 ms
System cpu use rate is : 54%
Cpu utilization for five seconds: 54% ;  one minute: 53% ;  five minutes: 29%.
Max CPU Usage : 99%
Max CPU Usage Stat. Time : 2021-02-04 16:01:03 536 ms
---------------------------
ServiceName  UseRate
---------------------------
SVRO             23%
SYSTEM           23%
BGP               7%
IP STACK          1%
AAA               0%
ARP               0%
BRAS              0%
CMF               0%
CSP               0%
DEVICE            0%
DHCP              0%
ETRUNK            0%
EUM               0%
FEA               0%
FEC               0%
FIBRESM           0%
IFM               0%
ISIS              0%
LDT               0%
LINK              0%
LLDP              0%
LOCAL PKT         0%
MFLP              0%
MSTP              0%
ND                0%
NETSTREAM         0%
OAM               0%
PKI               0%
PNP               0%
PTPA              0%
RBS               0%
RGM               0%
RM                0%
SLA               0%
SMLK              0%
SOC               0%
TNLM              0%
TUNNEL            0%
VLAN              0%
---------------------------
CPU Usage Details
----------------------------------------------------------------
CPU     Current  FiveSec   OneMin  FiveMin  Max MaxTime
----------------------------------------------------------------
cpu0        40%      38%      40%      29%  99% 2021-02-04 16:02:20
cpu1        46%      43%      40%      25%  99% 2021-02-04 15:36:10
cpu2        36%      38%      37%      27%  99% 2021-02-04 16:02:40
cpu3        97%      99%      95%      35%  99% 2021-02-02 09:20:43
----------------------------------------------------------------"""

    text = """Memory utilization statistics at 2021-02-25 10:55:39 153 ms
System Total Memory Is: 15766020 Kbytes
Total Memory Used Is: 3507512 Kbytes
Memory Using Percentage Is: 22%
----------------------------------------
Process memory information in the slot:
----------------------------------------
ProcessId  ProcessName      Used(Kbytes)
----------------------------------------
4          LM                     444005
1008       PROTO4                  82154
1019       VFPNSE                 104390
1018       VFPFWD                  88203
1002       RESP                    59179
1004       PROTO5                  40696
2          SM                      27849
3          CFG                    397307
1013       FESMB                   79360
1012       PSM1                   105415
10001      PROTO1                  27340
1025       IGP_SR                  29316
1016       PROTO3                  35555
1010       CFG_COMMON              31397
10002      FES                    125849
1020       BGP                     72406
1015       OPS                     28367
1011       LOGSERVER               28323
1014       SSH                     19127
1007       DHCP                    12884
1001       SYSMNT                  11935
1006       PKI                      9372
1027       BGPSERVICE              27268
1003       CLOCK                   12451
1005       PSM2                    15011
1009       LLP                     12963
1017       SYSMNT_LS               10908
1000       LICENSE                 12878
0          system                1555604
----------------------------------------"""
    text = '---\n' + text
    rows = text.split('\n')
    sections_indexes = [i for i in range(len(rows)) if '---' in rows[i]]
    sections = [rows[sections_indexes[si]+1 : sections_indexes[si+1]] for si in range(len(sections_indexes) - 1)]

    interesting_section = sections[3]
    print(interesting_section)
    splitting = [r.split(' ') for r in interesting_section]
    splitting_cleaned = [[y for y in x if y != ''] for x in splitting]
    # processes = [[' '.join(p[:-1]), int(p[-1][:-1])] for p in splitting_cleaned]
    processes = [[p[0], ' '.join(p[1:-1]), int(p[-1])] for p in splitting_cleaned]
    print(processes)
