# Testing Guide: Network Security Detection Scenarios

## 1. Objective

This guide describes the tests performed to evaluate the network security monitoring system developed for Lab.

Kali Linux was used to generate controlled network traffic, while Snort monitored the packets using custom detection rules. After each test, the generated alerts were checked to confirm that they had been collected and indexed in Elasticsearch.

Five scenarios were tested, covering ICMP traffic, TCP port scanning, repeated SSH and FTP connection attempts, and UDP traffic. All five produced the expected alerts.

## 2. Test Environment

The tests were carried out using three machines connected to the laboratory network.

Kali Linux, configured with the IP address `192.168.152.131`, was responsible for generating the traffic. Snort ran on an Ubuntu virtual machine at `192.168.152.130`, while Elasticsearch and Kibana were hosted on Linux Mint at `192.168.56.1`.

Before starting the tests, the monitoring services should be running.

On Ubuntu, the status of Snort, syslog-ng, and Filebeat can be checked with:

```bash
sudo systemctl status snort syslog-ng filebeat --no-pager
```

It is also important to confirm that Snort is running and monitoring the correct network interface.

```bash
ps aux | grep '[s]nort'
```

Once the services are active and Snort is monitoring the laboratory interface, the detection tests can begin.

## 3. Scenario 1: ICMP Ping Detection

The first scenario checks whether Snort can detect ICMP echo requests sent to the Ubuntu machine.

From Kali Linux, the following command sends five ping requests to the target:

```bash
ping -c 5 192.168.152.130
```

Snort rule `1000002` was configured to detect this traffic and generate the message:

```text
Someone is pinging
```

After running the command, the alerts can be checked directly in the Snort log file on Ubuntu:

```bash
sudo grep 'Someone is pinging' /var/log/snort/snort.alert.fast | tail -5
```

The test produced the expected ICMP alerts. The corresponding events were also found in Elasticsearch, confirming that the traffic was detected and the alerts were forwarded correctly.

*Evidence: Scenario 1*

## 4. Scenario 2: TCP Port Scanning

This scenario focuses on detecting TCP SYN packets generated during a port scan.

Nmap was used on Kali Linux to scan ports 20 through 100 on the Ubuntu machine.

```bash
sudo nmap -sS -Pn -p 20-100 192.168.152.130
```

The scan was monitored using Snort rule `1000003`, which generates the following message when a matching packet is detected:

```text
TCP connection attempt detected
```

The generated alerts can be checked on Ubuntu with:

```bash
sudo grep 'TCP connection attempt detected' /var/log/snort/snort.alert.fast | tail -10
```

The test generated 81 alerts, which were also indexed in Elasticsearch.

This result corresponds to the 81 ports included in the scan. However, the rule detects individual SYN packets rather than recognizing the entire port scan as a single event.

*Evidence: Scenario 2*

## 5. Scenario 3: SSH Connection Anomaly

The third scenario tests the detection of repeated TCP connection attempts to port 22, commonly used by SSH.

To generate the traffic, the following command runs eight SYN scan attempts against the SSH port:

```bash
for i in {1..8}; do sudo nmap -sS -Pn -p 22 --max-retries 0 192.168.152.130 >/dev/null; done
```

A threshold-based Snort rule with SID `1000004` was configured to detect repeated connection attempts within a short period.

When the rule is triggered, Snort generates the message:

```text
Possible SSH Brute Force Attack
```

The alerts can be checked using:

```bash
sudo grep 'Possible SSH Brute Force Attack' /var/log/snort/snort.alert.fast | tail -5
```

Snort detected the repeated connection attempts and generated the expected alerts.

Despite the alert message, this test does not simulate an actual password brute-force attack. It only generates repeated TCP SYN packets directed at port 22. No SSH authentication attempts or password guessing were performed.

The purpose of this scenario is to verify that the threshold-based rule can identify this type of connection pattern.

*Evidence: Scenario 3*

## 6. Scenario 4: FTP Connection Anomaly

The FTP scenario uses a similar approach, but targets TCP port 21.

Repeated connection attempts were generated from Kali Linux using the following command:

```bash
for i in {1..8}; do sudo nmap -sS -Pn -p 21 --max-retries 0 192.168.152.130 >/dev/null; done
```

Snort rule `1000005` monitors these attempts and generates an alert when the configured threshold is reached.

The expected message is:

```text
Possible FTP Brute Force Attack
```

To check the alerts on Ubuntu:

```bash
sudo grep 'Possible FTP Brute Force Attack' /var/log/snort/snort.alert.fast | tail -5
```

The rule triggered as expected, and the corresponding event was indexed in Elasticsearch with destination port 21.

As in the SSH scenario, the detection is based on repeated connection attempts rather than failed login attempts. The test therefore confirms that the rule can identify unusual TCP connection activity, but not an actual FTP authentication attack.

*Evidence: Scenario 4*

## 7. Scenario 5: UDP Traffic Detection

The final scenario checks whether Snort can detect UDP traffic sent to a specific destination port.

A test message was sent from Kali Linux to UDP port 9999 on the Ubuntu machine:

```bash
echo "LAB5 UDP test" | nc -u -w1 192.168.152.130 9999
```

Snort rule `1000007` was configured to detect this traffic and generate the following alert:

```text
LAB5 UDP Traffic Detected
```

The alert can be found in the Snort log using:

```bash
sudo grep 'LAB5 UDP Traffic Detected' /var/log/snort/snort.alert.fast | tail -5
```

The packet was detected successfully, and the alert was also found in Elasticsearch.

This scenario verifies that the custom rule can identify UDP traffic matching the configured conditions. It does not represent a specific network attack.

*Evidence: Scenario 5*

## 8. Verifying Alerts in Elasticsearch

After running the tests, the next step is to confirm that the generated alerts were received and processed by Elasticsearch.

This can be done through Kibana Dev Tools, which allows Elasticsearch queries to be executed directly.

The following query retrieves up to ten indexed events containing a Snort rule identifier:

```json
GET filebeat-*/_search
{
  "size": 10,
  "query": {
    "exists": {
      "field": "snort.rule_id"
    }
  },
  "_source": [
    "@timestamp",
    "snort.rule_id",
    "snort.alert_type",
    "snort.protocol",
    "snort.source_ip",
    "snort.destination_ip",
    "snort.destination_port",
    "error.message"
  ]
}
```

This query is useful for checking whether the ingest pipeline extracted the expected information from the Snort alerts.

It is also possible to search for events related to a specific scenario. For example, the following query looks for the UDP detection message:

```json
GET filebeat-*/_search
{
  "query": {
    "match_phrase": {
      "message": "LAB5 UDP Traffic Detected"
    }
  }
}
```

The returned documents should contain the corresponding rule ID, protocol, and network addresses.

For scenarios involving TCP or UDP, the destination port can also be checked to confirm that the event matches the generated traffic.

If an alert appears in the Snort log but not in Elasticsearch, the syslog-ng and Filebeat services should be checked, along with the Elasticsearch ingest pipeline configuration.

## 9. Verifying the Kibana Dashboard

Once the alerts have been indexed, they can be viewed through the **Snort Security Monitoring** dashboard in Kibana.

The dashboard should be opened with a time range that includes the test execution. Otherwise, some events may not appear even if they were indexed correctly.

The dashboard contains six panels displaying the total number of alerts, alert activity over time, alert types, protocols, priorities, and the most frequent source IP addresses.

These visualizations provide a broader view of the test results. The timeline shows when the traffic was generated, while the other panels make it easier to compare the alerts produced by each scenario.

The dashboard configuration is available in the repository at `dashboards/snort-security-monitoring.ndjson`.

## 10. Test Results Summary

All five scenarios produced the expected Snort alerts, and the corresponding events were found in Elasticsearch.

The ICMP test confirmed that the system could detect ping requests, while the TCP scanning scenario generated 81 alerts from the Nmap scan.

The SSH and FTP scenarios showed that threshold-based rules could detect repeated connection attempts to ports 22 and 21. The UDP test also confirmed that traffic directed to port 9999 could be identified using a custom rule.

In addition to traffic detection, the tests verified the log collection and processing workflow. The alerts generated by Snort were collected through syslog-ng, forwarded by Filebeat, and processed in Elasticsearch.

The results were also available through the Kibana dashboard, allowing the detected activity to be examined without manually reading the log files.

Overall, the tests confirmed that the monitoring system worked as expected under the conditions used in the laboratory. Although these scenarios do not cover every type of network attack, they provide a practical way to verify the integration between the detection, log collection, and visualization components.
