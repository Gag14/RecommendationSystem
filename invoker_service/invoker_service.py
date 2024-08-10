# invoker_service.py
import os
import json
import redis
import logging
import requests
from cachetools import TTLCache, cached
from flask import Flask, jsonify, request
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level to DEBUG, INFO, WARNING, ERROR, or CRITICAL as needed
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),  # Logs will be written to this file
        logging.StreamHandler()  # Logs will also be output to the console
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Local cache with TTL of 10 seconds, limited to 3 keys
local_cache = TTLCache(maxsize=3, ttl=10)

# Redis cache
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')  # This should match the service name in docker-compose
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

redis_cache = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def get_recommendation(viewerid):
    
    # Check local cache
    if viewerid in local_cache:
        print(local_cache)
        logger.debug("local worked")
        return local_cache[viewerid]
    try:
        redis_cache.ping()
        logger.info("Connected to Redis!")
    except redis.exceptions.ConnectionError as e:
        logger.warning(f"Redis connection error: {e}")
        
    
    # Check Redis cache
    cached_value = redis_cache.get(viewerid)

    if cached_value:
     
        recommendation = json.loads(cached_value)
        # Set the retrieved value in the local cache
        local_cache[viewerid] = recommendation
        return recommendation
    
    # Run the cascade if no cache exists
    recommendation = runcascade(viewerid)
    
    
    # Cache the result
    local_cache[viewerid] = recommendation
    print(local_cache[viewerid])
    # redis_cache.set(viewerid, recommendation)
    redis_cache.set(viewerid, json.dumps(recommendation))

    logger.info("cach set")
    
    return recommendation

def runcascade(viewerid):
    # Define model names for parallel calls
    model_names = [f"Model{i}" for i in range(1, 6)]
    # Function to call the generator service
    def call_generator(modelname):
        print("call")
        response = requests.post('http://generator_service:5000/generate', json={
            "modelname": modelname,
            "viewerid": viewerid
        })
        return response.json()
    # Make 5 parallel calls to the generator service
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(call_generator, model_names))
    # Merge the results into a single response
    merged_result = {"viewerid": viewerid, "recommendations": results}
    
    return merged_result

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    logger.debug(data)
    viewerid = data.get('viewerid')
    
    if not viewerid:
        return jsonify({"error": "Missing viewerid"}), 400
    
    recommendation = get_recommendation(viewerid)
    
    return jsonify(recommendation), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
