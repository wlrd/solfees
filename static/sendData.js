window.addEventListener('load', async () => {
    const isPhantomInstalled = window.solana && window.solana.isPhantom

    if (isPhantomInstalled) {
        window.solana.connect();
        window.solana.on("connect", () => {
            var address = window.solana.publicKey.toString();
            console.log('connected! address is ' + address);

            var xhttp = new XMLHttpRequest();
            xhttp.onreadystatechange = function () {
                if (this.readyState == 4 && this.status == 200) {
                    var result = JSON.parse(this.responseText);

                    if (result['failed']){
                        console.log('Something went wrong')
                        $('body').html('<p id="oops">Something went wrong!</strong>')
                    }

                    if (result['num_transactions'] == 0){
                        $('body').html('<p id="oops">You have no transactions, time to start using SOL! Time to buy a <a href="https://market.solanamonkey.business/"> monke</a>.</p>')
                        return;
                    }

                    document.getElementById("sol_fees").innerHTML = result['sol_fees']
                    document.getElementById("sol_fees_usd").innerHTML = '$' + result['sol_fees_usd']

                    document.getElementById("transaction_count").innerHTML = result['num_transactions']
                    document.getElementById("avg_transaction").innerHTML = '$' + result['avg_transaction_cost_usd'] 

                    document.getElementById("fail_count").innerHTML = result['fail_count']
                    document.getElementById("fail_cost_usd").innerHTML = '$' + result['fail_cost_usd']

                    document.getElementById("eth_avg_cost").innerHTML = '$41.04'
                }
            };
    
            xhttp.open("GET", "getfees?a=" + address, true);
            xhttp.send(address);
        })
    } else {
        console.log('Sign into Phantom!')
        $('body').html('<p id="oops">Sign into <strong><a href="https://phantom.app/">Phantom</a> </strong> to find out how much in fees you\'ve paid on Solana!</p>')
        return;
    }
});