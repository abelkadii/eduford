function openDiv() {
    document.getElementById('productSection').classList.remove('hide_section');
    document.getElementById('product_overlay').classList.remove('hide');
}

let form = document.getElementById('search_form')
let search = document.getElementById('search')
search.addEventListener('input', e=>{
    make_search()
})

function updateQueryStringParameter(uri, key, value) {
    var re = new RegExp("([?&])" + key + "=.*?(&|$)", "i");
    var separator = uri.indexOf('?') !== -1 ? "&" : "?";
    if (uri.match(re)) {
        return uri.replace(re, '$1' + key + "=" + value + '$2');
    }
    else {
        return uri + separator + key + "=" + value;
    }
}

function make_search(){
    // if(search.value=='')return
    // const csrftoken = getCookie('csrftoken');
    var newUrl = updateQueryStringParameter(window.location.href, 'query', search.value);
    history.pushState(null, '', newUrl);
    fetch(`/pc/search?query=${search.value}`)
    .then(res=>res.text())
    .then(html=>{
        document.getElementById('pc_container_products').innerHTML=html
        add_listeners()
    })
}
form.addEventListener('submit', e=>{
    e.preventDefault()
    make_search()
})


function closeDiv() {
    let contentSection = document.getElementById('productSectionContent')
    contentSection.innerHTML=""
    document.getElementById('productSection').classList.add('hide_section');
    document.getElementById('product_overlay').classList.add('hide');
}

function add_listeners(){
    let items = document.getElementsByClassName('pc_container_products_wrapper_item')
    let contentSection = document.getElementById('productSectionContent')
    Array.from(items).map(item=>{
        item.addEventListener('click', e=>{
            contentSection.innerHTML = "spinner"
            openDiv()
            fetch(item.getAttribute('data-href'))
                .then(response => {
                    if (!response.ok) {
                    throw new Error('Network response was not ok');
                    }
                    return response.text(); // Parse response as text
                })
                .then(html => {
                    contentSection.innerHTML = html; // Append HTML to div
                })
                .catch(error => {
                    console.error('There was a problem with your fetch operation:', error);
                });
        })
    })
}

window.onload = ()=>{
    add_listeners()
}