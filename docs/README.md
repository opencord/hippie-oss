# Hippie OSS 

This service is intended to be an example implementation of a service that integrates XOS with an external OSS system.
As the name suggests this service will be very welcoming and validate any ONU that is connected to the system.

Peace and Love

> NOTE: This service depends on RCORDSubscriber so make sure that the `rcord-synchronizer` is running

## How to install this service

Make sure you have `xos-core`, `rcord-lite` and `kafka` running.

To install from master:

```bash
helm install -n hippie xos-services/hippie-oss/
```

To install from the local `docker` daemon in minikube:

```bash
helm -f examples/image-tag-candidate.yaml -f examples/imagePullPolicy-IfNotPresent.yaml
```

## Configure this service

To get this service to work, you'll need to push the TOSCA in `samples/oss-service.yaml`