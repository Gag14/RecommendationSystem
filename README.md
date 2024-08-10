# Recommendation System

## Overview

This project is a recommendation system implemented using Python and Docker. The system consists of two main services:
- **Generator Service**: The service that generates recommendations.
        1. Single POST method that takes two parameters: model name and
        viewerid. Each run of the service generates a random number and returns
        a result of the type: {“reason”: **<MODELNAME>**, “result”:
        **<RANDOMNUMBER>**}

- **Invoker Service**: The service that returns recommendations.
        1. Method recommend() that checks the cache for the given user. If there is
        no data in the cache, it calls the runcascade() function. The merged
        result of the cascade runs is saved in the cache and returned in the
        response;
        2. Method runcascade() makes 5 parallel calls to the GENERATOR service
        with different <MODELNAME> parameters;

There are two levels of caching: local with a TTL of 10 seconds (limited to 3 keys) and
Redis. If there is no data for the given user in the local cache, take the cache from
Redis.
## Getting Started

To get the project up and running locally, follow these steps:

### Prerequisites

- Docker
- Docker Compose
- Python 3.x (for local development)
- Redis (handled by Docker Compose)

### Setup

1. **Clone the repository:**

   git clone https://github.com/Gag14/RecommendationSystem.git
   cd RecommendationSystem

2. **Build and run the Docker containers:**
    docker-compose up --build
This will start the Redis server, the Generator Service, and the Invoker Service.

Access the services:

 - Generator Service: http://localhost:5000
 - Invoker Service: http://localhost:5001

**Usage**
To test the recommendation system, you can use Postman or any other HTTP client:

- Endpoint: POST /recommend on http://localhost:5001
- Request Body: JSON with the required parameters (e.g., {"viewerid": "12345"})
