const money = new Intl.NumberFormat("en-UG", {
    style: "currency",
    currency: "UGX",
    maximumFractionDigits: 0
});

const today = () => new Date().toISOString().slice(0, 10);

const defaults = {
    members: [
        { no: "PPSW-1184", name: "Amina Kato", idNo: "CM87012459", phone: "+256 772 118 400", branch: "Parliament Branch", status: "Active", address: "Parliament duty station" },
        { no: "PPSW-0927", name: "Daniel Okello", idNo: "CM79011845", phone: "+256 701 927 009", branch: "Parliament Branch", status: "Active", address: "Parliament duty station" },
        { no: "PPSW-1032", name: "Sarah Namuli", idNo: "CM81055832", phone: "+256 775 103 200", branch: "Central Branch", status: "Active", address: "Central office" },
        { no: "PPSW-1108", name: "Moses Lutaaya", idNo: "CM76033781", phone: "+256 706 110 800", branch: "Central Branch", status: "Suspended", address: "Central office" },
        { no: "PPSW-1211", name: "Grace Akello", idNo: "CM82011988", phone: "+256 779 121 100", branch: "Parliament Branch", status: "Active", address: "Parliament duty station" }
    ],
    accounts: [
        { no: "ACC-000184", memberNo: "PPSW-1184", member: "Amina Kato", product: "Ordinary Savings", opened: "2024-02-14", balance: 18450000, status: "Active" },
        { no: "ACC-000927", memberNo: "PPSW-0927", member: "Daniel Okello", product: "Welfare Fund", opened: "2023-09-01", balance: 3250000, status: "Active" },
        { no: "ACC-001032", memberNo: "PPSW-1032", member: "Sarah Namuli", product: "Share Capital", opened: "2024-05-21", balance: 6400000, status: "Active" },
        { no: "ACC-001108", memberNo: "PPSW-1108", member: "Moses Lutaaya", product: "Ordinary Savings", opened: "2023-11-12", balance: 830000, status: "Dormant" },
        { no: "ACC-001211", memberNo: "PPSW-1211", member: "Grace Akello", product: "Welfare Fund", opened: "2025-01-17", balance: 2120000, status: "Active" }
    ],
    loans: [
        { no: "LN-00281", memberNo: "PPSW-1184", member: "Amina Kato", type: "Normal Loan", amount: 5000000, outstanding: 3875000, status: "Running", rate: 12, months: 24, guarantor: "Sarah Namuli" },
        { no: "LN-00282", memberNo: "PPSW-0927", member: "Daniel Okello", type: "Emergency Loan", amount: 1200000, outstanding: 0, status: "Cleared", rate: 10, months: 6, guarantor: "Amina Kato" },
        { no: "LN-00283", memberNo: "PPSW-1032", member: "Sarah Namuli", type: "School Fees Loan", amount: 3500000, outstanding: 2950000, status: "Approved", rate: 12, months: 12, guarantor: "Grace Akello" },
        { no: "LN-00284", memberNo: "PPSW-1211", member: "Grace Akello", type: "Normal Loan", amount: 8000000, outstanding: 7400000, status: "Running", rate: 12, months: 24, guarantor: "Amina Kato" },
        { no: "LN-00285", memberNo: "PPSW-1108", member: "Moses Lutaaya", type: "Emergency Loan", amount: 900000, outstanding: 620000, status: "Defaulted", rate: 10, months: 6, guarantor: "Daniel Okello" }
    ],
    transactions: [
        { date: "2026-06-03", account: "ACC-000184", member: "Amina Kato", type: "Deposit", method: "Payroll Deduction", amount: 250000, balanceAfter: 18450000, postedBy: "Teller N. Mugisha", narration: "Monthly contribution" },
        { date: "2026-06-03", account: "ACC-000927", member: "Daniel Okello", type: "Loan Repayment", method: "Cash", amount: 180000, balanceAfter: 3250000, postedBy: "Teller N. Mugisha", narration: "Installment payment" },
        { date: "2026-06-02", account: "ACC-001032", member: "Sarah Namuli", type: "Deposit", method: "Mobile Money", amount: 120000, balanceAfter: 6400000, postedBy: "Teller P. Kisembo", narration: "Share capital" },
        { date: "2026-06-02", account: "ACC-001211", member: "Grace Akello", type: "Withdrawal", method: "Bank Transfer", amount: 400000, balanceAfter: 2120000, postedBy: "Accountant J. Naki", narration: "Approved withdrawal" },
        { date: "2026-06-01", account: "ACC-001108", member: "Moses Lutaaya", type: "Charge", method: "Cash", amount: 15000, balanceAfter: 830000, postedBy: "Teller P. Kisembo", narration: "Service charge" }
    ]
};

let state = loadState();

const products = [
    ["Ordinary Savings", "Savings", "Active"],
    ["Welfare Fund", "Savings", "Active"],
    ["Share Capital", "Savings", "Active"],
    ["Normal Loan Product", "Loan", "Active"],
    ["Emergency Loan Product", "Loan", "Active"]
];

const roles = [
    ["Administrator", "System settings, users, roles, products"],
    ["Manager", "Loan approvals and supervisory reports"],
    ["Loans Officer", "Applications, guarantors, loan monitoring"],
    ["Teller", "Deposits, withdrawals, repayments"],
    ["Accountant", "Reconciliation and financial reports"],
    ["Auditor", "Read-only audit and compliance review"]
];

const reports = [
    ["Member Register", "Members by branch, status, and joining period."],
    ["Savings Statement", "Account transaction history for a selected member."],
    ["Daily Teller Collections", "Cash, mobile money, bank, and payroll totals by teller."],
    ["Loan Portfolio", "Approved, running, cleared, and defaulted loan balances."],
    ["Loan Arrears", "Overdue loans with days late and outstanding balance."],
    ["Branch Performance", "Membership, savings, welfare, share capital, and loans by branch."],
    ["Repayment Report", "Installments received with principal and interest split."],
    ["Audit Report", "Sensitive actions by user, date, branch, and module."],
    ["Welfare Contributions", "Member welfare fund activity and balances."]
];

function loadState() {
    const saved = localStorage.getItem("ppsw-sacco-state");
    return saved ? JSON.parse(saved) : structuredClone(defaults);
}

function saveState() {
    localStorage.setItem("ppsw-sacco-state", JSON.stringify(state));
}

function statusPill(status) {
    const tone = {
        Active: "green",
        Running: "blue",
        Approved: "blue",
        Applied: "amber",
        Cleared: "green",
        Dormant: "amber",
        Suspended: "amber",
        Defaulted: "red",
        Rejected: "red"
    }[status] || "blue";
    return `<span class="pill ${tone}">${status}</span>`;
}

function toast(message) {
    const box = document.getElementById("toast");
    box.textContent = message;
    box.classList.add("show");
    window.clearTimeout(toast.timer);
    toast.timer = window.setTimeout(() => box.classList.remove("show"), 2600);
}

function showModal(title, html) {
    document.getElementById("modal-title").textContent = title;
    document.getElementById("modal-body").innerHTML = html;
    document.getElementById("modal").classList.add("show");
    document.getElementById("modal").setAttribute("aria-hidden", "false");
}

function closeModal() {
    document.getElementById("modal").classList.remove("show");
    document.getElementById("modal").setAttribute("aria-hidden", "true");
}

function fillTable(id, rows, formatter) {
    document.getElementById(id).innerHTML = rows.map((row, index) => formatter(row, index)).join("");
}

function nextCode(prefix, collection, key) {
    const nums = collection.map(item => Number(String(item[key]).replace(/\D/g, ""))).filter(Boolean);
    return `${prefix}-${String((Math.max(...nums) || 0) + 1).padStart(prefix === "LN" ? 5 : 6, "0")}`;
}

function renderDashboard() {
    const activeMembers = state.members.filter(item => item.status === "Active").length;
    const savings = state.accounts.reduce((sum, item) => sum + item.balance, 0);
    const activeLoans = state.loans.filter(item => ["Running", "Approved", "Applied", "Defaulted"].includes(item.status));
    const loanPortfolio = activeLoans.reduce((sum, item) => sum + item.outstanding, 0);
    const arrears = state.loans.filter(item => item.status === "Defaulted").reduce((sum, item) => sum + item.outstanding, 0);
    const metrics = document.querySelectorAll(".dashboard-metrics .metric");

    metrics[0].querySelector("strong").textContent = String(activeMembers);
    metrics[0].querySelector("small").textContent = `${state.members.length} total registered`;
    metrics[1].querySelector("strong").textContent = money.format(savings);
    metrics[2].querySelector("strong").textContent = money.format(loanPortfolio);
    metrics[2].querySelector("small").textContent = `${activeLoans.length} active loan records`;
    metrics[3].querySelector("strong").textContent = money.format(arrears);
    metrics[3].querySelector("small").textContent = `${state.loans.filter(item => item.status === "Defaulted").length} accounts flagged`;

    renderCollectionsChart();
    renderPortfolioMix();
    renderArrearsAging();
    renderBranchPerformance();
}

function renderCollectionsChart() {
    const trend = [
        ["Jan", 318, 156],
        ["Feb", 352, 168],
        ["Mar", 336, 182],
        ["Apr", 391, 204],
        ["May", 428, 224],
        ["Jun", Math.round(state.transactions.filter(item => item.type === "Deposit").reduce((sum, item) => sum + item.amount, 0) / 1000000), Math.round(state.transactions.filter(item => item.type === "Loan Repayment").reduce((sum, item) => sum + item.amount, 0) / 1000000)]
    ];
    const maxValue = Math.max(...trend.flatMap(row => [row[1], row[2], 1]));
    document.getElementById("collections-chart").innerHTML = trend.map(row => `
        <div class="bar-group">
            <div class="bar-pair" title="${row[0]}: savings ${row[1]}M, repayments ${row[2]}M">
                <div class="bar savings" style="height: ${Math.round((row[1] / maxValue) * 160)}px"></div>
                <div class="bar repayments" style="height: ${Math.round((row[2] / maxValue) * 160)}px"></div>
            </div>
            <div class="bar-label">${row[0]}</div>
        </div>
    `).join("");
}

function renderPortfolioMix() {
    const savings = state.accounts.filter(item => item.product === "Ordinary Savings").reduce((sum, item) => sum + item.balance, 0);
    const welfare = state.accounts.filter(item => item.product === "Welfare Fund").reduce((sum, item) => sum + item.balance, 0);
    const shares = state.accounts.filter(item => item.product === "Share Capital").reduce((sum, item) => sum + item.balance, 0);
    const loan = state.loans.reduce((sum, item) => sum + item.outstanding, 0);
    const rows = [
        ["Ordinary Savings", savings, "#1abb9c"],
        ["Loan Portfolio", loan, "#3498db"],
        ["Welfare Fund", welfare, "#f0ad4e"],
        ["Share Capital", shares, "#7d5fb2"]
    ];
    const total = rows.reduce((sum, row) => sum + row[1], 0) || 1;
    let cursor = 0;
    const segments = rows.map(row => {
        const start = cursor;
        const end = cursor + (row[1] / total) * 100;
        cursor = end;
        return `${row[2]} ${start}% ${end}%`;
    });

    document.getElementById("portfolio-donut").style.background = `conic-gradient(${segments.join(", ")})`;
    document.querySelector("#portfolio-donut span").innerHTML = `${money.format(total).replace("UGX", "UGX<br>")}`;
    document.getElementById("portfolio-legend").innerHTML = rows.map(row => `
        <div class="legend-item">
            <span class="legend-dot" style="background: ${row[2]}"></span>
            <span>${row[0]}</span>
            <strong>${Math.round((row[1] / total) * 100)}%</strong>
        </div>
    `).join("");
}

function renderArrearsAging() {
    const defaulted = state.loans.filter(item => item.status === "Defaulted").reduce((sum, item) => sum + item.outstanding, 0);
    const rows = [
        ["1-30 days", 18, Math.round(defaulted * 0.17)],
        ["31-60 days", 31, Math.round(defaulted * 0.31)],
        ["61-90 days", 24, Math.round(defaulted * 0.24)],
        ["Over 90 days", 27, Math.round(defaulted * 0.28)]
    ];
    document.getElementById("arrears-bars").innerHTML = rows.map(row => `
        <div class="risk-row">
            <div class="risk-meta"><span>${row[0]}</span><strong>${money.format(row[2])}</strong></div>
            <div class="risk-track"><div class="risk-fill ${row[1] >= 27 ? "high" : ""}" style="width: ${row[1]}%"></div></div>
        </div>
    `).join("");
}

function renderBranchPerformance() {
    const branches = [...new Set(state.members.map(member => member.branch))];
    document.getElementById("branch-score").innerHTML = branches.map(branch => {
        const members = state.members.filter(item => item.branch === branch);
        const memberNos = members.map(item => item.no);
        const collected = state.accounts.filter(item => memberNos.includes(item.memberNo)).reduce((sum, item) => sum + item.balance, 0);
        const score = Math.min(96, 45 + members.length * 8);
        return `
            <div class="branch-card">
                <strong>${branch}</strong>
                <div class="score-line"><div class="score-fill" style="width: ${score}%"></div></div>
                <div class="branch-meta"><span>${members.length} members</span><span>${money.format(collected)} collected</span></div>
            </div>
        `;
    }).join("");
}

function renderTables() {
    fillTable("member-rows", state.members, row => `
        <tr><td>${row.no}</td><td>${row.name}</td><td>${row.idNo}</td><td>${row.phone}</td><td>${row.branch}</td><td>${statusPill(row.status)}</td></tr>
    `);
    fillTable("account-rows", state.accounts, row => `
        <tr><td>${row.no}</td><td>${row.member}</td><td>${row.product}</td><td>${row.opened}</td><td>${money.format(row.balance)}</td><td>${statusPill(row.status)}</td></tr>
    `);
    fillTable("loan-rows", state.loans, row => `
        <tr>
            <td>${row.no}</td><td>${row.member}</td><td>${row.type}</td><td>${money.format(row.amount)}</td><td>${money.format(row.outstanding)}</td>
            <td>${statusPill(row.status)} ${loanActions(row)}</td>
        </tr>
    `);
    fillTable("recent-transactions", state.transactions.slice(0, 8), row => `
        <tr><td>${row.date}</td><td>${row.member}</td><td>${row.type}</td><td>${row.method}</td><td>${money.format(row.amount)}</td><td>${row.postedBy}</td></tr>
    `);
    fillTable("ledger-rows", state.transactions, row => `
        <tr><td>${row.date}</td><td>${row.account}</td><td>${row.type}</td><td>${row.method}</td><td>${money.format(row.amount)}</td><td>${money.format(row.balanceAfter)}</td></tr>
    `);
    renderLoanQueue();
}

function loanActions(row) {
    if (row.status !== "Applied") return "";
    return `<button class="mini-button" data-approve="${row.no}">Approve</button><button class="mini-button danger" data-reject="${row.no}">Reject</button>`;
}

function renderLoanQueue() {
    const active = state.loans.filter(row => row.status !== "Cleared").slice(0, 6);
    document.getElementById("loan-queue").innerHTML = active.map(row => `
        <div class="list-item">
            <strong>${row.no} - ${row.member}</strong>
            <span>${row.type} | Outstanding ${money.format(row.outstanding)} | ${row.status}</span>
        </div>
    `).join("");
    document.querySelector("#loan-queue").previousElementSibling.querySelector(".pill").textContent = `${state.loans.filter(row => row.status === "Applied").length} pending`;
}

function renderSelects() {
    const memberOptions = state.members.filter(item => item.status === "Active").map(item => `<option value="${item.no}">${item.no} - ${item.name}</option>`).join("");
    document.getElementById("loan-member").innerHTML = memberOptions;
    document.getElementById("loan-guarantor").innerHTML = memberOptions;
    document.getElementById("transaction-account").innerHTML = state.accounts.map(item => `<option value="${item.no}">${item.no} - ${item.member} (${money.format(item.balance)})</option>`).join("");
}

function renderReportsAndSettings() {
    document.getElementById("report-cards").innerHTML = reports.map(row => `
        <article class="report-card">
            <strong>${row[0]}</strong>
            <span>${row[1]}</span>
            <button class="ghost-button" data-report="${row[0]}">Open</button>
        </article>
    `).join("");
    document.getElementById("product-list").innerHTML = products.map(row => `<div class="list-item"><strong>${row[0]}</strong><span>${row[1]} | ${row[2]}</span></div>`).join("");
    document.getElementById("role-list").innerHTML = roles.map(row => `<div class="list-item"><strong>${row[0]}</strong><span>${row[1]}</span></div>`).join("");
}

function renderAll() {
    renderDashboard();
    renderTables();
    renderSelects();
    renderReportsAndSettings();
    document.getElementById("member-no").value = nextCode("PPSW", state.members, "no");
}

function switchView(view) {
    document.querySelectorAll(".nav-item").forEach(item => item.classList.toggle("active", item.dataset.view === view));
    document.querySelectorAll(".view").forEach(section => section.classList.toggle("active-view", section.id === view));
    const active = document.querySelector(`.nav-item[data-view="${view}"] span`);
    document.getElementById("page-title").textContent = active ? active.textContent : "Dashboard";
}

function addMember(event) {
    event.preventDefault();
    const no = document.getElementById("member-no").value.trim();
    const first = document.getElementById("member-first-name").value.trim();
    const last = document.getElementById("member-last-name").value.trim();
    const idNo = document.getElementById("member-id-no").value.trim();
    const phone = document.getElementById("member-phone").value.trim();
    const branch = document.getElementById("member-branch").value;
    const address = document.getElementById("member-address").value.trim();

    if (!first || !last || !idNo || !phone) {
        toast("Please complete the required member fields.");
        return;
    }
    if (state.members.some(item => item.no === no || item.idNo === idNo)) {
        toast("Member number or ID number already exists.");
        return;
    }

    const member = { no, name: `${first} ${last}`, idNo, phone, branch, status: "Active", address };
    state.members.unshift(member);
    state.accounts.unshift({
        no: nextCode("ACC", state.accounts, "no"),
        memberNo: no,
        member: member.name,
        product: "Ordinary Savings",
        opened: today(),
        balance: 0,
        status: "Active"
    });
    saveState();
    event.target.reset();
    renderAll();
    toast("Member saved and default savings account opened.");
}

function postTransaction(event) {
    event.preventDefault();
    const accountNo = document.getElementById("transaction-account").value;
    const type = document.getElementById("transaction-type").value;
    const method = document.getElementById("transaction-method").value;
    const amount = Number(document.getElementById("transaction-amount").value);
    const narration = document.getElementById("transaction-narration").value.trim();
    const account = state.accounts.find(item => item.no === accountNo);

    if (!account || !amount || amount <= 0) {
        toast("Choose an account and enter a valid amount.");
        return;
    }

    const sign = ["Withdrawal", "Charge"].includes(type) ? -1 : 1;
    const newBalance = account.balance + sign * amount;
    if (newBalance < 0) {
        toast("Transaction blocked: account balance cannot go below zero.");
        return;
    }

    account.balance = newBalance;
    state.transactions.unshift({
        date: today(),
        account: account.no,
        member: account.member,
        type,
        method,
        amount,
        balanceAfter: newBalance,
        postedBy: "SACCO Manager",
        narration
    });

    if (type === "Loan Repayment") {
        const loan = state.loans.find(item => item.memberNo === account.memberNo && item.outstanding > 0);
        if (loan) {
            loan.outstanding = Math.max(0, loan.outstanding - amount);
            loan.status = loan.outstanding === 0 ? "Cleared" : "Running";
        }
    }

    saveState();
    renderAll();
    toast("Transaction posted and balances updated.");
}

function submitLoan(event) {
    event.preventDefault();
    const memberNo = document.getElementById("loan-member").value;
    const member = state.members.find(item => item.no === memberNo);
    const guarantor = state.members.find(item => item.no === document.getElementById("loan-guarantor").value);
    const amount = Number(document.getElementById("loan-amount").value);
    const rate = Number(document.getElementById("loan-interest").value);
    const months = Number(document.getElementById("loan-months").value);

    if (!member || !guarantor || !amount || amount <= 0 || !months || months <= 0) {
        toast("Please complete the loan application correctly.");
        return;
    }
    if (member.no === guarantor.no) {
        toast("A member cannot guarantee their own loan.");
        return;
    }

    state.loans.unshift({
        no: nextCode("LN", state.loans, "no"),
        memberNo,
        member: member.name,
        type: document.getElementById("loan-type").value,
        amount,
        outstanding: amount,
        status: "Applied",
        rate,
        months,
        guarantor: guarantor.name
    });
    saveState();
    renderAll();
    toast("Loan application submitted for approval.");
}

function approveLoan(no, status) {
    const loan = state.loans.find(item => item.no === no);
    if (!loan) return;
    loan.status = status;
    if (status === "Approved") {
        state.transactions.unshift({
            date: today(),
            account: "Loan Control",
            member: loan.member,
            type: "Loan Approval",
            method: "Internal",
            amount: loan.amount,
            balanceAfter: loan.outstanding,
            postedBy: "SACCO Manager",
            narration: `${loan.type} approved`
        });
    }
    saveState();
    renderAll();
    toast(`Loan ${no} marked as ${status}.`);
}

function openReport(name) {
    const html = {
        "Member Register": `<p>${state.members.length} members registered.</p>${simpleTable(["No", "Name", "Branch", "Status"], state.members.map(item => [item.no, item.name, item.branch, item.status]))}`,
        "Savings Statement": simpleTable(["Account", "Member", "Product", "Balance"], state.accounts.map(item => [item.no, item.member, item.product, money.format(item.balance)])),
        "Loan Portfolio": simpleTable(["Loan", "Member", "Type", "Outstanding", "Status"], state.loans.map(item => [item.no, item.member, item.type, money.format(item.outstanding), item.status])),
        "Loan Arrears": simpleTable(["Loan", "Member", "Outstanding"], state.loans.filter(item => item.status === "Defaulted").map(item => [item.no, item.member, money.format(item.outstanding)])),
        "Repayment Report": simpleTable(["Date", "Member", "Amount", "Method"], state.transactions.filter(item => item.type === "Loan Repayment").map(item => [item.date, item.member, money.format(item.amount), item.method]))
    }[name] || `<p>${name} is ready for filtering and export in the full backend implementation.</p>`;
    showModal(name, html);
}

function simpleTable(headers, rows) {
    return `<div class="table-wrap"><table><thead><tr>${headers.map(item => `<th>${item}</th>`).join("")}</tr></thead><tbody>${rows.map(row => `<tr>${row.map(cell => `<td>${cell}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
}

document.querySelectorAll(".nav-item").forEach(button => {
    button.addEventListener("click", () => switchView(button.dataset.view));
});

document.getElementById("member-form").addEventListener("submit", addMember);
document.getElementById("transaction-form").addEventListener("submit", postTransaction);
document.getElementById("loan-form").addEventListener("submit", submitLoan);
document.getElementById("modal-close").addEventListener("click", closeModal);
document.getElementById("modal").addEventListener("click", event => {
    if (event.target.id === "modal") closeModal();
});

document.addEventListener("click", event => {
    if (event.target.matches("[data-approve]")) approveLoan(event.target.dataset.approve, "Approved");
    if (event.target.matches("[data-reject]")) approveLoan(event.target.dataset.reject, "Rejected");
    if (event.target.matches("[data-report]")) openReport(event.target.dataset.report);
    if (event.target.matches(".segmented")) {
        event.target.parentElement.querySelectorAll(".segmented").forEach(item => item.classList.remove("active"));
        event.target.classList.add("active");
        toast(`Dashboard filter set to ${event.target.textContent}.`);
    }
});

document.querySelector(".icon-button[title='Print current view']").addEventListener("click", () => window.print());
document.querySelector(".icon-button[title='Notifications']").addEventListener("click", () => {
    showModal("Notifications", `
        <div class="stack-list">
            <div class="list-item"><strong>${state.loans.filter(item => item.status === "Applied").length} loans awaiting approval</strong><span>Review the loan queue from the Loans screen.</span></div>
            <div class="list-item"><strong>${state.loans.filter(item => item.status === "Defaulted").length} defaulted loans</strong><span>Use Loan Arrears report for follow-up.</span></div>
        </div>
    `);
});

document.getElementById("global-search").addEventListener("input", event => {
    const term = event.target.value.trim().toLowerCase();
    document.querySelectorAll("tbody tr").forEach(row => {
        row.style.display = row.textContent.toLowerCase().includes(term) ? "" : "none";
    });
});

document.getElementById("new-record").addEventListener("click", () => {
    const active = document.querySelector(".nav-item.active").dataset.view;
    const target = active === "dashboard" ? "members" : active;
    switchView(target);
    toast("Ready for a new record.");
});

renderAll();
