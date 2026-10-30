"""subnet_plan.py: check a cloud network plan before you build it.

Edit VPC and SUBNETS, then run: python3 subnet_plan.py
"""

import ipaddress
import itertools
import sys

VPC = "10.0.0.0/16"

# name: (CIDR block, availability zone, tier)
SUBNETS = {
    "public-a": ("10.0.1.0/24", "a", "public"),
    "public-b": ("10.0.2.0/24", "b", "public"),
    "private-a": ("10.0.11.0/24", "a", "private"),
    "private-b": ("10.0.12.0/24", "b", "private"),
}

# AWS keeps 5 addresses in every subnet: the first four and the last one.
AWS_RESERVED = 5


def main() -> int:
    ok = True
    vpc = ipaddress.ip_network(VPC)
    print(f"VPC {vpc}: {vpc.num_addresses} addresses")

    nets = {}
    for name, (cidr, az, tier) in SUBNETS.items():
        try:
            net = ipaddress.ip_network(cidr)
        except ValueError as err:
            print(f"BAD CIDR  {name}: {err}")
            ok = False
            continue
        nets[name] = net
        inside = net.subnet_of(vpc)
        ok = ok and inside
        usable = net.num_addresses - AWS_RESERVED
        where = "inside VPC" if inside else "OUTSIDE VPC"
        print(f"{name:10} {cidr:15} AZ {az}  {tier:8} {usable:5} usable  {where}")

    # Two subnets may never share an address.
    for (a, net_a), (b, net_b) in itertools.combinations(nets.items(), 2):
        if net_a.overlaps(net_b):
            print(f"OVERLAP   {a} {net_a} and {b} {net_b}")
            ok = False

    print("plan OK" if ok else "plan has problems")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
