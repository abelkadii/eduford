let listProductHTML = document.querySelector('.listProduct');
let listCartHTML = document.querySelector('.listCart');
let iconCart = document.querySelector('.icon-cart');
let iconCartSpan = document.querySelector('.icon-cart span');
let body = document.querySelector('body');
let closeCart = document.querySelector('.close');
let checkout = document.querySelector("#checkout")
// let checkout = document.querySelector("#checkout")
let products = [];
let cart = [];
let total_price = 0;

let currency = "USD"

const currencyMultipliers = {
    "USD": 1,
    "KES": 127.20,
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Search for the CSRF cookie name
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
  }
iconCart.addEventListener('click', () => {
    body.classList.toggle('showCart');
})
closeCart.addEventListener('click', e => {
    e.preventDefault()
    body.classList.toggle('showCart');
})

    const addDataToHTML = () => {
    // remove datas default from HTML
    listProductHTML.innerHTML=""
        // add new datas
        if(products.length > 0) // if has data
        {
            products.forEach(product => {
                let newProduct = document.createElement('div');
                newProduct.dataset.id = product.id;
                newProduct.classList.add('item');
                newProduct.innerHTML = 
                `<img src="${product.image}" alt="">
                <h2>${product.name}</h2>
                <div class="price">${currency} ${product.price * currencyMultipliers[currency]}</div>
                <button class="addCart">Add To Cart</button>`;
                listProductHTML.appendChild(newProduct);
            });
        }
    }
    listProductHTML.addEventListener('click', (event) => {
        let positionClick = event.target;
        if(positionClick.classList.contains('addCart')){
            let id_product = positionClick.parentElement.dataset.id;
            addToCart(id_product);
        }
    })
const addToCart = (product_id) => {
    let positionThisProductInCart = cart.findIndex((value) => value.product_id == product_id);
    let product = products.filter(p=>p.id==product_id)[0]
    total_price+=product.price*currencyMultipliers[currency]
    if(cart.length <= 0){
        cart = [{
            product_id: product_id,
            quantity: 1,
            price: product.price*currencyMultipliers[currency]
        }];
    }else if(positionThisProductInCart < 0){
        cart.push({
            product_id: product_id,
            quantity: 1,
            price: product.price*currencyMultipliers[currency]
        });
    }else{
        cart[positionThisProductInCart].quantity = cart[positionThisProductInCart].quantity + 1;
    }
    addCartToHTML();
    addCartToMemory();
}
const addCartToMemory = () => {
    localStorage.setItem('cart', JSON.stringify(cart));
}
const addCartToHTML = () => {
    let recalcuated_totalPrice = 0
    listCartHTML.innerHTML = '';
    let totalQuantity = 0;
    if(cart.length > 0){
        cart.forEach(item => {
            totalQuantity = totalQuantity +  item.quantity;
            let newItem = document.createElement('div');
            newItem.classList.add('item');
            newItem.dataset.id = item.product_id;
            
            let positionProduct = products.findIndex((value) => value.id == item.product_id);
            console.log(products, item)
            let info = products[positionProduct];
            recalcuated_totalPrice+=info.price * item.quantity *currencyMultipliers[currency]
            listCartHTML.appendChild(newItem);
            newItem.innerHTML = `
            <div class="image">
                    <img src="${info.image}">
                </div>
                <div class="name">
                ${info.name}
                </div>
                <div class="totalPrice">${currency} ${info.price * item.quantity *currencyMultipliers[currency]}</div>
                <div class="quantity">
                    <span class="minus"><</span>
                    <span>${item.quantity}</span>
                    <span class="plus">></span>
                </div>
            `;
        })
    }
    total_price = recalcuated_totalPrice
    iconCartSpan.innerText = totalQuantity;
    let totalPrice = document.getElementById("totalPrice")
    totalPrice.innerText = `Total: ${currency} ${total_price}`;
}

listCartHTML.addEventListener('click', (event) => {
    let positionClick = event.target;
    if(positionClick.classList.contains('minus') || positionClick.classList.contains('plus')){
        let product_id = positionClick.parentElement.parentElement.dataset.id;
        let type = 'minus';
        if(positionClick.classList.contains('plus')){
            type = 'plus';
        }
        changeQuantityCart(product_id, type);
    }
})

function handleCheckOut(e){
    e.preventDefault()
    checkout.innerHTML = "checking ...";
    if(cart.length==0)return
    csrftoken = getCookie('csrftoken')
    fetch('/shop/buy', {
        method: "POST",
        headers: {'X-CSRFToken': csrftoken},
        body: JSON.stringify({
            products: cart,
            currency: currency
        })
    })
    .then(
        response=>response.json()
    )
    .then(json=>{
        checkout.innerHTML = "Check Out"
        if(json.success==true){
            window.location.href = json.redirect
        }
    }).catch(err=>{
        checkout.innerHTML = "Check Out"
        alert("error", err)
    })
}

checkout.addEventListener("click", handleCheckOut)
document.getElementById('checkout_button').addEventListener("click", handleCheckOut)

const changeQuantityCart = (product_id, type) => {
    let positionItemInCart = cart.findIndex((value) => value.product_id == product_id);
    if(positionItemInCart >= 0){
        let info = cart[positionItemInCart];
        switch (type) {
            case 'plus':
                cart[positionItemInCart].quantity = cart[positionItemInCart].quantity + 1;
                total_price+=cart[positionItemInCart].price
                break;
        
            default:
                let changeQuantity = cart[positionItemInCart].quantity - 1;
                total_price-=cart[positionItemInCart].price
                if (changeQuantity > 0) {
                    cart[positionItemInCart].quantity = changeQuantity;
                }else{
                    cart.splice(positionItemInCart, 1);
                }
                break;
        }
    }
    addCartToHTML();
    addCartToMemory();
}

const initApp = () => {
    // get data product
    fetch('/shop/products')
    .then(response => response.json())
    .then(data => {
        products = data;
        addDataToHTML();

        // get data cart from memory
        // if(localStorage.getItem('cart')){
        //     cart = JSON.parse(localStorage.getItem('cart'));
        //     cart.map(i=>total_price+=i.price*i.quantity)
        //     addCartToHTML();
        // }
    })
}

document.addEventListener("DOMContentLoaded", function() {
    var dropdown = document.getElementsByClassName("dropdown")[0];
    if (localStorage.getItem('currency')){
        currency = localStorage.getItem('currency')
        dropdown.getElementsByClassName("dropbtn")[0].children[0].textContent = localStorage.getItem('currency');
    }
    var dropdownContent = document.getElementById("myDropdown");
    dropdownContent.addEventListener("click", function(e) {
      if (e.target.tagName === "A") {
        var selectedCurrency = e.target.dataset.currency;
        localStorage.setItem('currency', e.target.dataset.currency)
        currency=e.target.dataset.currency
        dropdown.getElementsByClassName("dropbtn")[0].children[0].textContent = selectedCurrency;
        addDataToHTML()
        addCartToHTML()
      }
    });
  });

initApp();
