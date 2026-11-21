# Results and Limitations

## 1. Overview

The project focused on building a network security monitoring system capable of detecting certain types of network activity, collecting alerts, and making the results available for analysis.

The laboratory environment combined Snort, syslog-ng, Filebeat, Elasticsearch, and Kibana. Each tool handled a different part of the monitoring process, from traffic detection to log storage and visualization.

Kali Linux was used to generate controlled network traffic across five test scenarios. The purpose was to check whether the configured detection rules worked and whether the generated alerts could pass through the entire logging system.

## 2. Detection Results

All five scenarios produced the expected Snort alerts during the laboratory tests.

The ICMP scenario used rule `1000002`, revision 2, to detect a short burst of echo requests exceeding 20 packets within 10 seconds. A test using 30 ping requests triggered multiple alerts. The events were also found in Elasticsearch with the expected structured fields.

Rule `1000003` monitored TCP SYN packets during a scan of ports 20 through 100. The scan generated 81 alerts, one for each port included in the test.

The SSH and FTP scenarios used rules `1000004` and `1000005` to identify repeated connection attempts to ports 22 and 21. Both tests triggered their configured thresholds. Although the alert messages refer to possible brute-force attacks, no password guessing or authentication failures were involved.

The final scenario used rule `1000007`, revision 2, to detect elevated UDP traffic sent to port 9999. A controlled sequence of 30 messages generated two Snort alerts. This confirms the threshold rule was triggered, but not that a service was disrupted.

The results show that the configured rules detected the selected traffic patterns. The ICMP and UDP scenarios represent short, controlled bursts rather than sustained denial-of-service attacks.

## 3. Log Collection and Processing

Detecting the traffic was only part of the project. The generated alerts also needed to be collected and processed before they could be analyzed.

Snort recorded the alerts in its fast alert log, which was monitored by syslog-ng. The collected messages were then written to a separate log file and forwarded to Elasticsearch through Filebeat.

An ingest pipeline named `snort-lab5-pipeline` handled the processing of incoming events. It extracted information such as the Snort rule ID, alert message, network protocol, source and destination IP addresses, and port numbers when available.

The pipeline also supported different alert formats, including ICMP events without port numbers and alerts that did not contain classification information.

The processed events were successfully indexed in Elasticsearch and could be retrieved using queries in Kibana Dev Tools.

This confirmed that the log collection and processing components were correctly connected and that the alerts contained structured information suitable for further analysis.

## 4. Visualization

A custom Kibana dashboard called **Snort Security Monitoring** was created to make the collected alerts easier to examine.

The dashboard includes six panels covering the total number of alerts, event activity over time, alert types, protocols, priorities, and source IP addresses.

These visualizations made it possible to compare the different test scenarios without manually inspecting individual log entries.

For example, the timeline provided an overview of when alerts were generated, while the protocol and alert type panels helped distinguish the traffic detected during each scenario.

The dashboard also provided a way to check whether the information extracted by the Elasticsearch ingest pipeline was being displayed correctly.

A screenshot of the dashboard is available at `docs/screenshots/snort-security-dashboard.png`. The exported configuration can be found in `dashboards/snort-security-monitoring.ndjson`.

## 5. Limitations

Although the monitoring system worked during the laboratory tests, there are several limitations to consider.

### 5.1 Rule-Based Detection

Snort relies on predefined rules to identify network activity. This approach works well for detecting known patterns, but traffic that does not match any configured rule may go unnoticed.

The rules developed for this project cover only a small number of traffic patterns. They are suitable for demonstrating the monitoring process but do not provide complete protection against network attacks.

### 5.2 False Positives

Some of the detection rules may generate alerts for traffic that is not actually malicious.

For example, the SSH rule identifies repeated SYN packets sent to port 22. A legitimate application making several connection attempts within a short period could potentially trigger the same alert.

The TCP scanning rule also detects individual SYN packets rather than analyzing whether they are part of an actual port scan.

This means that an alert does not necessarily confirm an intrusion attempt. Additional context would be needed to determine whether the detected activity represents a security threat.

### 5.3 Limited Attack Simulation

All tests were performed in a controlled virtual network using traffic generated from Kali Linux.

The five scenarios were useful for verifying the detection rules and the log processing workflow, but they do not represent the full range of techniques used in real network attacks. The ICMP and UDP tests used short bursts of traffic and did not measure service availability or system exhaustion.

The SSH and FTP tests, for example, focused on repeated connection attempts without performing authentication attempts.

The system was also not evaluated under continuous production traffic or high network loads. Its behavior in a larger environment remains untested.

### 5.4 No Automated Notifications

The system collects alerts and makes them available through Kibana, but it does not automatically notify an administrator when suspicious activity is detected.

During testing, the results were checked manually using Snort logs, Elasticsearch queries, and the Kibana dashboard.

Adding automatic notifications would make the system more useful in situations where important events need to be reviewed quickly.

### 5.5 Laboratory-Specific Configuration

The configuration was created for a specific virtual laboratory environment.

It uses local IP addresses, virtual network interfaces, and certificates configured for the machines involved in the project.

Deploying the same system on another network would require adjusting these settings, particularly the network interfaces, Elasticsearch connection details, and certificate configuration.

## 6. Possible Improvements

The current setup provides a working monitoring pipeline, but several improvements could make it more reliable and useful.

One priority would be to develop more specific Snort rules capable of identifying suspicious behavior with greater accuracy. For SSH and FTP, this could involve analyzing authentication failures rather than relying only on repeated TCP connections.

The detection thresholds could also be adjusted to reduce unnecessary alerts. Testing different traffic patterns would help determine whether the current rules generate false positives during normal network activity.

Another improvement would be to introduce automatic notifications for important security events. This would reduce the need to monitor Kibana manually.

The dashboard could also be expanded with additional filters and visualizations to make it easier to investigate individual alerts.

Finally, collecting network traffic over longer periods and testing the system under higher loads would provide a better understanding of its performance and limitations outside the laboratory.

## 7. Conclusion

This project demonstrated how network traffic detection, centralized log collection, and security event visualization can be combined into a single monitoring system.

The five test scenarios produced the expected Snort alerts. The log processing workflow was verified in Elasticsearch, including the structured ICMP flood events. Kibana provided a way to examine the collected information and compare the results.

The main outcome of the project was a functional monitoring pipeline connecting Snort, syslog-ng, Filebeat, Elasticsearch, and Kibana.

While the system is limited to a controlled laboratory environment, it provides a practical foundation for further work on intrusion detection and log management. Future development could focus on more accurate detection rules, additional testing scenarios, and automatic alert notifications.
