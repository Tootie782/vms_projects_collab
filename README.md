<h1 align="center">
  Variamos Projects Microservice
</h1>

## Description
```
Microservice that allows to get Variamos projects.
```

## Building of the project
```
docker build --no-cache --progress plain -t vms_projects .\ 
```

### Project deployment
```
docker run -p 10000:10000 --rm --name vms_projects -t vms_projects
```
# API Documentation

This document outlines the available endpoints and their usage for the project's API.

---

### Generate Token
Get a token for a user.

Parameter | Value
-- | --
Verb | `POST`
URL | `/token`
Payload | ```{"user_id": "«user id»"}```
Response | ```{"access_token": "«token value»", "token_type": "bearer"}```
Exception response | `Http response code 40x, body: {message:«message error»}`

---

### Save Project
Save the user's project.

Parameter | Value
-- | --
Verb | `POST`
URL | `/saveProject`
Authentication | `Bearer`
Payload | ```{"project": «project data»}```
Response | ```{Http response 200 OK}```
Exception response | `Http response code 40x, body: {message:«message error»}`

---

### Get Projects
Get the user's projects.

Parameter | Value
-- | --
Verb | `GET`
URL | `/getProjects`
Authentication | `Bearer`
Response | ```{ "projects": [ { "id": "1", "name": "Project 1" }, { "id": "2", "name": "Project 2" }, ...] }```
Exception response | `Http response code 40x, body: {message:«message error»}`

---

### Get Project
Get a specific project by ID.

Parameter | Value
-- | --
Verb | `GET`
URL | `/getProject?project_id=«project id»`
Authentication | `Bearer`
Response | ```{ "project": «project data»}```
Exception response | `Http response code 40x, body: {message:«message error»}`

---

### Share Project
Share a project with another user.

Parameter | Value
-- | --
Verb | `POST`
URL | `/shareProject`
Authentication | `Bearer`
Payload | ```{ "project_id": "«project id»", "user_id": "«user id»" }```
Response | ```{ Http response 200, body: {"Project shared successfully"}}```
Exception response | `Http response code 40x, body: {message:«message error»}`

---

### Get Users of Project
Get users associated with a specific project.

Parameter | Value
-- | --
Verb | `GET`
URL | `/usersProject?project_id=«project id»`
Authentication | `Bearer`
Response | ```{ "users": [ { "id": "«user id»", "username" : "«username»", "name": "«name»", email : "«user mail»"}, ...] }```
Exception response | `Http response code 40x, body: {message:«message error»}`

---

### Find User by Email
Find a user based on their email address.

Parameter | Value
-- | --
Verb | `GET`
URL | `/findUser?user_mail=«user email»`
Authentication | `Bearer`
Response | ```{ "id": "«user id»", "name": "«name»", "user": "«user name»", "email": "«user email»" }```
Exception response | `Http response code 40x, body: {message:«message error»}`
---

### Add Configuration
Add a configuration to a project.

Parameter |	Value
-- | --
Verb |	`POST`
URL |	`/addConfiguration`
Authentication |	`Bearer`
Payload |	```{ "project_id": "«project id»", "config_input": { "project_json": "«project data»", "id_feature_model": "«feature model id»", "config_name": "«configuration name»" } }```
Response |	```{ "transactionId": "1", "message": "Project updated successfully" }```
Exception response |	`HTTP response code 404/500, body: { "message": "«error message»" }`

---

### Delete Configuration
Delete a specific configuration from a project.

Parameter |	Value
-- | --
Verb |	`DELETE`
URL |	`/deleteConfiguration`
Authentication |	`Bearer`
Payload | ```{ "project_id": "«project id»", "configuration_id": "«configuration id»" }```
Response | ```{ "transactionId": "1", "message": "Configuration deleted successfully" }```
Exception response |	`HTTP response code 404/500, body: { "message": "«error message»" }`
---

### Get Configuration
Get a specific configuration by ID from a project.

Parameter |	Value
-- | --
Verb | `GET`
URL |	`/getConfiguration?project_id=«project id»&configuration_id=«configuration id»`
Authentication |	`Bearer`
Response |	```{ "transactionId": "1", "message": "Configuration found", "data": {«configuration data»} }```
Exception response |	`HTTP response code 404/500, body: { "message": "«error message»" }`

---


### Apply Configuration
Apply a configuration to a project model.

Parameter |	Value
-- | --
Verb |`POST`
URL | 	`/applyConfiguration`
Authentication |	`Bearer`
Payload |	```{ "model_json": {«model data»}, "configuration": {«configuration data»} }```
Response |	```{ "transactionId": "1", "message": "Configuration applied successfully", "data": {«updated model data»} }```
Exception response |	`HTTP response code 500, body: { "message": "«error message»" }`

---
