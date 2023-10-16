const date = new Date();
let currentDate = ('0' + date.getDate()).slice(-2) + '/' + ('0' + (date.getMonth()+1)).slice(-2) + '/' + date.getFullYear();
document.querySelector("#purchaseDate").value = currentDate;

let orders = {}
document.querySelectorAll(".product").forEach(prod => {
    const prodID = prod.dataset.productid
    orders[prodID] = {
        'quantity': parseInt(document.querySelector("#quantity_"+prodID).value), 
        'purchasePrice': parseFloat(document.querySelector("#price_"+prodID).dataset.value)
        // ^^ this will be validated before executing the order.
    }
});
document.querySelector("#orders").value = JSON.stringify(orders);

const quantityInputs = document.querySelectorAll("[id^=\"quantity_\"]");

quantityInputs.forEach(i => {
    i.addEventListener("change", () => {
        const totalPrice = document.querySelector("#totalPrice");
        let newTotal = 0;
        document.querySelectorAll("[id^=\"price_\"]").forEach(price => {
            const prodID = price.dataset.productid;
            newTotal = newTotal + price.dataset.value * document.querySelector("#quantity_"+prodID).value;
        })
        totalPrice.textContent = "€ "+newTotal.toFixed(2).toString().replace(".", ",");

        let orders = {}
        document.querySelectorAll(".product").forEach(prod => {
            const prodID = prod.dataset.productid
            orders[prodID] = {
                'quantity': parseInt(document.querySelector("#quantity_"+prodID).value), 
                'purchasePrice': parseFloat(document.querySelector("#price_"+prodID).dataset.value)
                // ^^ this will be validated before executing the order.
            }
        });
        document.querySelector("#orders").value = JSON.stringify(orders);
    })
});



