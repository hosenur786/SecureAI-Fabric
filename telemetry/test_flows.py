from telemetry.flows import parse_flow_line


def test_icmp_flow():
    line = (
        "cookie=0x0, duration=20.224s, table=0, "
        "n_packets=5, n_bytes=490, priority=110, "
        "icmp,nw_src=10.0.0.1,nw_dst=10.0.0.2 actions=NORMAL"
    )

    flow = parse_flow_line(line)

    assert flow["src_ip"] == "10.0.0.1"
    assert flow["dst_ip"] == "10.0.0.2"
    assert flow["protocol"] == "ICMP"
    assert flow["packets"] == 5
    assert flow["bytes"] == 490
    assert flow["priority"] == 110


def test_default_normal_rule_is_ignored():
    line = (
        "cookie=0x0, duration=500s, table=0, "
        "n_packets=100, n_bytes=8000, priority=0 actions=NORMAL"
    )

    flow = parse_flow_line(line)

    assert flow is None


if __name__ == "__main__":
    test_icmp_flow()
    test_default_normal_rule_is_ignored()
    print("All flow telemetry tests passed.")
