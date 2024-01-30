#!/bin/bash

kubectl apply -f ma_bdd_statefulset.yaml
kubectl apply -f ma_bdd_service.yaml
kubectl apply -f mon_api_secret.yaml
kubectl apply -f mon_api_deployment.yaml
kubectl apply -f mon_api_service.yaml
kubectl apply -f mon_ingress.yaml
