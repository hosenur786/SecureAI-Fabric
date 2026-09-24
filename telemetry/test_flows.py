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

def test_flow_rates():
    previous = [
        {
            "src_ip": "10.0.0.1",
            "dst_ip": "10.0.0.2",
            "protocol": "ICMP",
            "packets": 10,
            "bytes": 980,
        }
    ]

    current = [
        {
            "src_ip": "10.0.0.1",
            "dst_ip": "10.0.0.2",
            "protocol": "ICMP",
            "packets": 20,
            "bytes": 1960,
        }
    ]

    from telemetry.flows import calculate_flow_rates

    result = calculate_flow_rates(
        previous,
        current,
        2
    )

    assert result[0]["packet_delta"] == 10
    assert result[0]["byte_delta"] == 980
    assert result[0]["packets_per_sec"] == 5.0
    assert result[0]["bytes_per_sec"] == 490.0


if __name__ == "__main__":
    test_icmp_flow()
    test_default_normal_rule_is_ignored()
    test_flow_rates()
    print("All flow telemetry tests passed.")
