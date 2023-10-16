const buttons = document.querySelectorAll("[id^=\"delete\"]")
buttons.forEach(btn => 
    btn.addEventListener("click", e => {
        let pid = e.currentTarget.dataset.productid;
        
        let updateButton = document.querySelector("#update_"+pid);
        updateButton.classList.add("hidden");
        let confirmButton = document.querySelector("#confirm_"+pid);
        confirmButton.classList.remove("hidden");
        let discardButton = document.querySelector("#discard_"+pid);
        discardButton.classList.remove("hidden");
        
        confirmButton.addEventListener("click", e => {
            e.currentTarget.classList.add("hidden");    
            discardButton.classList.add("hidden");    
            updateButton.classList.remove("hidden");
        })

        discardButton.addEventListener("click", e => {
            e.currentTarget.classList.add("hidden");    
            confirmButton.classList.add("hidden"); 
            updateButton.classList.remove("hidden");   
        })
    }));