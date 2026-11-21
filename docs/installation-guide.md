# Installation and Configuration Guide

## 1. Overview

This guide covers the environment and configuration used for Lab 5: Network Security Anomaly Detection and Log Management at ESIGELEC.

The monitoring system combines Snort, syslog-ng, Filebeat, Elasticsearch, and Kibana. Snort runs on an Ubuntu virtual machine and monitors network traffic generated from Kali Linux. The resulting alerts are collected and forwarded to Elasticsearch for processing and storage.

Elasticsearch and Kibana are installed on the Linux Mint host machine, allowing the collected security events to be searched and visualized.

The configuration files used throughout the project are available in the repository's `configs/` directory.

## 2. Laboratory Environment

The laboratory environment consists of three machines connected through separate virtual networks.

Kali Linux uses the IP address `192.168.152.131` to generate test traffic, while the Ubuntu machine monitors the laboratory network through `192.168.152.130`.

Ubuntu also uses `192.168.56.20` to communicate with the Linux Mint host at `192.168.56.1`, where Elasticsearch is running.

### Network Interfaces

The Ubuntu virtual machine has three network interfaces, each serving a different purpose.

- `enp0s3`: NAT interface used for internet access.
- `enp0s8`: Laboratory network interface used to monitor traffic from Kali Linux.
- `enp0s9`: Host-only interface used to communicate with Elasticsearch on Linux Mint.

Keeping these connections separate makes it easier to manage the laboratory traffic without interfering with communication between the monitoring components.

The IP addresses and interface names correspond to the laboratory setup. They may need to be changed if the project is configured on another machine or network.

## 3. Snort Configuration

Snort runs on the Ubuntu virtual machine and is responsible for inspecting network traffic and generating alerts when packets match the configured detection rules.

The laboratory network is defined as `192.168.152.0/24`, allowing Snort to monitor traffic associated with the test environment.

Custom detection rules are stored in:

```bash
/etc/snort/rules/local.rules
```

A copy of these rules is also available in the repository at `configs/snort/lab5.rules`.

For the ICMP and UDP scenarios, the rules use `detection_filter` to report traffic that exceeds 20 matching packets from the same source within 10 seconds. The current rule revisions are `1000002:2` for ICMP and `1000007:2` for UDP. These thresholds were tested with short bursts of traffic in the virtual network; they do not establish that a denial of service occurred.

The rules cover the five detection scenarios used in the project: threshold-based ICMP flood detection, TCP SYN traffic during a port scan, repeated connection attempts to SSH and FTP ports, and threshold-based UDP flood detection on port 9999.

### 3.1 Validating the Configuration

After adding or modifying the detection rules, the Snort configuration should be checked for errors before restarting the service.

The following command runs Snort in test mode:

```bash
sudo snort -T -c /etc/snort/snort.conf
```

If the validation completes successfully, the Snort service can be restarted:

```bash
sudo systemctl restart snort
```

The running processes can then be checked to confirm that Snort is active:

```bash
ps aux | grep '[s]nort'
```

This command displays any running Snort processes and can help verify that the service started correctly.

If Snort fails to start, the configuration and detection rules should be checked for syntax errors. The service logs may also provide more information about the problem.
