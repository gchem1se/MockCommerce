imgInput = document.querySelector("#img")
imgInput.addEventListener("change", () => {
    const [file] = imgInput.files
    if (file) {
        document.querySelector("#productImg").src = URL.createObjectURL(file)
    }
});

const date = new Date();
let currentDate = ('0' + date.getDate()).slice(-2) + '/' + ('0' + (date.getMonth()+1)).slice(-2) + '/' + date.getFullYear();
document.querySelector("#lastUpdateDate").value = currentDate;
