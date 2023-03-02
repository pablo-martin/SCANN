<script>
  import {slide} from "svelte/transition";
  let contract = "";
  let error = "";
  let predictions = {};
  let currentPredictionText = "";
  let currentPredictionID = -1;
  const API_URL_ROOT = "http://127.0.0.1:5000";
  
  
  async function predict(){
    currentPredictionText = "";
    currentPredictionID = -1;
    if (! contract) {
      error="Please copy paste code in the text area.";
      return
    }
    const API_URL = API_URL_ROOT + "/predict";
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({contract: contract})
    });
    const data = await response.json();
    // Predictions look like this:
    // {
    //   "DAOGovernor.sol": "contracts/rinkeby/20/204F4EA4453cBD2eB86BD7dA06069A97Bb3406e0_DAOGovernor.sol",
    //   "DxController.sol": "contracts/rinkeby/f2/f2ffF257c2D34e91A555af98d3E57BD41734A1d5_DxController.sol",
    //   "ForeignBridgeErcToNative.sol": "contracts/rinkeby/22/22e0e94708f476221a0b58078f5f0a8b2639abad_ForeignBridgeErcToNative.sol",
    //   "HokkPremium.sol": "contracts/kovan/57/575143A2e6cd88035C90b49CC42BF51dcaE60cB7_HokkPremium.sol",
    //   "MyPFPlandv2.sol": "contracts/rinkeby/e3/E36C73b86A0b6DC822b899CA05fb9C1CEb329D9e_MyPFPlandv2.sol"
    // }
    predictions = data;
  }

  async function displayPrediction(predictionName, index){
    const predictionURL = "https://raw.githubusercontent.com/tintinweb/smart-contract-sanctuary-ethereum/master/" + predictions[predictionName];
    const response = await fetch(predictionURL);
    currentPredictionText = await response.text();
    currentPredictionID = index;
    // Call localhost:5000/clicked?contract_id=number
    const API_URL = API_URL_ROOT + "/click";
    await fetch(API_URL,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({contract_id: index + 1})
      }
    );
  }
  
  async function like(value){
    if (currentPredictionID === -1) {
      return
    }
    const API_URL = API_URL_ROOT + "/like";
    console.log("LIKE", JSON.stringify({contract_id: currentPredictionID + 1, value: value}))
    await fetch(API_URL,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({contract_id: currentPredictionID + 1, value: value})
      }
    );

  }
  

</script>
<svelte:head>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
      body {
        font-family: 'Inter', sans-serif;
        font-size: 16px;
      }
    </style>
</svelte:head>
<!--A mainContainer, grid, 3 columns-->
<div class="mainContainer">
  <!-- The first column  -->
  <div class="container containerFirst">
    <h1>SCANN</h1>
    <h4> (Smart Contract Approximate Nearest Neighbours)</h4>
    <!--A big textarea-->
    <textarea id="text" rows="45" cols="60" placeholder="Copy paste smart contract here." bind:value={contract}></textarea>
    <p class="error">{error}</p>
    <!--A button-->
    <button id="button" on:click={predict}>Find</button>
  </div>
  <!-- The second column  -->
  <div class="container containerSecond">
    <h4 class="title">Results</h4>
    {#each Object.keys(predictions) as predictionName, index}
      <div class="result" on:click={displayPrediction(predictionName, index)}>
        {predictionName}
      </div>
    {/each}
  </div>
  <!-- The third column  -->
  <div class="container containerThird">
    <h4 class="title">Prediction</h4>
    <textarea id="text" disabled="true" rows="45" cols="60" placeholder="" bind:value={currentPredictionText}></textarea>
    {#if currentPredictionID !== -1}
    <div class="likeContainer" transition={slide}>
      <button id="likeButton" on:click={() => like(1)}>Like</button>
      <button id="dislikeButton" on:click={() => like(-1)}>Dislike</button>
    </div>
    {/if}
  </div>
</div>

<style>
  .likeContainer{
    display: flex;
    flex-direction: row;
    justify-content: center;
    width: 100%;
    margin-top: 20px;
    grid-gap: 20px;
  }
  .title{
    margin-bottom: 48px;
  }
  .result{
    cursor: pointer;
    background-color: #4c6faf;
    color: white;
    padding: 15px 32px;
    border-radius: 8px;
    margin: 8px;
  }
  .mainContainer{
    display: grid;
    grid-template-columns: 4fr 1fr 4fr;
    grid-template-rows: 1fr;
    grid-template-areas: "containerFirst containerSecond containerThird";
    height: 100vh;
    width: 95%;
    /* justify items top  */
    align-items: start;
  }
  .container{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }
  .containerSecond{
    align-items: start;
  }
  .error {
    color: red;
  }
  #button{
    background-color: #4c6faf; /* Green */
    border: none;
    color: white;
    padding: 15px 32px;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 16px;
    border-radius: 4px;
  }

  h1{
    font-size: 22px;
    font-weight: 600;
    margin: 10px;
  }
  h4{
    font-size: 18px;
    font-weight: 500;
    margin: 10px;
  }
</style>