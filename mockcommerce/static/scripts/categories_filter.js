const links = document.querySelectorAll(".mySidebarEntry")
links.forEach(link => 
  link.addEventListener("click", e => {
    document.querySelector(".mySidebarEntry.selected").classList.remove("selected");    
    link.classList.add("selected");

    const filter = e.target.dataset.categoryid;

    const products = document.querySelectorAll(".col")
    
    products.forEach(product => {
      product.classList.remove("hidden");
      if (filter != "0" && product.dataset.categoryid != filter){
        product.classList.add("hidden");
      }
    })
  }));

const dropdown = document.querySelector(".myDropdown");
dropdown.addEventListener("change", () => {
  sel = dropdown.options[dropdown.selectedIndex];
  const filter = sel.value;
  products = document.querySelectorAll(".col");
  products.forEach(product => {
    product.classList.remove("hidden");
    if (filter != "0" && product.dataset.categoryid != filter){
      product.classList.add("hidden");
    }
  })});
