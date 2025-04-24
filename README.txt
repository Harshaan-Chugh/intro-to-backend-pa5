Name: Harshaan Chugh
NetID: hsc53

Challenges Attempted: None
Working Endpoint: GET /api/courses/
Your Docker Hub Repository Link: https://hub.docker.com/layers/harshaan999/pa5/latest/images/sha256:98ab00defb4cc0b36c3438fabd8288675a9ffe0d2b4fa0f2f787312052722d6f?uuid=3FB130F7-0B0A-49E1-B1FA-BE4AF90E7A8F

Questions:
Explain the concept of containerization in your own words.
Containerization is a method that packages an application into a single unit
so that it may run smoothly across different environments.

What is the difference between a Docker image and a Docker container?
A docker image is a read-only blueprint for creating containers, while a Docker
container is an instance of the image.

What is the command to list all Docker images?
docker images

What is the command to list all Docker containers?
docker ps 

What is a Docker tag and what is it used for?
A docker tag is a label that helps identify a specific version of the Docker image,
helping with versioning.

What is Docker Hub and what is it used for?
Docker hub is a cloud-based registry for sharing and storing Docker images.

What is Docker compose used for?
Docker compose helps us use a YAML configuration file to more smoothly run 
docker containers without going through the effort of writing bulky commands 
in the terminal. It also helps define multi-container Docker apps.

What is the difference between the RUN and CMD commands?
RUN executes instructions during the image building process.
CMD specifies the default command to run when a container starts.
