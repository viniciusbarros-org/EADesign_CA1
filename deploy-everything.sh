kubectl apply -k ./async/redis/ 
kubectl apply -f ./async/deployment.yaml  
kubectl apply -f ./async/service.yaml
kubectl apply -f ./sync/deployment.yaml  
kubectl apply -f ./sync/service.yaml