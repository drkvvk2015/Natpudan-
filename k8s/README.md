# Kubernetes Deployment Guide for Natpudan AI

Quick reference for deploying to Kubernetes clusters (AWS EKS, Azure AKS, Google GKE, or local minikube).

## Prerequisites

```bash
kubectl version --client
helm version
```

## Quick Deploy

```bash
# 1. Update secrets in k8s/00-namespace-and-config.yaml
# 2. Update image URLs in k8s/*.yaml (replace YOUR_USERNAME)

# 3. Apply all manifests
kubectl apply -f k8s/

# 4. Check status
kubectl get pods -n natpudan
kubectl get services -n natpudan

# 5. Port forward for testing
kubectl port-forward -n natpudan svc/frontend 3000:3000
kubectl port-forward -n natpudan svc/backend 8000:8000
```

## Production Setup

```bash
# Install nginx ingress controller
helm install ingress-nginx ingress-nginx/ingress-nginx

# Install cert-manager for SSL
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Deploy application
kubectl apply -f k8s/

# Monitor rollout
kubectl rollout status deployment/backend -n natpudan
kubectl rollout status deployment/frontend -n natpudan
```

## Scaling

```bash
# Scale backend
kubectl scale deployment backend --replicas=5 -n natpudan

# Scale frontend
kubectl scale deployment frontend --replicas=3 -n natpudan

# Auto-scaling
kubectl autoscale deployment backend --cpu-percent=70 --min=2 --max=10 -n natpudan
```

## Logs

```bash
kubectl logs -f deployment/backend -n natpudan
kubectl logs -f deployment/frontend -n natpudan
kubectl logs -f deployment/celery -n natpudan
```
