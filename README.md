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


### Token Generation
- **Endpoint**: `/token`
- **Method**: POST
- **Description**: Generates a token for user authentication.
- **Request Body**: `{"user_id": "uuid"}`
- **Response**: `{"access_token": "token", "token_type": "bearer"}`
- **Errors**: 400 (User not found), 401 (Invalid credentials)

### Save Project
- **Endpoint**: `/saveProject`
- **Method**: POST
- **Description**: Saves or updates a project in the database.
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**: `{"project_dict": {}, "template": boolean}`
- **Response**: 200 (Project saved successfully)
- **Errors**: 404 (Project not found), 500 (Internal server error)

### Get Projects
- **Endpoint**: `/getProjects`
- **Method**: GET
- **Description**: Retrieves all projects associated with the authenticated user.
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `{"projects": [{"id": "uuid", "name": "Project Name"}]}`
- **Errors**: 500 (Internal server error)

### Get Specific Project
- **Endpoint**: `/getProject`
- **Method**: GET
- **Description**: Fetches a specific project by its ID.
- **Query Parameters**: `project_id`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `{"project": {}}`
- **Errors**: 404 (Project not found), 500 (Internal server error)

### Share Project
- **Endpoint**: `/shareProject`
- **Method**: POST
- **Description**: Shares a project with another user.
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**: `{"user_id": "uuid", "project_id": "uuid"}`
- **Response**: `{"message": "Project shared successfully"}`
- **Errors**: 404 (User or project not found), 500 (Internal server error)

### Update Project Name
- **Endpoint**: `/updateProjectName`
- **Method**: PUT
- **Description**: Updates the name of a project.
- **Query Parameters**: `project_id`, `new_name`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `{"message": "Project name updated successfully"}`
- **Errors**: 404 (Project not found), 500 (Internal server error)

### Delete Project
- **Endpoint**: `/deleteProject`
- **Method**: DELETE
- **Description**: Deletes a project by ID.
- **Query Parameters**: `project_id`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `{"message": "Project deleted successfully"}`
- **Errors**: 404 (Project not found), 500 (Internal server error)

### Add Configuration
- **Endpoint**: `/addConfiguration`
- **Method**: POST
- **Description**: Adds a new configuration to a project.
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**: `{"project_id": "uuid", "config_input": {"project_json": {}, "id_feature_model": "uuid", "config_name": "string"}}`
- **Response**: `{"transactionId": "1", "message": "Configuration added successfully"}`
- **Errors**: 404 (Project not found), 500 (Internal server error)

### Delete Configuration
- **Endpoint**: `/deleteConfiguration`
- **Method**: DELETE
- **Description**: Deletes a configuration from a project.
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**: `{"project_id": "uuid", "model_id": "uuid", "configuration_id": "uuid"}`
- **Response**: `{"transactionId": "1", "message": "Configuration deleted successfully"}`
- **Errors**: 404 (Configuration or project not found), 500 (Internal server error)

### Get Configuration
- **Endpoint**: `/getAllConfigurations`
- **Method**: GET
- **Description**: Retrieves a specific configuration by ID from a project.
- **Query Parameters**: `project_id`: `uuid`,`model_id`: `uuid`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `{"transactionId": "1", "message": "Configuration retrieved successfully", "data": {}}`
- **Errors**: 404 (Configuration or project not found), 500 (Internal server error)

### Get Configuration
- **Endpoint**: `/getConfiguration`
- **Method**: GET
- **Description**: Retrieves a specific configuration by ID from a project.
- **Query Parameters**: `project_id`: `uuid`,`configuration_id`: `uuid`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `{"transactionId": "1", "message": "Configuration retrieved successfully", "data": {}}`
- **Errors**: 404 (Configuration or project not found), 500 (Internal server error)

### Apply Configuration
- **Endpoint**: `/applyConfiguration`
- **Method**: POST
- **Description**: Applies a specified configuration to a project.
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**: `{"project_id": "uuid", "configuration_id": "uuid"}`
- **Response**: `{"transactionId": "1", "message": "Configuration applied successfully", "data": {}}`
- **Errors**: 404 (Configuration or project not found), 500 (Internal server error)
