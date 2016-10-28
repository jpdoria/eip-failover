# About

[![forthebadge](http://forthebadge.com/images/badges/built-with-love.svg)](http://forthebadge.com)
[![forthebadge](http://forthebadge.com/images/badges/powered-by-oxygen.svg)](http://forthebadge.com)
[![forthebadge](http://forthebadge.com/images/badges/fuck-it-ship-it.svg)](http://forthebadge.com)

A basic AWS Lambda function, when triggered by SNS if CPU utilization is >= 65%, automatically disassociates Elastic IP from unhealthy EC2 instance, then associates it to a healthy EC2 instance.

# Use Case
The client has two proxy instances that are not using Auto Scaling and they need to transfer the Elastic IP from one instance to another when the CPU utilization is >= 65%.

# Setup
* 1 Proxy instance (primary) using an Elastic IP
* 1 Proxy instance (secondary)
* 1 SNS topic for CloudWatch Alarms
* 2 CloudWatch alarms (CPUUtilization > 65%) for these instances

# Diagram
![aws-eip-failover-diagram](https://cdn.lazyadm.in/eip-failover.png)