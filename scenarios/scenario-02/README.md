# Scenario 02 — TCP Port Scan Detection

## 1. Objective

The second scenario examined TCP SYN packets generated during a port scan of ports 20 through 100 on the Ubuntu machine.

The purpose was to check whether the configured Snort rule detected the traffic and whether the alert reached Elasticsearch.

## 2. Test Environment

Kali Linux (`192.168.152.131`) generated the traffic. Snort monitored the laboratory network on Ubuntu (`192.168.152.130`). syslog-ng and Filebeat collected and forwarded the alerts to Elasticsearch, where they could be examined using Kibana.

## 3. Test Procedure

The following command was executed on Kali Linux:

```bash
sudo nmap -sS -Pn -p 20-100 192.168.152.130
```

Snort rule `1000003` was configured to generate the message:

```text
TCP connection attempt detected
```

On Ubuntu, the alert can be checked using:

```bash
sudo grep -F 'TCP connection attempt detected' /var/log/snort/snort.alert.fast | tail -5
```

## 4. Results

Snort generated 81 alerts, corresponding to the 81 ports scanned with Nmap. The alerts were also indexed in Elasticsearch.

## 5. Evidence

### Traffic generated from Kali Linux

![Kali Linux test](../../docs/screenshots/scenario-02-ping-kali.png)

### Snort alert output

![Snort alert](../../docs/screenshots/scenario-02-snort-alert.png)

### Kibana / Elasticsearch evidence

![Indexed alert](../../docs/screenshots/scenario-02-tcp-kibana.png)

## 6. Limitations

The rule matches individual SYN packets. It does not correlate packets into a single scan event, so a legitimate connection attempt can also generate an alert.

[Back to the main README](../../README.md)
