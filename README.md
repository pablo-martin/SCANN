# ⟠ SCANN ⟠ 
### Smart Contract Approximate Nearest Neighbours

SCANN is a smart contract similarity search service. Given a smart contract, it searches from a DB with 750K+ [open-sourced](https://github.com/tintinweb/smart-contract-sanctuary-ethereum) contracts and retrieves the 5 most similar contracts.

## Installation ⚡️ 

Requirements are docker and npm (version `9.5.1` tested). Open up a terminal, and in the desired location run:
```bash
git clone https://github.com/pablo-martin/SCANN.git
cd SCANN/
bash build_frontend.sh # additionally installs pnmp
docker build -t scann_docker . # go make a coffee ~5 mins
# once image is built
docker run -p 5000:5000 -d scann_docker

```
On a separate terminal start the front-end:
```bash
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
Open a browser and go to localhost with whatever port number is shown.


## Smart Contract Search

Finding similar smart contracts is a search problem, which is classically split into a retrieval and a ranking phase. In this approach, we are trying Embedding Based Retrieval (EBR) which first encodes a smart contract as fixed dimension vector of numbers. SCANN takes the following approach:

### Embeddings
- Create embedding using [SmartEmbed](https://github.com/pablo-martin/SmartEmbed) (we forked this from [here](https://github.com/beyondacm/SmartEmbed)). It uses [ANTLR4](https://www.antlr.org/) parsing and creates ngram models from the parsed contract.  

### Retrieval
- It uses approximate nearest neighbours for retrieving top 5 recommendations. Chose to use Spotify's [ANNOY](https://github.com/spotify/annoy) library for implementation

### Ranking
- We rank by highest weighted cosine similarity to the input embedding. The weights come from a transformed function of "likes" and "dislikes" from the users. For more detail, look at the online learning section below.

## System Design

### ML Inference
### API
### DB
### Docker
### FrontEnd
### Batch Processes
