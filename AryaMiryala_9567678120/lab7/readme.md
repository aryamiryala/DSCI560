## Project Overview

This project transforms iPhones into mobile IoT devices using the OwnTracks application and connects them to a cloud-hosted IoT hub deployed on Amazon Web Services (AWS).

Telemetry data including:

- Latitude (`lat`)
- Longitude (`lon`)
- Battery Percentage (`batt`)

is transmitted via HTTP to a ThingsBoard Community Edition instance running on an Ubuntu EC2 server.

The system implements real-time monitoring and an automated low-battery alert system using the ThingsBoard Rule Engine.

---
## AWS Setup

### Launch EC2 Instance

- Ubuntu 22.04 LTS
- Instance type: t3.medium 

---

### Connect via SSH

```bash
chmod 400 lab7_560.pem
ssh -i lab7_560.pem ubuntu@<EC2_PUBLIC_IP>
```

Then start ThingsBoard
``` bash
sudo service thingsboard start
```

Open the browser and navigate to
http://<EC2_PUBLIC_IP>:8080

Login using 
Email: tenant@thingsboard.org
Password: tenant