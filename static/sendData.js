function connectWallet() {    
    window.solana.connect();
}

function getAddress(){
    var addy = window.solana.publicKey.toString();
    console.log('wallet addy is ' + addy);

    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            document.getElementById("demo").innerHTML = this.responseText;
       }
    };

    xhttp.open("GET", "getfees?addy=" +addy , true);
    xhttp.send(addy);    
}