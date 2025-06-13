let cart = [];

window.onload = function () {
    const searchInput = document.getElementById('search');
    const categoryFilter = document.getElementById('category-filter');
    let inputTimeout = null;

    if (searchInput) {
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
    }

    if (categoryFilter) {
        categoryFilter.addEventListener('change', () => {
            const selectedCategory = categoryFilter.value;
            filterStocks(selectedCategory);
        });
        filterStocks("All");
    }
};

async function searchItems(query) {
    try {
        const response = await fetch('/search_items', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `query=${encodeURIComponent(query)}`
        });

        if (!response.ok) throw new Error('Network response was not ok');

        const data = await response.json();
        const results = document.getElementById('search-results');
        if (results) {
            results.innerHTML = '';
            data.items.forEach(item => {
                const div = document.createElement('div');
                div.className = 'p-2 border-b';
                div.innerHTML = `
                    <p class="text-center">${item[1]} - ₹${item[2]}
                    <button onclick="addToCart('${item[0]}', '${item[1]}', ${item[2]})" 
                        class="bg-blue-500 text-white px-2 py-1 rounded ml-2">Add</button></p>`;
                results.appendChild(div);
            });
        }
    } catch (error) {
        console.error('Error searching items:', error);
        alert('An error occurred while searching items. Please try again.');
    }
}

async function filterStocks(category) {
    try {
        const response = await fetch('/filter_stocks', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `category_id=${encodeURIComponent(category)}`
        });

        if (!response.ok) throw new Error('Network response was not ok');

        const data = await response.json();
        const tableBody = document.getElementById('stocks-table-body');
        if (tableBody) {
            tableBody.innerHTML = '';
            if (data.stocks.length === 0) {
                const row = tableBody.insertRow();
                const cell = row.insertCell(0);
                cell.colSpan = 5;
                cell.textContent = 'No stocks found for this category.';
                cell.className = 'text-center text-gray-500 p-4';
                return;
            }

            data.stocks.forEach(stock => {
                const row = tableBody.insertRow();
                row.className = 'hover:bg-gray-100 transition';

                const nameCell = row.insertCell(0);
                nameCell.className = 'p-3 text-center';
                nameCell.textContent = stock[1];

                const priceCell = row.insertCell(1);
                priceCell.className = 'p-3 text-center';
                priceCell.textContent = `₹${stock[2]}`;

                const quantityCell = row.insertCell(2);
                quantityCell.className = `p-3 text-center ${parseInt(stock[3]) < 100 ? 'text-red-600 font-semibold' : ''}`;
                quantityCell.textContent = stock[3];

                const categoryCell = row.insertCell(3);
                categoryCell.className = 'p-3 text-center';
                categoryCell.textContent = stock[4];

                const imgCell = row.insertCell(4);
                imgCell.className = 'p-3 text-center';
                imgCell.innerHTML = `<img src="/static/${stock[5]}" alt="Barcode" class="h-10 mx-auto" loading="lazy">`;
            });
        }
    } catch (error) {
        console.error('Error filtering stocks:', error);
        alert('An error occurred while filtering stocks. Please try again.');
    }
}

async function scanBarcode(barcode) {
    try {
        const response = await fetch('/scan_barcode', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `barcode=${encodeURIComponent(barcode)}`
        });

        if (!response.ok) throw new Error('Network response was not ok');

        const data = await response.json();
        if (data.item) {
            addToCart(data.item[0], data.item[1], data.item[2]);
            document.getElementById('search').value = '';
        } else {
            alert('Item not found');
        }
    } catch (error) {
        console.error('Error scanning barcode:', error);
        alert('An error occurred while scanning barcode. Please try again.');
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
    if (cartBody) {
        cartBody.innerHTML = '';
        let total = 0;

        cart.forEach((item, index) => {
            const subtotal = item.price * item.quantity;
            total += subtotal;

            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="p-2 border text-center">${item.name}</td>
                <td class="p-2 border text-center">₹${item.price}</td>
                <td class="p-2 border text-center">${item.quantity}</td>
                <td class="p-2 border text-center">₹${subtotal.toFixed(2)}</td>
                <td class="p-2 border text-center">
                    <button onclick="removeFromCart(${index})" class="bg-red-500 text-white px-2 py-1 rounded">Remove</button>
                </td>`;
            cartBody.appendChild(row);
        });

        const totalElement = document.getElementById('total');
        const totalHidden = document.getElementById('total-hidden');
        if (totalElement) totalElement.value = total.toFixed(2);
        if (totalHidden) totalHidden.value = total.toFixed(2);
        updateFormData();
    }
}

function updateFormData() {
    const itemsInput = document.getElementById('items');
    const quantitiesInput = document.getElementById('quantities');
    if (itemsInput) itemsInput.value = cart.map(item => item.id).join(',');
    if (quantitiesInput) quantitiesInput.value = cart.map(item => item.quantity).join(',');
}
