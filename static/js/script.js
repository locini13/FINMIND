import { db } from './firebase_init.js';
import { collection, addDoc, onSnapshot, query, orderBy, serverTimestamp } from "https://www.gstatic.com/firebasejs/9.6.1/firebase-firestore.js";

// DOM Elements
const chatWindow = document.getElementById('chat-window');
const inputField = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const balanceEl = document.getElementById('balance-display');
const incomeEl = document.getElementById('income-display');
const expenseEl = document.getElementById('expense-display');
const txList = document.getElementById('transaction-list');

let chartInstance = null;

// 1. Handle Chat Input
async function handleSendMessage() {
    const text = inputField.value.trim();
    if (!text) return;

    addMessageToUI(text, 'user');
    inputField.value = '';

    try {
        const response = await fetch('http://127.0.0.1:5000/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });
        
        const data = await response.json();

        if(data.status === 'success' && data.amount > 0) {
            // Save to Firestore
            await addDoc(collection(db, "transactions"), {
                original_text: data.original_text,
                amount: data.amount,
                type: data.type,
                category: data.category,
                timestamp: serverTimestamp()
            });

            addMessageToUI(`✅ Logged: ₹${data.amount} (${data.category})`, 'bot');
        } else {
            addMessageToUI("I couldn't catch the amount. Try 'Paid 200 for food'.", 'bot');
        }

    } catch (error) {
        console.error("Error:", error);
        addMessageToUI("Error connecting to AI server.", 'bot');
    }
}

function addMessageToUI(text, sender) {
    const div = document.createElement('div');
    div.classList.add('message', sender);
    
    // Get current time HH:MM
    const now = new Date();
    const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    div.innerHTML = `
        <div class="msg-content">${text}</div>
        <div class="msg-time">${timeString}</div>
    `;
    chatWindow.appendChild(div);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

// Event Listeners
sendBtn.addEventListener('click', handleSendMessage);
inputField.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleSendMessage();
});

// 4. Real-time Dashboard Listener
const q = query(collection(db, "transactions"), orderBy("timestamp", "desc"));

onSnapshot(q, (snapshot) => {
    let totalIncome = 0;
    let totalExpense = 0;
    let categories = {};
    
    txList.innerHTML = ''; 

    if (snapshot.empty) {
        txList.innerHTML = '<li class="empty-state" style="padding:20px; color:#aaa; text-align:center;">No transactions found.</li>';
    }

    snapshot.docs.forEach(doc => {
        const data = doc.data();
        
        // Math
        if (data.type === 'Income') {
            totalIncome += data.amount;
        } else {
            totalExpense += data.amount;
            categories[data.category] = (categories[data.category] || 0) + data.amount;
        }

        // UI: List Item
        const li = document.createElement('li');
        li.className = 'ledger-item';
        li.innerHTML = `
            <div>
                <span>${data.category}</span>
                <span class="cat-label">${data.type}</span>
            </div>
            <span class="${data.type === 'Income' ? 'text-green' : 'text-red'}">
                ${data.type === 'Income' ? '+' : '-'} ₹${data.amount.toLocaleString()}
            </span>
        `;
        txList.appendChild(li);
    });

    // UI: Update Numbers
    incomeEl.innerText = `₹ ${totalIncome.toLocaleString()}`;
    expenseEl.innerText = `₹ ${totalExpense.toLocaleString()}`;
    const balance = totalIncome - totalExpense;
    balanceEl.innerText = `₹ ${balance.toLocaleString()}`;

    updateChart(categories);
});

// 5. Chart Logic
function updateChart(categoryData) {
    const ctx = document.getElementById('expenseChart').getContext('2d');
    const labels = Object.keys(categoryData);
    const data = Object.values(categoryData);

    // If no data, show empty chart or hide
    if (data.length === 0) {
        // optional: hide chart
    }

    if (chartInstance) {
        chartInstance.destroy();
    }

    chartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: ['#6c5ce7', '#00b894', '#ff7675', '#fab1a0', '#fdcb6e', '#0984e3'],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false } // Hide default legend to save space
            },
            layout: {
                padding: 10
            }
        }
    });
}