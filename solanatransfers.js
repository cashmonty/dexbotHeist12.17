const axios = require("axios");
const createObjectCsvWriter = require("csv-writer").createObjectCsvWriter;
const fs = require('fs');
const csv = require('csv-parser');
const apikey = "sk_live_5db81dff5c0145b9a1c81088cc6402dd";
const solanafmBaseUrl = "https://api.solana.fm";
const epochFromTimestamp = "1703538136";
const epochToTimestamp = "1704142936";

// Function to read wallet addresses from CSV
function readWalletAddresses(path) {
  return new Promise((resolve, reject) => {
    const walletAddresses = [];
    fs.createReadStream(path)
      .pipe(csv())
      .on('data', (row) => walletAddresses.push(row.Text1))
      .on('end', () => {
        console.log('CSV file successfully processed');
        resolve(walletAddresses);
      })
      .on('error', reject);
  });
}

// Main function to process wallet addresses
const app = async () => {
  try {
    const walletAddresses = await readWalletAddresses('table.csv'); // replace with your CSV file path
    for (let walletAddress of walletAddresses) {
      let totalPages = 1;
      let page = 1;
      do {
        await axios.get(`${solanafmBaseUrl}/v0/accounts/${walletAddress}/transfers`, {
          params: {
            utcFrom: epochFromTimestamp,
            utcTo: epochToTimestamp,
            page: page,
          },
          headers: {
            ApiKey: apikey,
          },
        })
        .then((response) => {
          if (totalPages === 1) {
            console.log("Total pages to index: ", response.data.pagination.totalPages);
            totalPages = response.data.pagination.totalPages;
          }
          console.log("Retrieving data for page: ", page);
          let responseData = response.data.results;

          const csvData = [];
          responseData.forEach((transaction) => {
            transaction.data.forEach((movement) => {
              const csvRow = {
                transactionHash: transaction.transactionHash,
                instructionIndex: movement.instructionIndex,
                innerInstructionIndex: movement.innerInstructionIndex,
                action: movement.action,
                status: movement.status,
                source: movement.source,
                sourceAssociation: movement.sourceAssociation,
                destination: movement.destination,
                destinationAssociation: movement.destinationAssociation,
                token: movement.token,
                amount: movement.amount,
                timestamp: movement.timestamp,
              };

              csvData.push(csvRow);
            });
          });

          const csvWriter = createObjectCsvWriter({
            path: `${walletAddress}.csv`,
            header: [
              { id: "transactionHash", title: "Transaction Hash" },
              // ... other headers
            ],
          });

          csvWriter.writeRecords(csvData)
            .then(() => console.log(`Data written to CSV for ${walletAddress}`))
            .catch((error) => console.log("Error writing to csv file: ", error));
          page++;
        })
        .catch((error) => console.log("Error log: ", error));
      } while (page <= totalPages);
    }
    console.log("Process completed without errors.");
  } catch (error) {
    console.log("Error log: ", error);
  }
};

app();
