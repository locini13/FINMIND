import { db } from './firebase_init.js';
import { collection, addDoc, getDocs, deleteDoc, onSnapshot, query, orderBy, serverTimestamp } from "https://www.gstatic.com/firebasejs/9.6.1/firebase-firestore.js";

// DOM Elements
const chatWindow = document.getElementById('chat-window');
const inputField = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const balanceEl = document.getElementById('balance-display');
const incomeEl = document.getElementById('income-display');
const expenseEl = document.getElementById('expense-display');
const txList = document.getElementById('transaction-list');

let globalTransactions = []; 
let chartInstance = null;
let totalIncome = 0;
let totalExpense = 0;
let categoryTotals = {};

// Handle Chat Input
async function handleSendMessage() {
    const text = inputField.value.trim();
    if (!text) return;

    addMessageToUI(text, 'user');
    inputField.value = '';

    try {
        // 1. Send to Python API
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });
        const aiData = await response.json();

        if (aiData.status !== 'success') throw new Error("AI Failed");

        // 2. Handle Intents
        switch (aiData.intent) {
            case 'reset':
                await performReset();
                break;

            case 'query':
                handleQuery(aiData.query_type);
                break;

            case 'budget_goal':
                // Fix 2: Don't log as transaction, just acknowledge
                let budgetMsg = `🎯 I've noted your goal to <b>${aiData.original_text}</b>.`;
                if(aiData.amount > 0) {
                    budgetMsg += `<br>I'll help you track your budget for <b>${aiData.category}</b> (₹${aiData.amount}).`;
                }
                addMessageToUI(budgetMsg, 'bot');
                break;

            case 'transaction':
                if(aiData.amount > 0) {
                    // Fix 1 & 3: Save correctly classified transaction
                    await addDoc(collection(db, "transactions"), {
                        original_text: aiData.original_text,
                        amount: aiData.amount,
                        type: aiData.type,
                        category: aiData.category,
                        timestamp: serverTimestamp()
                    });
                    
                    let reply = `✅ Logged: <span class="${aiData.type === 'Income' ? 'green' : 'red'}">${aiData.type}</span> of ₹${aiData.amount.toLocaleString()} for <b>${aiData.category}</b>.`;
                    
                    // Simple Alert Logic
                    if(aiData.type === 'Expense' && aiData.amount > 5000) {
                        reply += `<br>⚠️ <i>That's a high expense! Watch your budget.</i>`;
                    }
                    addMessageToUI(reply, 'bot');
                } else {
                    addMessageToUI("I couldn't read the amount. Please try format: 'Spent 500 on food'", 'bot');
                }
                break;

            default:
                addMessageToUI("I'm listening, but I didn't catch that.", 'bot');
        }

    } catch (error) {
        console.error("Error:", error);
        addMessageToUI("Sorry, brain freeze (Server Error).", 'bot');
    }
}

// Reset Logic
async function performReset() {
    addMessageToUI("🗑️ Clearing all financial data...", 'bot');
    const q = query(collection(db, "transactions"));
    const snapshot = await getDocs(q);
    const deletePromises = snapshot.docs.map(doc => deleteDoc(doc.ref));
    await Promise.all(deletePromises);
    addMessageToUI("✅ Reset Complete. Start fresh!", 'bot');
}

// Query Logic (Fix 4)
function handleQuery(type) {
    let reply = "";
    const balance = totalIncome - totalExpense;

    if (type === 'balance') {
        reply = `💰 <b>Balance:</b> ₹${balance.toLocaleString()}<br>` + 
                `🔼 Income: ₹${totalIncome.toLocaleString()}<br>` +
                `🔽 Expense: ₹${totalExpense.toLocaleString()}`;
    } 
    else if (type === 'highest_expense') {
        let maxCat = "None";
        let maxVal = 0;
        for(const [cat, val] of Object.entries(categoryTotals)) {
            if(val > maxVal) { maxVal = val; maxCat = cat; }
        }
        reply = `💸 <b>Highest Spending:</b> ${maxCat} (₹${maxVal.toLocaleString()})`;
    }
    else if (type === 'report') {
        reply = `📊 <b>Category Breakdown:</b><br>`;
        if(Object.keys(categoryTotals).length === 0) reply += "No expenses yet.";
        for(const [cat, val] of Object.entries(categoryTotals)) {
            reply += `• ${cat}: ₹${val.toLocaleString()}<br>`;
        }
    } 
    else {
        reply = "Here is your summary: Balance is ₹" + balance.toLocaleString();
    }

    addMessageToUI(reply, 'bot');
}

// UI Helpers
function addMessageToUI(html, sender) {
    const div = document.createElement('div');
    div.classList.add('message', sender);
    const now = new Date();
    div.innerHTML = `
        <div class="msg-content">${html}</div>
        <div class="msg-time">${now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
    `;
    chatWindow.appendChild(div);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

// Real-time Listener
const q = query(collection(db, "transactions"), orderBy("timestamp", "desc"));

onSnapshot(q, (snapshot) => {
    totalIncome = 0;
    totalExpense = 0;
    categoryTotals = {};
    txList.innerHTML = ''; 

    if (snapshot.empty) {
        txList.innerHTML = '<li class="empty-state" style="padding:15px;text-align:center;color:#aaa">No transactions yet.</li>';
    }

    snapshot.docs.forEach(doc => {
        const data = doc.data();
        
        if (data.type === 'Income') {
            totalIncome += data.amount;
        } else {
            totalExpense += data.amount;
            categoryTotals[data.category] = (categoryTotals[data.category] || 0) + data.amount;
        }

        const li = document.createElement('li');
        li.className = 'ledger-item';
        li.innerHTML = `
            <div>
                <span>${data.category}</span>
                <span class="cat-label" style="font-size:0.75rem; color:#aaa; display:block">${data.original_text.substring(0, 20)}...</span>
            </div>
            <span class="${data.type === 'Income' ? 'text-green' : 'text-red'}">
                ${data.type === 'Income' ? '+' : '-'} ₹${data.amount.toLocaleString()}
            </span>
        `;
        txList.appendChild(li);
    });

    incomeEl.innerText = `₹ ${totalIncome.toLocaleString()}`;
    expenseEl.innerText = `₹ ${totalExpense.toLocaleString()}`;
    balanceEl.innerText = `₹ ${(totalIncome - totalExpense).toLocaleString()}`;
    updateChart(categoryTotals);
});

// Chart Logic
function updateChart(dataObj) {
    const ctx = document.getElementById('expenseChart').getContext('2d');
    if (chartInstance) chartInstance.destroy();
    chartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(dataObj),
            datasets: [{
                data: Object.values(dataObj),
                backgroundColor: ['#6c5ce7', '#00b894', '#ff7675', '#fab1a0', '#fdcb6e', '#0984e3'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } }
        }
    });
}

// Listeners
sendBtn.addEventListener('click', handleSendMessage);
inputField.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleSendMessage();
});