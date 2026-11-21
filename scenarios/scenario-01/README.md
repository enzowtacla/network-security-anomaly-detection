# Scenario 01 — ICMP Ping Detection

## Objective

Detect ICMP echo requests sent from Kali Linux to the Ubuntu Snort machine.

## Test Environment

- **Traffic generator:** Kali Linux (`192.168.152.131`)
- **Detection machine:** Ubuntu Snort (`192.168.152.130`)
- **Monitoring tools:** Snort, syslog-ng, Filebeat, Elasticsearch, and Kibana

## Test Command

Run the following command on Kali Linux:

```bash
ping -c 5 192.168.152.130
```

## Expected Detection

- **Snort rule ID:** `1000002`
- **Expected alert:** `Someone is pinging`

## Verification

On Ubuntu, check the Snort alert log:

```bash
sudo grep -F 'Someone is pinging' /var/log/snort/snort.alert.fast | tail -5
```

Then verify that the corresponding event appears in Elasticsearch using Kibana Discover or Dev Tools.

## Result

Snort generated ICMP alerts, which were successfully indexed in Elasticsearch.

## Evidence

### Evidence 1

![Scenario 01 evidence 1](../../docs/screenshots/scenario-01-icmp-ping-kali.png)

### Evidence 2

![Scenario 01 evidence 2](../../docs/screenshots/scenario-01-snort-alert.png)

### Evidence 3

![Scenario 01 evidence 3](../../docs/screenshots/scenario-01-icmp-kibana.png)

## Limitations

ICMP echo requests are not inherently malicious. This test validates traffic detection and log forwarding.

[Back to the main README](../../README.md)
