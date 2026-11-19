# Filebeat, Elasticsearch and Kibana Integration

## Objective

Forward Snort intrusion detection alerts from the Ubuntu Snort virtual machine to Elasticsearch and visualize them using Kibana.

## Architecture

The implemented pipeline is:

**Kali Linux → Snort → syslog-ng → Filebeat → Elasticsearch → Kibana**

- **Kali Linux:** generates network traffic for testing.
- **Snort:** detects suspicious traffic and generates alerts.
- **syslog-ng:** collects Snort alerts into a log file.
- **Filebeat 9.5.6:** reads the collected alerts and forwards them to Elasticsearch.
- **Elasticsearch 9.5.6:** stores and indexes the received records.
- **Kibana 9.5.6:** allows searching and visualizing the alerts.

## Network Configuration

| Component | IP address |
|---|---|
| Ubuntu Snort (Host-only) | 192.168.56.20 |
| Linux Mint / Elasticsearch (Host-only) | 192.168.56.1 |
| Elasticsearch HTTPS endpoint | https://192.168.56.1:9200 |
| Kibana local interface | http://127.0.0.1:5601 |

## Log Collection

Snort alerts are collected by syslog-ng and written to:

`/var/log/lab5/snort-collected.log`

Filebeat uses the `filestream` input to read this file.

The example configuration is available at:

`configs/filebeat/filebeat.yml`

## Validation Results

The following tests were completed successfully:

1. Snort generated alerts from laboratory network traffic.
2. syslog-ng collected the Snort alerts into the configured log file.
3. Filebeat successfully connected to Elasticsearch using HTTPS and authentication.
4. Elasticsearch indexed **1,102 documents** at the time of validation.
5. Kibana Discover displayed the indexed documents.
6. Kibana searches returned results for:
   - `message: "Someone is pinging"`
   - `message: "BAD-TRAFFIC"`

These results confirm that the end-to-end log collection and visualization pipeline is operational.

## Security Considerations

Elasticsearch authentication and HTTPS are enabled.

Filebeat credentials are stored in the Filebeat Keystore instead of the YAML configuration.

The Elasticsearch CA certificate is installed locally on the Ubuntu Snort virtual machine and is not included in the repository.

**Known limitation:** Filebeat temporarily uses `ssl.verification_mode: certificate` because the Elasticsearch HTTPS certificate does not include the Host-only IP address `192.168.56.1`.

This mode validates the certificate chain but skips hostname/IP verification.

**Future improvement:** issue a new HTTPS certificate containing `192.168.56.1` and restore `ssl.verification_mode: full`.

## Conclusion

The laboratory successfully integrates network intrusion detection, centralized log collection, secure log transport, indexing and visualization using Snort, syslog-ng, Filebeat, Elasticsearch and Kibana.
