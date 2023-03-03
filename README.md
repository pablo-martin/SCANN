# ⟠ SCANN ⟠ 
### Smart Contract Approximate Nearest Neighbours

SCANN is a smart contract similarity search service. Given a smart contract, it searches from a DB with 750K+ [open-sourced](https://github.com/tintinweb/smart-contract-sanctuary-ethereum) contracts and retrieves the 5 most similar contracts.

## Installation ⚡️ 

Requirements are docker and npm (version `9.5.1` tested). Open up a terminal, and in the desired location run:
```bash
git clone https://github.com/pablo-martin/SCANN.git
cd SCANN/
bash build_frontend.sh # additionally installs pnmp
```
It will prompt you 3 times, the first select "Skeleton Project", the other 2 just hit enter on the first option. Continue:

```bash
docker build -t scann_docker . # go make a coffee ~5 mins
docker run -p 5000:5000 -d scann_docker
cd scann_front/
pnpm run dev
```

You will get output similar to this:
```bash
  VITE v4.1.4  ready in 1181 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h to show help
```
Open a browser and go to localhost with whatever port number is shown. When you're done don't forget to stop your container since it's ~4.5GB 
```bash
docker container ls # to find the name of your container
docker container stop <container-name>
```

## ML - Smart Contract Search

Finding similar smart contracts is a search problem, which is classically split into a retrieval and a ranking phase. In this approach, SCANN uses "Embedding Based Retrieval" (EBR).  which first encodes a smart contract as fixed dimension vector of numbers. SCANN takes the following approach:

### Embeddings
- Take the smart contract and encode it as a fixed dimension vector representing semantic meaning. SCANN uses [SmartEmbed](https://github.com/pablo-martin/SmartEmbed) (forked from [here](https://github.com/beyondacm/SmartEmbed)), which first parses the contract using [ANTLR4](https://www.antlr.org/)and then creates a traditional embedding via ngram models from the parsed contract.  
### Retrieval
- SCANN uses approximate nearest neighbours for retrieving top 5 recommendations. Chose to use Spotify's [ANNOY](https://github.com/spotify/annoy) library for implementation
- Also explored [FAISS](https://github.com/facebookresearch/faiss) which is a similar implementation from Facebook FAIR. However, it needed some BLAS C++ libraries that may not have worked on a Docker image
- Initially thought about using ElasticSearch, which also offers [ANN](https://www.elastic.co/blog/introducing-approximate-nearest-neighbor-search-in-elasticsearch-8-0) capabilities and is a standard in the industry. However, again I thought it may not run well in a container or will have forced me to use multiple containers and docker-compose

### Ranking
- SCANN ranks suggestions by highest weighted cosine similarity to the input embedding. The weights come from a transformed function of "likes" and "dislikes" from the users. For more detail, look at the online learning section below.

### Online Learning
The smart contract repository we used had many contracts (+1M contract, although 750K+ unique ones), but it did not have any labels regarding similarity. In other words, there was no way to know which contracts are similar to what other contracts. Having a solidity developer look through the half a trillion combinations is unfeasible. So how do we know that are recommendations are good? For this reason, we implemented a simple online learning system based on "likes" and "dislikes".
- when a user clicks on a recommendation, it has the ability to either give it a "like" or "dislike", signaling whether the suggestion was good or not
- that relationship is stored by the system, and when that contract is searched again, the cosine similarity is weighed by a the like score passed through the following sigmoid variation:  
$$\frac{2} {1 + e^-\Theta^Tx }$$ 
<p align="center">
  <img src="double_sigmoid.png" width="350" title="hover text">
</p>

- if there is no like history, the cosine similarity is multiplied by 1, so it's the same  
- 1 like will multiply it by 1.44 (a strong increase) . 
- since traffic will probably be low, likes/dislikes are taken as strong signals to push the recommendations significantly 

### Monitoring



## System Design

### ML Inference
There are 3 components in the ML inference component: the embedding, the retrieval and the ranker. The input smart contract is passed sequentially through the 3 components. 

### API
- I designed a simple API to serve the inference predictions using flask. 
- There is a user session object that is created that keeps tracks of all the likes/clicks of the user and stores them in the DB when a user searches for a new contract.
- Ideally it would store the user session when the browser gets closed as well, but it could be added in a future iteration
### DB
- A sqlite3 database stores 2 tables: all the user session data, and all info related to smart contracts.
- `session_data`: table is consumed downstream by the model monitoring service in the batch processes. it keeps track of quality of predictions, latency.
- `smart_contracts`: table stores unique identifiers for smart contracts, a hashed representation of their embedding, and in future iterations the embedding itself and potentially the actual text of the code to be able to serve it. I chose not to include those because the DB is currently stored on file, and managing a more capable (perhaps distribued DB like DynamoDB) in a cloud service would be a good improvement, depending on the intended use.
### Docker
The backend is deployed in a Docker container. This includes the ML inference system, the flask API, and the sqlite3 DB. There are some quirks about this container:
- the embedding library requires a Java Runtime Environment (JRE) for the grammar parsing ANTLR4 package
- for this reason, I chose a Java based image, and extended it to have Python
- in a more mature system, perhaps running these services in different containers through [Docker Compose](https://docs.docker.com/compose/) could be a more modular approach
### FrontEnd
The front-end is built using the [Svelte](https://svelte.dev/docs) toolkit. By following this tutorial I was able to quickly spin up a usable front-end to display my tool. 
### Batch Processes

