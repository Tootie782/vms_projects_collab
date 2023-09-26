<h1 align="center">
  Variamos Projects Microservice
</h1>

## Description
```
Microservice that allows to get Variamos projects.
```

## Construcción del proyecto
```
docker build --no-cache --progress plain -t vms_projects .\ 
```

### Ejecución del proyecto
```
docker run -p 10000:10000 --rm --name vms_projects -t vms_projects
```
