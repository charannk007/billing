let cart = [];

window.onload = function () {
    const searchInput = document.getElementById('search');
    const categoryFilter = document.getElementById('category-filter');
    let inputTimeout = null;

    // Barcode or text search input
    searchInput.addEventListener('input', () => {
        clearTimeout(inputTimeout);
        inputTimeout = setTimeout(() => {
            const value = searchInput.value.trim();

            if (value === '') return;

            if (/^\d{6,}$/.test(value)) {
                scanBarcode(value);
            } else {
                searchItems(value);
            }
        }, 300);
    });

    // Filter by category
    categoryFilter.addEventListener('change', () => {
        const selectedCategory = categoryFilter.value;
        filterStocks(selectedCategory);
    });

    // Load all items initially
    filterStocks("All");
};

async function searchItems(query) {
    const response = await fetch('/search_items', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `query=${encodeURIComponent(query)}`
    });

    const data = await response.json();
    const results = document.getElementById('search-results');
    results.innerHTML = '';

    data.items.forEach(item => {
        const div = document.createElement('div');
        div.innerHTML = `
            <p>${item[1]} - ₹${item[2]}
            <button onclick="addToCart('${item[0]}', '${item[1]}', ${item[2]})" 
                class="bg-blue-500 text-white px-2 py-1 rounded ml-2">Add</button></p>`;
        results.appendChild(div);
    });
}

async function filterStocks(category) {
    const response = await fetch('/filter_stocks', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `category=${encodeURIComponent(category)}`
    });

    const data = await response.json();
    const tableBody = document.getElementById('stock-table-body');
    tableBody.innerHTML = '';

    data.stocks.forEach(stock => {
        const row = tableBody.insertRow();

        row.insertCell(0).textContent = stock[1]; // Item Name

        const priceCell = row.insertCell(1);
        priceCell.className = 'text-right p-2';
        priceCell.textContent = `₹${stock[2]}`;

        const quantityCell = row.insertCell(2);
        quantityCell.className = parseInt(stock[3]) < 100 
            ? 'text-red-600 font-semibold text-right p-2' 
            : 'text-right p-2';
        quantityCell.textContent = stock[3];

        const categoryCell = row.insertCell(3);
        categoryCell.className = 'text-left p-2';
        categoryCell.textContent = stock[4];

        const imgCell = row.insertCell(4);
        imgCell.className = 'text-center p-2';
        imgCell.innerHTML = `<img src="/static/${stock[5]}" alt="Barcode" class="h-10 inline-block" loading="lazy">`;
    });
}

async function scanBarcode(barcode) {
    const response = await fetch('/scan_barcode', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `barcode=${encodeURIComponent(barcode)}`
    });

    const data = await response.json();
    if (data.item) {
        addToCart(data.item[0], data.item[1], data.item[2]);
        document.getElementById('search').value = '';
    } else {
        alert('Item not found');
    }
}

function addToCart(id, name, price) {
    const existing = cart.find(item => item.id === id);
    if (existing) {
        existing.quantity++;
    } else {
        cart.push({ id, name, price, quantity: 1 });
    }
    updateCart();
}

function removeFromCart(index) {
    cart.splice(index, 1);
    updateCart();
}

function updateCart() {
    const cartBody = document.getElementById('cart-body');
    cartBody.innerHTML = '';
    let total = 0;

    cart.forEach((item, index) => {
        const subtotal = item.price * item.quantity;
        total += subtotal;

        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="p-2 border">${item.name}</td>
            <td class="p-2 border">₹${item.price}</td>
            <td class="p-2 border">${item.quantity}</td>
            <td class="p-2 border">₹${subtotal.toFixed(2)}</td>
            <td class="p-2 border">
                <button onclick="removeFromCart(${index})" class="bg-red-500 text-white px-2 py-1 rounded">Remove</button>
            </td>`;
        cartBody.appendChild(row);
    });

    document.getElementById('total').value = total.toFixed(2);
    document.getElementById('total-hidden').value = total.toFixed(2);
    updateFormData();
}

function updateFormData() {
    document.getElementById('items').value = cart.map(item => item.id).join(',');
    document.getElementById('quantities').value = cart.map(item => item.quantity).join(',');
}
